from utils.Mealymachine import MealyMachine
from itertools import product


class PaternMM(MealyMachine):
    def __init__(self, patterns, insigns, outsigns):
        def compute_number_of_states():
            k = 1
            for x in patterns:
                k *= len(x) + 1
            return k

        super().__init__(
            Q=compute_number_of_states(), input_signs=insigns, output_signs=outsigns
        )
        self.patterns = patterns
        self.n = len(self.patterns)
        self.state_mapping = dict()
        self._compute_state_transitions()
        self._compute_output_function()

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
                print("too much patterns, maximum possible number is only 4!")
        cnt = 0
        for x in nested_loop1:
            self.state_mapping[x] = cnt
            cnt += 1
        for x in nested_loop2:
            for a in self.input_signs:
                self.δ[(self.state_mapping[x], a)] = find_new_state(x, a)

    def _compute_output_function(self):
        for i in range(self.Q):
            for a in self.input_signs:
                next_state = self.δ[(i, a)]
                q = list(self.state_mapping.keys())[
                    list(self.state_mapping.values()).index(next_state)
                ]
                znaczek = "0"
                for j in range(self.n):
                    if len(self.patterns[j]) == q[j]:
                        znaczek = "1"
                # print(f"q = {q}, patterms = {self.patterns}, znaczek = {znaczek}")
                self.λ[(i, a)] = znaczek
