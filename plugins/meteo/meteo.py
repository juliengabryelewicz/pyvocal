import requests
import sys
from pyvocal import plugin

class MeteoPlugin(plugin.PluginObject):

    meteo_file="plugins/meteo/list_meteo.txt"
    api_key=""

    def get_response(intent, slots):
        default = "Je n'ai malheureusement pas bien compris"
        return getattr(MeteoPlugin(), 'case_' + intent, lambda: default)(slots)

    def has_intent(intent):
        intent_list=["listmeteo"]
        return any(elem == intent for elem in intent_list)

    def get_weather(self, location):
        url = "https://api.openweathermap.org/data/2.5/weather?q={},fr&units=metric&appid={}".format(location, self.api_key)
        r = requests.get(url)
        r_json = r.json()
        return location+" : "+r_json["weather"][0]["description"]+" température : "+str(r_json['main']['temp'])+" degrés"

    def case_listmeteo(self,slots):
        response=""
        with open(self.meteo_file, 'r') as file:
            for line in file:
                response+=self.get_weather(line)
        return "Voici la météo d'aujourd'hui : "+response
