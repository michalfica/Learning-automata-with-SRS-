from utils.automats.DFA.DFA import DFA
from itertools import product


"""Klasa automatów, akceptująca słowa, w których  występują 
   WSZYSTKIE wzorce wyspecyfikowane w polu 'patterns'"""


class PatternDFA(DFA):
    AND_TYPE_PATTERN_DFA = "AND"
    OR_TYPE_PATTERN_DFA = "OR"
    EMPTY_STRING = ""

    def __init__(self, input_signs, patterns, _type=AND_TYPE_PATTERN_DFA):
        def compute_number_of_states():
            k = 1
            for x in patterns:
                k *= len(x) + 1
            return k

        super().__init__(
            Q=compute_number_of_states(), input_signs=input_signs, δ=dict(), F=set()
        )

        patterns.sort(key=lambda s: -len(s))
        if patterns[-1] == PatternDFA.EMPTY_STRING:
            patterns.pop()
            self.mark_start_state_as_accepting = True
        else:
            self.mark_start_state_as_accepting = False

        self.patterns = patterns
        self.n = len(patterns)
        self.state_mapping = dict()
        self.type = _type
        self._compute_state_transitions()
        self._mark_accepting_states()

    def _compute_state_transitions(self):
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

    def _mark_accepting_states(self):
        if self.mark_start_state_as_accepting:
            start_state = self.state_mapping[tuple([0 for _ in range(self.n)])]
            self.F.add(start_state)

        if self.type == PatternDFA.AND_TYPE_PATTERN_DFA:
            state = [len(x) for x in self.patterns]
            accept_state = self.state_mapping[tuple(state)]
            self.F.add(accept_state)
        elif self.type == PatternDFA.OR_TYPE_PATTERN_DFA:
            xs = [range(len(x) + 1) for x in self.patterns]
            nested_loop = product(*xs)
            for state in nested_loop:
                for i in range(self.n):
                    if state[i] == len(self.patterns[i]):
                        self.F.add(self.state_mapping[tuple(state)])
        else:
            assert False, "Wrong type of PatternDFA, 'AND' or 'OR' type allowed only!"
