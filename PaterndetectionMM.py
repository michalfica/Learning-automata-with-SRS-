from utils.Mealymachine import MealyMachine
from itertools import product


class PaternMM(MealyMachine):
    def __init__(self, patterns, insigns, outsigns):
        n = 1
        for x in patterns:
            n *= len(x) + 1
        super().__init__(Q=n, input_signs=insigns, output_signs=outsigns)
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
        match len(self.patterns):
            case 1:
                cnt = 0
                for x in product(xs[0]):
                    self.state_mapping[x] = cnt
                    cnt += 1
                for x in product(xs[0]):
                    for a in self.input_signs:
                        self.δ[(self.state_mapping[x], a)] = find_new_state(x, a)
            # case 2:
            #     for x in product(xs[0], xs[1]):
            #         for a in self.input_signs:
            #             self.δ[(cnt, a)] = find_new_state(x, a)
            #             cnt += 1
            # case 3:
            #     for x in product(xs[0], xs[1], xs[2]):
            #         for a in self.input_signs:
            #             self.δ[(cnt, a)] = find_new_state(x, a)
            #             cnt += 1
            case _:
                print("PROBLEM!")

    def _compute_output_function(self):
        pass
