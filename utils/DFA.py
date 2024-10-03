from queue import Queue


class DFA:
    """konwencja:
    Q                   - liczba stanów maszyny,
    input_signs         - alfabet wejściowy,
    δ                   - funkcja (q,a) -> q'(funkcja przejścia automatu), słownik
    F                   - zbiór stanów akceptujących
    """

    NO_ANSWER = ""

    def __init__(self, Q, input_signs=[], δ=dict(), F=set()):
        self.Q = Q
        self.input_signs = input_signs
        self.δ = δ
        self.F = F

    def __str__(self):
        return f"DFA amount of states = {self.Q}, transitions = {self.δ}, accept states = {self.F}"

    def route(self, w):
        q, v = 0, ""
        for a in w:
            assert (q, a) in self.δ, "nie ma takie przejścia w maszynie!"
            q = self.δ[(q, a)]
        if q in self.F:
            return (w, 1)
        return (w, 0)

    """
    specyficzne przechodzenie po automacie, tworzymy zarazem słowo, 
    funkcja pomocnicza gdy traktowałem dfa jako wyrocznie do uczenia się maszyn mealy'ego 
    """

    def route_oracle(self, w):
        q, v = 0, ""
        for i in range(2 * len(w)):
            if i % 2 == 0:
                q = self.δ[(q, w[i // 2])]
            else:
                for a in self.input_signs:
                    if (q, a) in self.δ:
                        v += a
                        q = self.δ[(q, a)]
        if q in self.F:
            return (w, v)
        else:
            return (w, self.NO_ANSWER)

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
                if not state in visited:
                    visited[state] = True
                    Q.put((state, w))

            addToQueue((0, 0), "0")
            while not Q.empty():
                item = Q.get()
                q1, q2, w = item[0][0], item[0][1], item[1]
                if (q1 in self.F and q2 not in other.F) or (
                    q1 not in self.F and q2 in other.F
                ):
                    return w
                for a in self.input_signs:
                    addToQueue((self.δ[(q1, a)], other.δ[(q2, a)]), w + a)
            return ""

        if not self.input_signs == other.input_signs:
            assert (
                False
            ), "automaty pracują na różnych alfabetach - nie moga być równoważne!"
        counterexample = BFS()
        if counterexample == "":
            return (True, "")
        return (False, counterexample[1:])
