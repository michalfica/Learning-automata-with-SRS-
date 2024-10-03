import sys

from importlib import reload

sys.path.append("../")

import utils.Inferring

reload(utils.Inferring)
from utils.Inferring import Inferring

import utils.Mealymachine as Mealymachine
from utils.Mealymachine import MealyMachine


class InferringMM(Inferring):
    def __init__(self, target_mm, oracle=None, debug=False):
        super().__init__(target_mm=target_mm, oracle=oracle, debug=debug)

    def initialization(self):
        self._extend_E(self.input_signs)
        for e in self.E:
            self.T[("", e)] = self._query_type1("" + e)[-len(e) :]
        self._extend_S("")

    def _query_type1(self, w):
        # return "kurwamac!" # dlaczego się z tym zapętla ? tego  nie wiem
        if self.oracle is not None:

            ans = self.queries[w] if w in self.queries else self._ask_oracle(w)

            if ans != self.NO_ANSWER and ans == self.target_mm.route(w)[1]:
                self.queries[w] = ans
                return ans

        if w not in self.queries:
            self.cnt[0] += 1
            if self.debug and self.oracle is not None:
                print(f"zapytanie o słowo {w}")
            self.queries[w] = self.target_mm.route(w)[1]

        return self.queries[w]

    def create_conjecture(self):
        def _equivalent_in_S(s):
            for i, t in enumerate(self.S):
                if self._E_realtion(s, t):
                    return i

        conjecture = MealyMachine(
            Q=len(self.S), input_signs=self.input_signs, output_signs=self.output_signs
        )
        for i, s in enumerate(self.S):
            for a in self.input_signs:
                conjecture.λ[(i, a)] = self.T[(s, a)]
                conjecture.δ[(i, a)] = _equivalent_in_S(s + a)
        return conjecture
