from queue import Queue
from itertools import product


class DFA:
    """konwencja:
    Q                   - liczba stanów maszyny,
    input_signs         - alfabet wejściowy,
    δ                   - funkcja (q,a) -> q'(funkcja przejścia automatu), słownik
    F                   - zbiór stanów akceptujących
    """

    NO_ANSWER = ""
    ACCEPT = 1
    SIMPLE_DFA, CONV_DFA = "DFA", "convDFA"

    def __init__(self, Q=0, input_signs=[], δ=dict(), F=set()):
        self.Q = Q
        self.input_signs = input_signs
        self.output_signs = []
        self.δ = δ
        self.F = F

        """ mapowanie stanów:
            * dla conv dfa1, dfa2 mapuje krotkę (q1, q2) w stan q, (q1, q2 - to stany odpowiednio w dfa1 i dfa2)"""
        self.mapping = dict()

    def __str__(self):
        return f"DFA amount of states = {self.Q}, transitions = {self.δ}, accept states = {self.F}"

    def print_transitions(self):
        for q in range(self.Q):
            for a in self.input_signs:
                assert (
                    q,
                    a,
                ) in self.δ, (
                    "nie ma taiego przejścia w maszynie, potencjalnie zły alfabet!"
                )
                print(f"({q},{a}) --> {self.δ[(q,a)]}")
        print(f"stany akceptujące - {self.F}")

    def route(self, w):
        q = 0
        for a in w:
            assert (q, a) in self.δ, "nie ma takie przejścia w maszynie!"
            q = self.δ[(q, a)]
        if q in self.F:
            return (w, 1)
        return (w, 0)

    def route_and_return_q(self, w, q0=0):
        q = q0
        for a in w:
            assert (q, a) in self.δ, "nie ma takie przejścia w maszynie!"
            q = self.δ[(q, a)]
        return q

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

    def equiv_dfs(self, other):
        visited = dict()
        alp = []
        alp.extend([a for a in self.input_signs if a.islower()])
        alp.extend([a for a in self.input_signs if a.isupper()])

        def DFS(state, w):
            visited[state] = True
            q1, q2 = state
            if (q1 in self.F and q2 not in other.F) or (
                q1 not in self.F and q2 in other.F
            ):
                return w

            for a in alp:
                u1, u2 = self.δ[(q1, a)], other.δ[(q2, a)]
                if (u1, u2) not in visited:
                    s = DFS((u1, u2), w + a)
                    if s != "":
                        return s

            return ""

        if not self.input_signs == other.input_signs:
            assert (
                False
            ), "automaty pracują na różnych alfabetach - nie moga być równoważne!"
        counterexample = DFS((0, 0), "0")
        if counterexample == "":
            return (True, "")
        return (False, counterexample[1:])

    """
    Dane dwa automaty, tworzę ich splot.

    Konwencja dotycząca alfabetu:
        * pozdbiór input_signs zawierający tylko MAŁE litery tworzy alfabet jednego automatu (ze splotu),
        * pozdbiór input_signs zawierający tylko WIELKIE litery tworzy alfabet drugiego automatu (ze splotu).

    """

    def _compute_state_transitions_for_conv(self, dfa1, dfa2):
        def find_new_state(q, a):
            if a.isupper():
                return self.state_mapping[(q[0], dfa2.δ[(q[1], a.lower())])]
            else:
                return self.state_mapping[(dfa1.δ[(q[0], a)], q[1])]

        nested_loop1, nested_loop2 = product(range(dfa1.Q), range(dfa2.Q)), product(
            range(dfa1.Q), range(dfa2.Q)
        )

        cnt = 0
        for x in nested_loop1:
            self.state_mapping[x] = cnt
            cnt += 1
        for x in nested_loop2:
            for a in self.input_signs:
                self.δ[(self.state_mapping[x], a)] = find_new_state(x, a)

    def create_convolution(self, dfa1, dfa2):
        self.Q = dfa1.Q * dfa2.Q
        self.input_signs = dfa1.input_signs + [a.upper() for a in dfa2.input_signs]
        self.state_mapping = dict()
        self._compute_state_transitions_for_conv(dfa1, dfa2)
        self.F = set([self.state_mapping[q] for q in product(dfa1.F, dfa2.F)])
