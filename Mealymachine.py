import numpy as np
from queue import Queue


class MealyMachine:
    """konwencja:
    Q                   - liczba stanów maszyny,
    input, output_signs - alfabet wejściowy/wyjściowy jako lista?
    λ                   - funkcja (q,a) -> a (jaką literke wypisać przy danym przejściu), słownik
    δ                   - funkcja (q,a) -> q'(funkcja przejścia automatu), słownik
    """

    def __init__(self, Q=0, input_signs=None, output_signs=None, λ=dict(), δ=dict()):
        self.Q = Q
        self.input_signs = sorted(input_signs)  # sortowanie by móc porównywac
        self.output_signs = sorted(output_signs)
        self.λ = λ
        self.δ = δ

    def __str__(self):
        return f"Mealy Machine amount of states = {self.Q}, I = {self.input_signs}, O = {self.output_signs}"

    def route(self, w=10):
        w = (
            "".join(np.random.choice(self.input_signs, w, replace=True))
            if isinstance(w, int)
            else w
        )
        v, q = "", 0
        for a in w:
            assert (q, a) in self.λ and (
                q,
                a,
            ) in self.δ, "nie ma taiego przejścia w maszynie, potencjalnie zły alfabet!"
            v += self.λ[(q, a)]
            q = self.δ[(q, a)]
        return (w, v)

    def print_transitions(self):
        for q in range(self.Q):
            for a in self.input_signs:
                assert (q, a) in self.λ and (
                    q,
                    a,
                ) in self.δ, (
                    "nie ma taiego przejścia w maszynie, potencjalnie zły alfabet!"
                )
                print(f"({q},{a}) --> '{self.λ[(q,a)]}',{self.δ[(q,a)]}")

    """
    zwracane wartości:
        1  -> różne alfabety obu maszyn 
        "" -> maszyny równoważne 
        s  -> słowo rozróżniające automaty 
    """

    def equiv(self, other):

        def BFS():
            visited = dict()
            Q = Queue()

            def addToQueue(state, w):
                if not (state, w[-1]) in visited:
                    visited[(state, w[-1])] = True
                    Q.put((state, w))

            addToQueue((0, 0), "0")
            while not Q.empty():
                item = Q.get()
                q1, q2, w = item[0][0], item[0][1], item[1]
                for a in self.input_signs:
                    l1, l2 = self.λ[(q1, a)], other.λ[(q2, a)]
                    if l1 != l2:
                        return w + a
                    else:
                        addToQueue((self.δ[(q1, a)], other.δ[(q2, a)]), w + a)
            return ""

        if not (
            self.input_signs == other.input_signs
            and self.output_signs == other.output_signs
        ):
            assert (
                False
            ), "automaty pracują na różnych alfabetach - nie moga być równoważne!"

        counterexample = BFS()
        if counterexample == "":
            return (True, "")
        return (False, counterexample[1:])
