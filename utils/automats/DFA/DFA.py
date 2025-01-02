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
    NOT_DEFINED, SIMPLE_DFA, CONV_DFA = "not defined", "DFA", "convDFA"
    BITWISE_ADDITION = "bitwise addition"
    AND_TYPE_PATTERN_DFA, OR_TYPE_PATTERN_DFA = "AND", "OR"
    EMPTY_STRING = ""

    def __init__(self, Q=0, input_signs=None, δ=None, F=None, type_=NOT_DEFINED):
        if input_signs is None:
            input_signs = []
        if δ is None:
            δ = dict()
        if F is None:
            F = set()

        self.Q = Q
        self.input_signs = input_signs
        self.output_signs = []
        self.δ = δ
        self.F = F
        self.type = type_

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

    def route(self, w, q0=0, route_and_return_q=False):
        q = q0
        for a in w:
            assert (q, a) in self.δ, "nie ma takie przejścia w maszynie!"
            q = self.δ[(q, a)]
        if route_and_return_q:
            return q

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
    Funkcja, mając dane dwa automaty, tworzy ich splot.

    Konwencja dotycząca alfabetu:
        * pozdbiór input_signs zawierający tylko MAŁE litery tworzy alfabet automatu dfa1,
        * pozdbiór input_signs zawierający tylko WIELKIE litery tworzy alfabet automatu dfa2.

    """

    def _compute_state_transitions_for_conv(self, dfa1, dfa2):
        def find_new_state(q, a):
            if a.isupper():
                if a.lower() not in set(dfa2.input_signs):  # add self loop
                    return self.state_mapping[(q[0], q[1])]
                return self.state_mapping[(q[0], dfa2.δ[(q[1], a.lower())])]
            else:
                if a.lower() not in set(dfa1.input_signs):  # add self loop
                    return self.state_mapping[(q[0], q[1])]
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
        self.type = DFA.CONV_DFA
        self.Q = dfa1.Q * dfa2.Q
        self.input_signs = dfa1.input_signs + [a.upper() for a in dfa2.input_signs]
        self.state_mapping = dict()
        self._compute_state_transitions_for_conv(dfa1, dfa2)
        self.F = set([self.state_mapping[q] for q in product(dfa1.F, dfa2.F)])

    """
    Funkcja tworząca automat, akceptujący słowa, w których  występują wzorce. Sa 2 możliwe typy:
        AND - w słowie muszą występować WSZYSTKIE wzorce wyspecyfikowane w polu 'patterns',
        OR  - w słowie musi wystąpić CO NAJMNIEJ 1 wzorzec wyspecyfikowany w polu 'patterns' (poza EMPTY_STRING), 
                dodatkowo jeśli EMPTY_STRING występuje w 'patterns' to do stanów akceptujących należy także stan początkowy.   
    """

    def create_pattern_dfa(self, input_signs, patterns, _type=AND_TYPE_PATTERN_DFA):
        assert len(set(patterns)) == len(patterns), "Wszystkie wzorce muszą być różne!"
        assert _type == DFA.OR_TYPE_PATTERN_DFA or DFA.EMPTY_STRING not in set(
            patterns
        ), "Nie dpouszczalny pusty string dla PDdfa typu AND!"

        def compute_number_of_states():
            k = 1
            for x in patterns:
                k *= len(x) + 1
            return k

        patterns.sort(key=lambda s: -len(s))
        if patterns[-1] == DFA.EMPTY_STRING:
            patterns.pop()
            self.mark_start_state_as_accepting = True
        else:
            self.mark_start_state_as_accepting = False

        self.Q = compute_number_of_states()
        self.input_signs = input_signs
        self.patterns = patterns
        self.n = len(patterns)
        self.state_mapping = dict()
        self.type = _type

        self._compute_state_transitions_for_pdfa()
        self._mark_accepting_states_for_pdfa()

    def _compute_state_transitions_for_pdfa(self):
        def find_new_state(x, a):
            words = [self.patterns[i][: x[i]] + a for i in range(self.n)]
            state = []
            for i in range(self.n):
                # szukam max prefiksu słowa self.patterns[i], które jest sufiksem słowa words[i]
                prefixes = set(
                    [self.patterns[i][:j] for j in range(len(self.patterns[i]) + 1)]
                )
                suffixes = [words[i][j:] for j in range(len(words[i]) + 1)]
                for s in suffixes:
                    if s in prefixes:
                        state.append(len(s) % (len(self.patterns[i]) + 1))
                        break
            # korekta, zapamiętuję, że patterns[i] juz wystąpił
            for i in range(self.n):
                if x[i] == len(self.patterns[i]):
                    state[i] = x[i]

            return self.state_mapping[tuple(state)]

        xs = [range(len(x) + 1) for x in self.patterns]
        nested_loop1, nested_loop2 = product(*xs), product(*xs)

        cnt = 0
        for x in nested_loop1:
            self.state_mapping[x] = cnt
            cnt += 1
        for x in nested_loop2:
            for a in self.input_signs:
                self.δ[(self.state_mapping[x], a)] = find_new_state(x, a)

    def _mark_accepting_states_for_pdfa(self):
        if self.mark_start_state_as_accepting:
            start_state = self.state_mapping[tuple([0 for _ in range(self.n)])]
            self.F.add(start_state)

        if self.type == DFA.AND_TYPE_PATTERN_DFA:
            state = [len(x) for x in self.patterns]
            accept_state = self.state_mapping[tuple(state)]
            self.F.add(accept_state)
        elif self.type == DFA.OR_TYPE_PATTERN_DFA:
            xs = [range(len(x) + 1) for x in self.patterns]
            nested_loop = product(*xs)
            for state in nested_loop:
                for i in range(self.n):
                    if state[i] == len(self.patterns[i]):
                        self.F.add(self.state_mapping[tuple(state)])
        else:
            assert False, "Wrong type of PatternDFA, 'AND' or 'OR' type allowed only!"
