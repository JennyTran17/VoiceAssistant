import base64
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from model.assistant import *


app = Flask(__name__)
CORS(app)
# start the wake word detection loop at startup

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listen', methods=['POST'])
def listen():
    """
    Handles audio chunks from the web client for wake word detection.
    """
    try:
        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({'error': 'No audio data found'}), 400

        audio_bytes = base64.b64decode(data['audio'])
        score = process_audio_for_wakeword(audio_bytes)
        predicted_score = float(score)

        # Check if the wake word score exceeds the threshold
        if score > 0.05:
            return jsonify({'wake_word_detected': True, 'score': predicted_score})

        return jsonify({'wake_word_detected': False, 'score': predicted_score})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process_command', methods=['POST'])
def process_command():
    """
    Handles a full command after the wake word has been detected.
    """
    try:
        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({'error': 'No audio data found'}), 400

        audio_bytes = base64.b64decode(data['audio'])
        sample_rate = data.get('sampleRate', 48000)  # Default to 48kHz if not provided
        print(f"Received audio data: {len(audio_bytes)} bytes at {sample_rate}Hz")

        success, command, response_text = process_command_from_audio(audio_bytes, sample_rate)
        print(f"Command processing result: success={success}, command='{command}', response='{response_text}'")

        if success:
            return jsonify({'status': 'success', 'command': command, 'response': response_text})
        else:
            return jsonify({'status': 'failure', 'message': command})

    except Exception as e:
        print(f"Error in process_command: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)