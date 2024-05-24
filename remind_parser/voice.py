import speech_recognition as sr


def voice_to_text():
    r = sr.Recognizer()
    r.recognize_google()
