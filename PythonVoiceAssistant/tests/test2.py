import speech_recognition as sr

print(dir(sr.Recognizer))  # See all available methods


r = sr.Recognizer()
print("r has recognize_google:", hasattr(r, "recognize_google"))  # Should print True

with sr.Microphone() as source:
    print("Say something...")
    audio = r.listen(source)

try:
    command = r.recognize_google(audio)
    print("You said:", command)
except Exception as e:
    print("Recognition error:", e)
