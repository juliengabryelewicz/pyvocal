from __future__ import print_function
import json
import os.path
import os
import pkg_resources
import queue
import sounddevice as sd
import re
import vosk
from .configuration import Configuration
from .hotword import Hotword
from .nlu import Nlu
from .tts import Tts
from .plugin import PluginList

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def main():
    configuration=Configuration("config/config.yaml")

    if not os.path.exists("model/"+configuration.config_list["language"]):
        print("Please download the model from https://github.com/alphacep/vosk-api/blob/master/doc/models.md and unpack as 'model' in the current folder.")
        exit(1)

    ##HOTWORD
    hotword=Hotword(configuration.config_list["hotword"])

    ##TEXT TO SPEECH
    tts = Tts()
    tts.setVoice(configuration.config_list["voice_id"])

    ##VOSK
    model = vosk.Model("model/"+configuration.config_list["language"])
    device_info = sd.query_devices(None, 'input')
    samplerate = int(device_info['default_samplerate'])


    ##PADATIOUS
    nlu = Nlu()
    nlu.add_intents(configuration.config_list["language"])
    nlu.train()

    # Load plugins
    plugin_directories = [
        os.path.normpath('plugins')
    ]

    plugins_list=PluginList(plugin_directories)
    plugins_list.find_plugins()

    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, dtype='int16',channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        rec.SetWords(True)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                rec_result = json.loads(rec.Result())
                print(rec_result["text"])
                if hotword.getState() == True:
                    if rec_result["text"] != "":
                        parsing = nlu.calculate(rec_result["text"])
                        if parsing.conf >= configuration.config_list["min_probability"]:
                            for plugin in plugins_list._plugins:
                                plugin_object = plugins_list._plugins[plugin].plugin_class
                                if plugin_object.has_intent(parsing.name) == True:
                                    response = plugin_object.get_response(parsing.name,parsing.matches)
                                    tts.speak(response)
                                    hotword.setState(False)
                        elif parsing.name == None:
                            hotword.setState(True)
                        else:
                            tts.speak("je ne suis pas sur d'avoir compris, peux-tu répéter?")
                if rec_result["text"].count(hotword.getWord()) > 0:
                    print("je passe")
                    tts.speak(configuration.config_list["sentence_welcome"])
                    hotword.setState(True)