# from advice_system1 import advice_system1
from importlib import reload
import utils.advice_systems.SRS as SRS

reload(SRS)

from utils.advice_systems.SRS import SRS

"""klasa implementująca więzy:
 SYSTEM PRZEPISYWANIA SŁÓW, reguła: Alpha w Betha"""


class SRSmark(SRS):

    def __init__(self, alphabet):
        pi = []
        pi.append(("ββ", "αα"))
        for a in alphabet:
            if a != "α":
                pi.append((a + "α", "αα"))
            if a != "β":
                pi.append(("β" + a, "ββ"))
            pi.append(("αα" + a, "αα"))
        self.pi = pi

    def get_normal_form(self, w):
        n = len(w)
        l, r = w.rfind("α"), w.find("β")
        if l != -1 and r != -1:
            return w if (l == 0 and r == n - 1) else "αα"
        if l != -1:
            return w if l == 0 else "αα"
        if r != -1:
            return w if r == n - 1 else "αα"
        return w
