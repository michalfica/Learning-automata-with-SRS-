from utils.MealyMachine import MealyMachine
from itertools import product
import numpy as np


class PatternSwap(MealyMachine):
    """
    patterns - list of pairs of patterns to swap
    n        - amount of pairs of pattens

    The state in the machine is a (n+2)-element tuple, on the ith coordniate there is:
        (*) 0 <= i < n   - length of max prefix of i-th pattern, ending on curently read word,
        (*) n <= i < n+1 - the number of currently printed pattern (NUMBERED FROM 1 TO N)    or 0          otherwise,
        (*) i == n+1     - the number of the currently printed pattern letter                or [whatever] otherwise.

    Note on the 'language'/relation defined by PatternSwap machines:
    patterns recognised in text by the machine are DISJOINT, swaps can not overlap, (printing next pattern-swap can take only place after previous printing is finised)
    """

    def __init__(self, patterns, insigns, outsigns, debug=False):

        def compute_number_of_states(xs):
            k = np.prod([len(x[0]) + 1 for x in xs])
            m = max(1, np.max([len(x[1]) for x in xs]))
            return k * (len(xs) + 1) * m

        super().__init__(
            Q=compute_number_of_states(xs=patterns),
            input_signs=insigns,
            output_signs=outsigns,
        )

        self.patterns = patterns
        self.n = len(self.patterns)
        self.NO_PRINTNIG = 0
        self.state_mapping = dict()
        self.debug = debug
        self._compute_state_transitions()
        self._compte_output_function()

    """
    zwraca długość:
        i == 1 k-tego zamiennika 
        i == 0 k-tego wzorca 
    """

    def sz(self, k, i=1):
        return len(self.patterns[k][i])

    def _compute_state_transitions(self):
        def find_new_state(x, a):
            printing, letter = x[self.n], x[self.n + 1]
            if printing != self.NO_PRINTNIG:
                # jeśli to ostatnia literka - zmień status priniting
                if letter >= self.sz(printing - 1) - 1:
                    printing, letter = self.NO_PRINTNIG, 0
                else:
                    letter += 1

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
                            full_patterns.append(i + 1)
                        state.append(len(s) % (len(self.patterns[i][0]) + 1))
                        break
            assert (
                len(full_patterns) <= 1
            ), "wykryto kilka wzorców naraz w jednym miejscu - niewiadomo co wypisać!"

            if printing == self.NO_PRINTNIG:
                if len(full_patterns) == 1:
                    printing, letter = full_patterns[0], 0
            state.extend([printing, letter])
            return self.state_mapping[tuple(state)]

        xs = [range(self.sz(k, i=0) + 1) for k in range(self.n)]
        xs.append(range(self.n + 1))
        xs.append(range(max([self.sz(k, i=1) for k in range(self.n)])))

        match self.n:
            case 1:
                nested_loop1, nested_loop2 = product(xs[0], xs[1], xs[2]), product(
                    xs[0], xs[1], xs[2]
                )
            case 2:
                nested_loop1, nested_loop2 = product(
                    xs[0], xs[1], xs[2], xs[3]
                ), product(xs[0], xs[1], xs[2], xs[3])
            case _:
                assert False, "too much patterns, maximum possible is only 2!"
        cnt = 0
        for x in nested_loop1:
            self.state_mapping[x] = cnt
            cnt += 1
        for x in nested_loop2:
            for a in self.input_signs:
                self.δ[(self.state_mapping[x], a)] = find_new_state(x, a)

    def _compte_output_function(self):
        for i in range(self.Q):
            for a in self.input_signs:
                q = list(self.state_mapping.keys())[
                    list(self.state_mapping.values()).index(i)
                ]
                printing, letter = q[self.n], q[self.n + 1]
                if printing != self.NO_PRINTNIG and letter < self.sz(printing - 1):
                    letter = self.patterns[printing - 1][1][letter]
                else:
                    letter = a
                self.λ[(i, a)] = letter
