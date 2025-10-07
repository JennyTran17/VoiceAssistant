import sounddevice as sd
import scipy.io.wavfile
print(sd.query_devices())
print("Default Input Device:", sd.default.device[0])

# Replace 3 with your actual mic's device ID
sd.default.device = (2, 4)  # (input_device_index, output_device_index)

# Also optionally set the sample rate
sd.default.samplerate = 16000

fs = 16000  # Sample rate
duration = 5  # seconds

print("Recording...")
recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
sd.wait()
print("Recording done")

scipy.io.wavfile.write('test_mic.wav', fs, recording)