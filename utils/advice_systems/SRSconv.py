# from advice_system1 import advice_system1
from importlib import reload
import utils.advice_systems.SRS as SRS

reload(SRS)

from utils.advice_systems.SRS import SRS


class SRSconv(SRS):

    def __init__(self, alphabet=None):
        if alphabet is None:
            alphabet = []
        upper_letters = [a for a in alphabet if a.isupper()]
        lower_letters = [b for b in alphabet if not b.isupper()]

        pi = []
        for a in upper_letters:
            for b in lower_letters:
                pi.append((a + b, b + a))
        self.pi = pi

    def get_normal_form(self, w):
        def custom_key(x):
            if x.isupper():
                return 0
            if x.islower():
                return 1

        return "".join(sorted(w, key=custom_key))
