from openwakeword.model import Model
import sounddevice as sd
import numpy as np

model = Model(wakeword_models=["alexa"], inference_framework="onnx")
SAMPLE_RATE = 16000
BLOCK_SIZE = 1280  # 80ms at 16kHz

def callback(indata, frames, time, status):
    audio_frame = indata[:, 0].astype(np.float32).copy()
    audio_frame *= 10
    audio_frame = np.clip(audio_frame * 10, -1.0, 1.0)

    print(f"Audio sample min/max: {audio_frame.min():.6f}/{audio_frame.max():.6f}")

    prediction = model.predict(audio_frame)
    print(f"Prediction: {prediction}")


with sd.InputStream(callback=callback,
                    channels=1,
                    samplerate=SAMPLE_RATE,
                    blocksize=BLOCK_SIZE):
    print("Listening...")
    while True:
        sd.sleep(1000)
