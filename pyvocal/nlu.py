import yaml
import glob
from padatious import IntentContainer

class Nlu:

    _container = IntentContainer('pyvocal_container')
    
    def add_intents(self, language):
        for nlu_file in glob.glob('plugins/**/nlu/'+language+'/*.yaml'):
            with open(nlu_file) as nlu:
                nlu_contents = yaml.load_all(nlu, Loader=yaml.FullLoader)
                for nlu_content in nlu_contents:
                    self._container.add_intent(nlu_content["name"], nlu_content["utterances"])
                    
    def train(self):
        self._container.train()
        
    def calculate(self, sentence):
        return self._container.calc_intent(sentence)