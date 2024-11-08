from queue import Queue
import copy
import re

"""klasa implementująca więzy:
SYSTEM PRZEPISYWANIA SŁÓW"""


class OracleProf:
    NO_ANSWER = ""

    def __init__(self, pi):
        def check_permissible(xs):
            for l, r in xs:
                if len(l) < len(r):
                    return False
            return True

        assert check_permissible(pi), "Niedopuszczalny system! Można tylko skracać!"
        self.pi = pi

    """sprawdza czy odpowieć o należenie słowa 'w' do języka można wywnioskować 
    na podstawie zbioru słów, o krórych już wiem czy należą do języka ('answers')"""

    def get_normal_form(self, w):
        normal_form = copy.deepcopy(w)

        while True:
            check = False
            for l, r in self.pi:
                find_all = [
                    i.start() for i in re.finditer("(?=" + l + ")", normal_form)
                ]  # wszytskie wystapienia l w słowie w

                if len(find_all) == 0:
                    continue

                check = True
                normal_form = (
                    "".join(normal_form[: find_all[0]])
                    + copy.deepcopy(r)
                    + normal_form[find_all[0] + len(l) :]
                )
                break
            if check == False:
                break
        return normal_form

    def ask_oracle(self, w, answers):
        nrm_form = self.get_normal_form(w)
        if nrm_form in answers:
            return answers[nrm_form]
        else:
            return OracleProf.NO_ANSWER
