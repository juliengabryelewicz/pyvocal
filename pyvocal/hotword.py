class Hotword:

    state_wake = False

    def __init__(self,word):
        self.word = word

    def getWord(self):
        return self.word

    def getState(self):
        return self.state_wake

    def setState(self,state):
        self.state_wake = state;