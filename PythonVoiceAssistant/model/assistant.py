import openwakeword
from openwakeword.model import Model
import sounddevice as sd
import numpy as np
import speech_recognition as sr
import pyttsx3
from datetime import datetime
from database.ai_database import DATABASE as db

# Devices
sd.default.device = (2, 4)
sd.default.samplerate = 16000
INPUT_DEVICE_ID = 2
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 80
BLOCK_SIZE = int(SAMPLE_RATE * (FRAME_DURATION_MS / 1000))

# Initialize audio device on import
sd.default.device = (INPUT_DEVICE_ID, 4)
sd.default.samplerate = SAMPLE_RATE

# Load wake word model
openwakeword.utils.download_models()
model = Model(wakeword_models=["alexa"], inference_framework="onnx")

# Text-to-speech
tts = pyttsx3.init()
tts.setProperty('rate', 150)

def speak(text):
    print(f"Assistant: {text}")
    tts.say(text)
    tts.runAndWait()

wake_word_detected = False

# Audio callback for wake word detection
def audio_callback(indata, frames, time, status):
    global wake_word_detected
    audio_frame = indata[:, 0].astype(np.float32).copy()
    audio_frame = np.clip(audio_frame * 10, -1.0, 1.0)
    audio_frame *= 800
    prediction = model.predict(audio_frame)
    alexa_score = prediction.get('alexa', 0.0)
    print(f"Prediction: {{'alexa': {alexa_score:.6f}}}")
    if alexa_score > 0.05:
        wake_word_detected = True

# Start listening for wake word
def start_listening():
    global wake_word_detected
    while True:
        wake_word_detected = False
        print("Listening for wake word...")
        with sd.InputStream(callback=audio_callback,
                            channels=1,
                            samplerate=SAMPLE_RATE,
                            dtype='float32',
                            device=INPUT_DEVICE_ID,
                            blocksize=BLOCK_SIZE):
            while not wake_word_detected:
                sd.sleep(100)
        try:
            # Wake word detected, now stop stream and handle command
            print("Wake word detected!")
            run_voice_command()
        except KeyboardInterrupt:
            print("Stopped by user")

# Handle recognized command
def handle_command(command):
    command = command.lower()
    for keyword, answer in db.items():
        if keyword in command:
            if keyword == "time":
                current_time = datetime.now().strftime("%H:%M")
                speak(answer.format(current_time=current_time))
                return answer.format(current_time=current_time)
            elif keyword in ["exit", "bye"]:
                speak(answer)
                print("exit")
                return answer
            else:
                speak(answer)
                return answer


    speak("I don't know that one.")
    return "I don't know that one."

# Handle recognized command for web interface (without TTS)
def handle_command_web(command):
    command = command.lower()
    for keyword, answer in db.items():
        if keyword in command:
            if keyword == "time":
                current_time = datetime.now().strftime("%H:%M")
                return answer.format(current_time=current_time)
            elif keyword in ["exit", "bye"]:
                return answer
            else:
                return answer
    
    return "I don't know that one."

# Record and recognize command
def run_voice_command():
    r = sr.Recognizer()
    with sr.Microphone(device_index=INPUT_DEVICE_ID) as source:
        speak("I'm listening...")

        # Use a more aggressive ambient noise adjustment
        r.adjust_for_ambient_noise(source, duration=0.5)

        # You can also manually set a different energy threshold if needed
        # r.energy_threshold = 4000

        try:
            # The listen method now gets a "cleaner" signal from adjust_for_ambient_noise
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            command = r.recognize_google(audio)
            print(f"You said: {command}")
            handle_command(command)
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
        except sr.RequestError:
            speak("Speech service error.")
        except sr.WaitTimeoutError:
            speak("Listening timed out.")
        except KeyboardInterrupt:
            print("Stopped by user")

# if __name__ == "__main__":
#     try:
#         start_listening()
#     except KeyboardInterrupt:
#         print("Stopped by user")

def process_command_from_audio(audio_data_bytes, sample_rate=48000):
    # Use microphone directly like the original assistant
    r = sr.Recognizer()
    try:
        with sr.Microphone(device_index=INPUT_DEVICE_ID) as source:
            print("Listening for command...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=3, phrase_time_limit=3)
            command = r.recognize_google(audio)
            print(f"You said: {command}")
            response_text = handle_command_web(command)
            return True, command, response_text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return False, "Sorry, I didn't catch that.", None
    except sr.WaitTimeoutError:
        print("Listening timeout")
        return False, "No command detected", None
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {str(e)}", None

def process_audio_for_wakeword(audio_frame_bytes):
    try:
        # Convert bytes to numpy array
        audio_frame = np.frombuffer(audio_frame_bytes, dtype=np.int16).astype(np.float32)
        
        # Normalize to [-1, 1] range
        audio_frame /= 32768.0
        
        # Simple downsampling - take every nth sample to get approximately 16kHz
        # Assuming input is ~44.1kHz, downsample by factor of ~2.75
        downsample_factor = max(1, len(audio_frame) // BLOCK_SIZE)
        if downsample_factor > 1:
            audio_frame = audio_frame[::downsample_factor]
        
        # Ensure we have exactly BLOCK_SIZE samples
        if len(audio_frame) < BLOCK_SIZE:
            audio_frame = np.pad(audio_frame, (0, BLOCK_SIZE - len(audio_frame)))
        else:
            audio_frame = audio_frame[:BLOCK_SIZE]
        
        # Apply some gain to boost weak signals
        audio_frame = np.clip(audio_frame * 20.0, -1.0, 1.0)
        
        prediction = model.predict(audio_frame)
        alexa_score = prediction.get('alexa', 0.0)
        
        print(f"Prediction: {{'alexa': {alexa_score:.6f}}}")
        return alexa_score
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        return 0.0
