import sys

sys.path.append("../")
sys.path.append("../utils/")

from importlib import reload

import inferring.Inferring
import utils.automats.MM.MealyMachine

reload(inferring.Inferring)
reload(utils.automats.MM.MealyMachine)
from inferring.Inferring import Inferring
from utils.automats.MM.MealyMachine import MealyMachine


class InferringMM(Inferring):
    def __init__(
        self, target, advice_system=None, equiv_query_fashion="BFS", debug=False
    ):
        super().__init__(
            target=target,
            advice_system=advice_system,
            equiv_query_fashion=equiv_query_fashion,
            debug=debug,
        )

    def _initialization(self):
        self._extend_E(self.input_signs)
        for e in self.E_set:
            self.T[("", e)] = self._query_type1("", e)
        self._extend_S("")

    def _query_type1(self, s, e):
        w = s + e
        if self.advice_system is not None:

            ans = self.queries[w] if w in self.queries else self._ask_advice_system(w)

            if ans != self.NO_ANSWER and ans == self.target.route(w)[1]:
                self.queries[w] = ans
                return ans[-len(e) :]

        if w not in self.queries:
            self.cnt[0] += 1
            if self.debug and self.advice_system is not None:
                print(f"zapytanie o słowo {w}")
            self.queries[w] = self.target.route(w)[1]

        return self.queries[w][-len(e) :]

    def _create_conjecture(self):
        def _equivalent_in_S(s):
            for i, (t, t_binary) in enumerate(self.S):
                if self._E_realtion(s, t):
                    return i

        conjecture = MealyMachine(
            Q=len(self.S), input_signs=self.input_signs, output_signs=self.output_signs
        )
        for i, (s, s_binary) in enumerate(self.S):
            for a in self.input_signs:
                conjecture.λ[(i, a)] = self.T[(s, a)]
                conjecture.δ[(i, a)] = _equivalent_in_S(s + a)
        return conjecture
