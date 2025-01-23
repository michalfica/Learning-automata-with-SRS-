from queue import Queue
import copy
import re


class SRS:
    NO_ANSWER = ""

    def __init__(self, pi=None):
        if pi is None:
            pi = []

        def check_permissible(xs):
            for l, r in xs:
                if len(l) < len(r):
                    return False
            return True

        assert check_permissible(pi), "Such SRS not permitted!"
        self.pi = pi

    def get_normal_form(self, w):
        normal_form = copy.deepcopy(w)

        while True:
            check = False
            for l, r in self.pi:
                find_all = [
                    i.start() for i in re.finditer("(?=" + l + ")", normal_form)
                ]

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

    def ask_advice_system(self, w, answers):
        nrm_form = self.get_normal_form(w)
        if nrm_form in answers:
            return answers[nrm_form]
        else:
            return SRS.NO_ANSWER
