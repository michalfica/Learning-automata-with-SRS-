import numpy as np
from numpy import random
from queue import Queue

from string import ascii_lowercase as alc


class MealyMachine:
    """konwencja:
    Q                   - liczba stanów maszyny,
    input, output_signs - alfabet wejściowy/wyjściowy jako lista?
    λ                   - funkcja (q,a) -> a (jaką literke wypisać przy danym przejściu), słownik
    δ                   - funkcja (q,a) -> q'(funkcja przejścia automatu), słownik
    """

    def __init__(self, Q=0, input_signs=None, output_signs=None, λ=dict(), δ=dict()):
        self.Q = Q
        # sortowanie by móc porównywac
        self.input_signs = sorted(input_signs) if input_signs is not None else None
        self.output_signs = sorted(output_signs) if output_signs is not None else None
        self.λ = λ
        self.δ = δ

    def __str__(self):
        return f"Mealy Machine amount of states = {self.Q}, I = {self.input_signs}, O = {self.output_signs}"

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

    def fully_conected(self):
        visited = [False] * self.Q

        def dfs(q):
            visited[q] = True
            for a in self.input_signs:
                q_nxt = self.δ[(q, a)]
                if not visited[q_nxt]:
                    dfs(q_nxt)

        for q in range(self.Q):
            visited[q] = False
        dfs(0)
        for q in range(self.Q):
            if not visited[q]:
                return False
        return True

    def random_machine(self):
        self.Q = random.randint(low=1, high=10)
        insz, outsz = (
            random.randint(low=1, high=8, size=1)[0],
            random.randint(low=1, high=8, size=1)[0],
        )
        self.input_signs = [a for i, a in enumerate(alc) if i < insz]
        self.output_signs = [a for i, a in enumerate(alc) if i < outsz]

        for q in range(self.Q):
            for a in self.input_signs:
                x = self.output_signs[random.randint(low=0, high=outsz)]
                self.λ[(q, a)] = x

        for q in range(self.Q):
            for a in self.input_signs:
                nxt_q = random.randint(low=0, high=self.Q)
                self.δ[(q, a)] = nxt_q

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
