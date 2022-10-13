import pyttsx3

class Tts:

    engine = pyttsx3.init()

    def setVoice(self,voice):
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voice)

    def speak(self,text):
        self.engine.say(text)
        self.engine.runAndWait()