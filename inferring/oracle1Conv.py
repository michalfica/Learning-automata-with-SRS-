# from oracle1 import Oracle1
from oracle1prof import OracleProf

"""klasa implementująca więzy:
 SYSTEM PRZEPISYWANIA SŁÓW, reguła: ZAMIEŃ SĄSIEDNIE LITERY, ale
 zamienia tylko litery z 'różnych' alfabetów """


class Oracle1Conv(OracleProf):

    def __init__(self, alphabet=[]):
        upper_letters = [a for a in alphabet if a.isupper()]
        lower_letters = [b for b in alphabet if not b.isupper()]

        pi = []
        for a in upper_letters:
            for b in lower_letters:
                pi.append((a + b, b + a))
                pi.append((b + a, a + b))
        self.pi = pi

    # def __init__(self):
    #     super().__init__()

    # def get_adjacents(self, w):
    #     def get_type(s):
    #         return s.isupper()

    #     s = set()
    #     for i in range(len(w) - 1):
    #         if get_type(w[i]) != get_type(w[i + 1]):
    #             t = "".join(w[:i]) + w[i + 1] + w[i] + w[i + 2 :]
    #             s.add(t)
    #     return s
