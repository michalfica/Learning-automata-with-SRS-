import sys
import copy
from importlib import reload

sys.path.append("../")
sys.path.append("../utils/")
import inferring.Inferring
import utils.DFA

reload(inferring.Inferring)
reload(utils.DFA)
from inferring.Inferring import Inferring
from utils.DFA import DFA


class InferringDFA(Inferring):
    def __init__(self, target, oracle=None, debug=False, check_consistency=False):
        super().__init__(
            target=target,
            oracle=oracle,
            debug=debug,
            check_consistency=check_consistency,
        )

    def _initialization(self):
        self._extend_E(self.input_signs + [""])
        for e in self.E:
            self.T[("", e)] = self._query_type1("", e)
        self._extend_S("")

    def _query_type1(self, s, e):
        w = s + e
        if self.oracle is not None:
            ans = (
                self.queries[w]
                if w in self.queries
                else self.oracle.ask_oracle(w, self.queries)
            )
            if ans != self.oracle.NO_ANSWER:
                self.queries[w] = ans
                return ans

        if w not in self.queries:
            self.cnt[0] += 1
            self.queries[w] = self.target.route(w)[1]
        return self.queries[w]

    def _create_conjecture(self):
        def _equivalent_in_S(s):
            for i, t in enumerate(self.S):
                if self._E_realtion(s, t):
                    return i

        conjecture = DFA(Q=len(self.S), input_signs=self.input_signs, F=set())
        for i, s in enumerate(self.S):
            for a in self.input_signs:
                conjecture.δ[(i, a)] = _equivalent_in_S(s + a)
            if self.T[(s, "")] == DFA.ACCEPT:
                conjecture.F.add(i)
        return copy.deepcopy(conjecture)
