import os
from pyvocal import plugin

class BirthdayPlugin(plugin.PluginObject):

    birthday_file="plugins/birthday/list_birthday.txt"

    def get_response(intent, slots):
        default = "Je n'ai malheureusement pas bien compris"
        return getattr(BirthdayPlugin(), 'case_' + intent, lambda: default)(slots)

    def has_intent(intent):
        intent_list=["addbirthday","removebirthday","listbirthday"]
        return any(elem == intent for elem in intent_list)

    def delete_birthday_by_person(self, original_file, condition):
        bak_file = original_file + '.bak'
        is_skipped = False
        with open(original_file, 'r') as read_file, open(bak_file, 'w') as write_file:
            for line in read_file:
                if condition(line) == False:
                    write_file.write(line)
                else:
                    is_skipped = True
        if is_skipped:
            os.remove(original_file)
            os.rename(bak_file, original_file)
        else:
            os.remove(bak_file)

    def case_removebirthday(self,slots):
        self.delete_birthday_by_person(self.birthday_file, lambda x : slots["person"] in x )
        return slots["person"]+" a bien été retiré de votre liste d'anniversaire"

    def case_addbirthday(self,slots):
        with open(self.birthday_file, 'a') as file:
            file.write(slots["person"] +","+slots["dateBirthday"])
        return slots["person"]+" a bien été ajouté dans votre liste d'anniversaire"

    def case_listbirthday(self,slots):
        response=""
        with open(self.birthday_file, 'r') as file:
            for line in file:
                response+=line+" "
        return "Voici votre liste d'anniversaire : "+response
