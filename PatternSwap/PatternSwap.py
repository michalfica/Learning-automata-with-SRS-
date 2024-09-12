from utils.Mealymachine import MealyMachine
from itertools import product
import numpy as np


class PatternSwap(MealyMachine):
    """
    patterns - list of pairs of patterns to swap
    n        - amount of pairs of pattens
    """

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
        self._compute_state_transitions()
        self._compte_output_function()

    def _compute_state_transitions(self):
        pass

    def _compte_output_function(self):
        pass
