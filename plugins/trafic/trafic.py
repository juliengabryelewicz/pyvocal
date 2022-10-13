from bs4 import BeautifulSoup
import re
import requests
import sys
from pyvocal import plugin
import yaml

class TraficPlugin(plugin.PluginObject):


    url_bouchons="http://tipi.bison-fute.gouv.fr/publication/cnir/RecapBouchonsFranceEntiere.html"

    def get_response(intent, slots):
        default = "Je n'ai malheureusement pas bien compris"
        return getattr(TraficPlugin(), 'case_' + intent, lambda: default)(slots)

    def has_intent(intent):
        intent_list=["listbouchons"]
        return any(elem == intent for elem in intent_list)

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def get_all_bouchons(self,departement):
        text_bouchon = ""
        for bouchon in departement.find_next_siblings():
            if bouchon.name == 'div':
                text_bouchon+=bouchon.text
            elif bouchon.name == 'hr':
                break
        return text_bouchon

    def case_listbouchons(self, slots):
        with open("plugins/trafic/config.yaml") as file:
            config_list = yaml.load(file, Loader=yaml.FullLoader)

        response=""
        html_content = requests.get(self.url_bouchons).content.decode('utf8')
        soup = BeautifulSoup(html_content, "lxml")
        departement_table_data = soup.find_all("span", attrs={"class": "rupture"})
        departement_found=""
        for departement in departement_table_data:
            departement_check = departement.find("a", attrs={"name": str(config_list["departements"]).split(",")})
            if departement_check is not None:
                departement_found+= self.get_all_bouchons(departement)
        if departement_found == "":
            return "aucun bouchon à signaler"
        else:
            return self.cleanhtml(departement_found)
