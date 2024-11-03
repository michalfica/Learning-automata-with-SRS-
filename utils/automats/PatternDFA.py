from utils.automats.DFA import DFA
from itertools import product


class PatternDFA(DFA):
    def __init__(self, input_signs, patterns):
        def compute_number_of_states():
            k = 1
            for x in patterns:
                k *= len(x) + 1
            return k

        # print(f"stany akcept = {self.F}")
        super().__init__(
            Q=compute_number_of_states(), input_signs=input_signs, δ=dict(), F=set()
        )
        # print(f"stany akcept = {self.F}")
        self.patterns = patterns
        self.n = len(patterns)
        self.state_mapping = dict()
        self._compute_state_transitions()
        # print(f"stany akcept = {self.F}")
        self._mark_accepting_states()  # and correct transtion function
        # print(f"stany akcept = {self.F}")

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
            # korekta
            for i in range(self.n):
                if x[i] == len(self.patterns[i]):
                    state[i] = x[i]

            return self.state_mapping[tuple(state)]

        xs = [range(len(x) + 1) for x in self.patterns]

        match self.n:
            case 1:
                nested_loop1, nested_loop2 = product(xs[0]), product(xs[0])
            case 2:
                nested_loop1, nested_loop2 = product(xs[0], xs[1]), product(
                    xs[0], xs[1]
                )
            case 3:
                nested_loop1, nested_loop2 = product(xs[0], xs[1], xs[2]), product(
                    xs[0], xs[1], xs[2]
                )
            case 4:
                nested_loop1, nested_loop2 = product(
                    xs[0], xs[1], xs[2], xs[3]
                ), product(xs[0], xs[1], xs[2], xs[3])
            case _:
                assert False, "too much patterns, maximum possible number is only 4!"
        cnt = 0
        for x in nested_loop1:
            self.state_mapping[x] = cnt
            cnt += 1
        for x in nested_loop2:
            for a in self.input_signs:
                self.δ[(self.state_mapping[x], a)] = find_new_state(x, a)

    def _mark_accepting_states(self):
        state = [len(x) for x in self.patterns]
        accept_state = self.state_mapping[tuple(state)]
        # print(f"dodaje do akceptujacych {accept_state}")
        self.F.add(accept_state)

        # # correcnt transition function
        # for a in self.input_signs:
        #     self.δ[(accept_state, a)] = accept_state
