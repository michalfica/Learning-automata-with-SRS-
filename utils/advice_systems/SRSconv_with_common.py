# from advice_system1 import advice_system1
from importlib import reload
import utils.advice_systems.SRS as SRS

reload(SRS)

from utils.advice_systems.SRS import SRS


class SRSconv_with_common(SRS):

    def __init__(self, alphabet=None, common_letters=None):
        if alphabet is None:
            alphabet = []

        if len(common_letters) == 0:
            assert (
                len(alphabet) % 2 == 0
            ), "Nie zgadza się rozmiar alfabetu !!!(załozenie jest takie ze oba automaty, które wchodzą w skałąd konwolucji majaą alfabet tego samego rozmiaru)"
            st_alphbt = alphabet[: len(alphabet) // 2]
            nd_alphbt = alphabet[len(alphabet) // 2 :]
        else:
            st_alphbt = alphabet[: alphabet.index(common_letters[0])]
            nd_alphbt = alphabet[alphabet.index(common_letters[-1]) + 1 :]

        pi = []
        for a in st_alphbt:
            for b in nd_alphbt:
                pi.append((a + b, b + a))
        self.pi = pi
        self.common_letter = common_letters
        self.st_alphbt = st_alphbt
        self.nd_alphbt = nd_alphbt

    def get_normal_form(self, w):

        def custom_key(x):
            if x in set(self.st_alphbt):
                return 0
            if x in set(self.nd_alphbt):
                return 1

        normal_form = ""
        helper = ""
        for a in w:
            if a not in self.common_letter:
                helper += a
            else:
                normal_form += "".join(sorted(helper, key=custom_key))
                normal_form += a
                helper = ""

        normal_form += "".join(sorted(helper, key=custom_key))
        return normal_form
