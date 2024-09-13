from utils.Mealymachine import MealyMachine
from itertools import product
import numpy as np


class PatternSwap(MealyMachine):
    """
    patterns - list of pairs of patterns to swap
    n        - amount of pairs of pattens
    """

    NO_PRINTNIG = -1

    def __init__(self, patterns, insigns, outsigns):
        def compute_number_of_states():
            n = np.prod([len(x) for x in patterns])
            m = np.sum([len(x) for x in patterns])
            return n * m

        super().__init__(
            Q=compute_number_of_states(), input_signs=insigns, output_signs=outsigns
        )
        self.patterns = patterns
        self.n = len(self.patterns)
        self.state_mapping = dict()
        self._compute_state_transitions()
        self._compte_output_function()

    def _compute_state_transitions(self):
        def find_new_state(x, a):
            printing, letter = x[self.n], x[self.n + 1]
            if printing != self.NO_PRINTNIG and letter == len(
                self.patterns[printing][1]
            ):
                printing = self.NO_PRINTNIG

            words = [self.patterns[i][0][: x[i]] + a for i in range(self.n)]
            state, full_patterns = [], []
            for i in range(self.n):
                # szukam max prefiksu słowa self.patterns[i][0], które jest sufiksem słowa words[i]
                prefixes = set(
                    [
                        self.patterns[i][0][:j]
                        for j in range(len(self.patterns[i][0]) + 1)
                    ]
                )
                suffixes = [words[i][j:] for j in range(len(words[i]) + 1)]
                for s in suffixes:
                    if s in prefixes:
                        if s == self.patterns[i][0]:
                            full_patterns.append(i)
                        state.append(len(s) % (len(self.patterns[i][0]) + 1))
                        break
            assert (
                full_patterns <= 1
            ), "wykryto kilka wzorców naraz w jednym miejscu - niewiadomo co wypisać!"
            assert (
                printing == self.NO_PRINTNIG or len(full_patterns) == 0
            ), "konflikt przy wypisywaniu!"

            if printing == self.NO_PRINTNIG:
                if full_patterns:
                    printing = full_patterns[0]
                state.extend([printing, 0])
            else:
                state.extend([printing, letter + 1])

            return self.state_mapping[tuple(state)]

        xs = [range(len(x[0]) + 1) for x in self.patterns]
        xs.append(range(self.n + 1))
        xs.append(range(max([len(x[0]) for x in self.patterns])))

        match self.n:
            case 1:
                nested_loop1, nested_loop2 = product(xs[0], xs[1], xs[2]), product(
                    xs[0], xs[1], xs[2]
                )
            case _:
                assert False, "too much patterns, maximum possible is only 1!"

        cnt = 0
        for x in nested_loop1:
            self.state_mapping[x] = cnt
            cnt += 1
        for x in nested_loop2:
            for a in self.input_signs:
                self.δ[(self.state_mapping[x], a)] = find_new_state(x, a)

    def _compte_output_function(self):
        pass
