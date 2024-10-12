from oracle1 import Oracle1

"""klasa implementująca więzy:
 SYSTEM PRZEPISYWANIA SŁÓW, reguła: ZAMIEŃ SĄSIEDNIE LITERY, ale
 zamienia tylko litery z 'różnych' alfabetów """


class Oracle1Conv(Oracle1):
    def __init__(self):
        super().__init__()

    def get_adjacents(self, w):
        def get_type(s):
            return s[-1]

        w = [w[i : i + 2] for i in range(0, len(w), 2)]
        s = set()
        for i in range(len(w) - 1):
            if get_type(w[i]) != get_type(w[i + 1]):
                t = w[:i] + [w[i + 1]] + [w[i]] + w[i + 2 :]
                s.add("".join(t))
        return s
