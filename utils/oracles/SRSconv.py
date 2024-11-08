# from oracle1 import Oracle1
from importlib import reload
import utils.oracles.SRS as SRS

reload(SRS)

from utils.oracles.SRS import SRS

"""klasa implementująca więzy:
 SYSTEM PRZEPISYWANIA SŁÓW, reguła: ZAMIEŃ SĄSIEDNIE LITERY, ale
 zamienia tylko litery z 'różnych' alfabetów """


class SRSconv(SRS):

    def __init__(self, alphabet=[]):
        upper_letters = [a for a in alphabet if a.isupper()]
        lower_letters = [b for b in alphabet if not b.isupper()]

        pi = []
        for a in upper_letters:
            for b in lower_letters:
                pi.append((a + b, b + a))
        self.pi = pi
