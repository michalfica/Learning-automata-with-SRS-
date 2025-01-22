# from advice_system1 import advice_system1
from importlib import reload
import utils.advice_systems.SRS as SRS

reload(SRS)

from utils.advice_systems.SRS import SRS

"""klasa implementująca więzy:
 SYSTEM PRZEPISYWANIA SŁÓW, reguła: wszystko co przed słowem resetującym nieważne"""


class SRSreset(SRS):

    def __init__(self, alphabet, reset_words):
        pi = []
        for w in reset_words:
            for a in alphabet:
                pi.append((a + w, w))
        self.pi = pi
        self.reset_words = reset_words

    def get_normal_form(self, w):
        idx = max([w.rfind(r) for r in self.reset_words])
        return w[idx:] if idx != -1 else w
