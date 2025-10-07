// static/script.js
const statusBox = document.getElementById('status-box');
const responseBox = document.getElementById('response-box');
const micIcon = document.getElementById('mic-icon');
const pulseRing = document.getElementById('pulse-ring');

let audioContext;
let scriptProcessor;
let mediaStream;
let _awake = false;
let isListeningForCommand = false;
let commandAudioChunks = [];

function getAudio(){
    console.log('Getting audio, _awake:', _awake, 'isListeningForCommand:', isListeningForCommand);
    navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    console.log('Audio stream obtained');
                    mediaStream = stream;
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    console.log('Audio context sample rate:', audioContext.sampleRate);
                    const source = audioContext.createMediaStreamSource(stream);
                    scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);

                    source.connect(scriptProcessor);
                    scriptProcessor.connect(audioContext.destination);

                    scriptProcessor.onaudioprocess = function(event) {
                        const audioData = event.inputBuffer.getChannelData(0);
                        // Send audioData to the server
                        if(!_awake)
                        {
                            sendAudio(audioData);
                        }
                        if(isListeningForCommand)
                        {
                            commandAudioChunks.push(new Float32Array(audioData));
                            if(commandAudioChunks.length % 100 === 0) {
                                console.log('Collected', commandAudioChunks.length, 'audio chunks');
                            }
                        }
                    };
                })
                .catch(err => {
                    console.error('Error accessing microphone:', err);
                    statusBox.textContent = 'Error: Could not access microphone.';
                });
}

// This function will be triggered by a user action, e.g., a button click
function startListening() {
    if(!_awake)
   {
        statusBox.textContent = 'Ready - say "Alexa" to start';
        micIcon.classList.remove('active');
        getAudio()
   }
}

async function sendAudio(audioData) {
    // Apply gain to boost weak signals
    const gainFactor = 3.0;
    const amplifiedData = new Float32Array(audioData.length);
    for (let i = 0; i < audioData.length; i++) {
        amplifiedData[i] = Math.max(-1, Math.min(1, audioData[i] * gainFactor));
    }
    
    // Convert Float32Array to Int16Array
    const int16Array = new Int16Array(amplifiedData.length);
    for (let i = 0; i < amplifiedData.length; i++) {
        const s = amplifiedData[i];
        int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }

    // Convert Int16Array to a base64 string
    const base64Audio = btoa(String.fromCharCode.apply(null, new Uint8Array(int16Array.buffer)));

    // Send as JSON
    fetch('/listen', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ audio: base64Audio }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Server error:', data.error);
            statusBox.textContent = `Error: ${data.error}`;
            return;
        }
        
        // Show current score for debugging
        statusBox.textContent = `Listening for "Alexa"... (${data.score?.toFixed(3) || 'N/A'})`;
        
        if (data.wake_word_detected) {
            console.log('Wake word detected! Starting command mode...');
            _awake = true;
            statusBox.textContent = 'Wake word detected!';
            micIcon.classList.add('active');
            pulseRing.classList.add('active');

            // Start command mode without stopping audio
            startCommandMode();
        }
    })
    .catch(err => console.error('API error:', err));
}

// Start command listening mode
function startCommandMode() {
    console.log('Starting command mode');
    statusBox.textContent = 'Speak now...';
    isListeningForCommand = true;
    commandAudioChunks = [];
    
    // Process command immediately
    console.log('Processing command immediately');
    statusBox.textContent = 'Listening for your command...';
    sendProcessCommand();
}

// Stop listening and send the recorded command
function sendProcessCommand() {
    console.log('sendProcessCommand called');
    isListeningForCommand = false;


    fetch('/process_command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio: '', sampleRate: 48000 }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            statusBox.textContent = 'Ready - say "Alexa" to start';
            responseBox.textContent = `Assistant: ${data.response}`;
        } else {
            statusBox.textContent = 'Ready - say "Alexa" to start';
            responseBox.textContent = `Assistant: ${data.message}`;
        }
        micIcon.classList.remove('active');
        pulseRing.classList.remove('active');
        // Restart the wake word listening loop
        _awake = false;
        stopListening();
        setTimeout(startListening, 1000);
    })
    .catch(err => {
        console.error('API error:', err);
        statusBox.textContent = 'Ready - say "Alexa" to start';
        micIcon.classList.remove('active');
        _awake = false;
        stopListening();
        setTimeout(startListening, 1000);
    });
}

function stopListening() {
    console.log('Stopping audio listening');
    if (scriptProcessor) {
        scriptProcessor.disconnect();
        scriptProcessor = null;
    }
    if (audioContext && audioContext.state !== 'closed') {
        audioContext.close();
        audioContext = null;
    }
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }
}

// Start listening when the page loads (or on a user gesture)
document.addEventListener('DOMContentLoaded', () => {
    // Make the mic icon clickable to start
    micIcon.onclick = startListening;
    statusBox.textContent = 'Click microphone to start';
});