import sys
import copy
from importlib import reload

sys.path.append("../")
sys.path.append("../utils/")
sys.path.append("../utils/DFA")
import inferring.Inferring
import utils.automats.DFA

reload(inferring.Inferring)
reload(utils.automats.DFA)
from inferring.Inferring import Inferring
from utils.automats.DFA.DFA import DFA


class InferringDFA(Inferring):
    def __init__(self, target, oracle=None, check_consistency=False, debug=False):
        super().__init__(
            target=target,
            oracle=oracle,
            check_consistency=check_consistency,
            debug=debug,
        )

    def _initialization(self):
        self._extend_E(self.input_signs + [""])
        for e in self.E:
            self.T[("", e)] = self._query_type1("", e)
        self._extend_S("")

    def _query_type1(self, s, e):
        w = s + e

        if w in self.queries:
            return self.queries[w]

        if self.oracle is not None:
            ans = self.oracle.ask_oracle(w, self.queries)
            if ans != self.oracle.NO_ANSWER:
                return ans

        self.cnt[0] += 1
        ans = self.target.route(w)[1]
        self.queries[w] = ans

        if self.oracle is not None:
            w_norm = self.oracle.get_normal_form(w)
            self.queries[w_norm] = ans

        return ans

    def _create_conjecture(self):
        def _equivalent_in_S(s):
            for i, (t, t_binary) in enumerate(self.S):
                if self._E_realtion(s, t):
                    return i

        conjecture = DFA(Q=len(self.S), input_signs=self.input_signs, F=set())
        for i, (s, s_binary) in enumerate(self.S):
            for a in self.input_signs:
                conjecture.δ[(i, a)] = _equivalent_in_S(s + a)
            if self.T[(s, "")] == DFA.ACCEPT:
                conjecture.F.add(i)
        return copy.deepcopy(conjecture)
