import sys
import copy
import BitVector

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
from utils.advice_systems.SRS import SRS
from utils.advice_systems.SRSconv import SRSconv
from utils.advice_systems.SRSreset import SRSreset
from utils.advice_systems.SRSmark import SRSmark
from utils.advice_systems.SRSpartial import SRSpartial
from utils.advice_systems.SRSindemp import SRSindemp


class InferringDFA(Inferring):
    def __init__(
        self,
        target,
        advice_system=None,
        check_consistency=False,
        equiv_query_fashion="BFS",
        debug=False,
    ):
        if advice_system is not None:
            if target.type == DFA.CONV_DFA:
                advice_system = SRSconv(target.input_signs)
            if target.type == DFA.BITWISE_ADDITION:
                advice_system = SRS(pi=[("4", "2"), ("5", "3")])
            if target.type == DFA.SYNCHRONICITY:
                advice_system = SRSreset(
                    alphabet=target.input_signs, reset_words=[target.reset_word]
                )
            if target.type == DFA.MARKEDWORDS:
                advice_system = SRSmark(alphabet=target.input_signs)
            if target.type == DFA.PARTIAL:
                advice_system = SRSpartial(
                    alphabet=advice_system.input_signs, partial_dfa=advice_system
                )
            if target.type == DFA.INDEMPOTENT:
                advice_system = SRSindemp(letter="a")

        super().__init__(
            target=target,
            advice_system=advice_system,
            check_consistency=check_consistency,
            equiv_query_fashion=equiv_query_fashion,
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

        if self.advice_system is not None:
            ans = self.advice_system.ask_advice_system(w, self.queries)
            if ans != self.advice_system.NO_ANSWER:
                return ans

        self.cnt[0] += 1
        ans = self.target.route(w)[1]
        self.queries[w] = ans

        if self.advice_system is not None:
            w_norm = self.advice_system.get_normal_form(w)
            self.queries[w_norm] = ans

        return ans

    def _create_automat(self, _type=DFA.SIMPLE_DFA):

        binary_rep_of_all_states = dict()
        for i, (_, s_binary) in enumerate(self.S):
            binary_rep_of_all_states[tuple(s_binary)] = i
            # binary_rep_of_all_states[str(s_binary)] = i

        def _equivalent_in_S(t):
            t_bitlist = []
            for e in self.E:
                t_bitlist.append(self.T[(t, e)])
            # t_binary = BitVector.BitVector(bitlist=t_bitlist)
            # return binary_rep_of_all_states[str(t_binary)]

            t_binary = t_bitlist
            return binary_rep_of_all_states[tuple(t_binary)]

        conjecture = DFA(Q=len(self.S), input_signs=self.input_signs, type_=_type)

        for i, (s, _) in enumerate(self.S):
            conjecture.mapping[i] = s
            for a in self.input_signs:
                conjecture.δ[(i, a)] = _equivalent_in_S(s + a)
            if self.T[(s, "")] == DFA.ACCEPT:
                conjecture.F.add(i)
        # return copy.deepcopy(conjecture)
        return conjecture

    def _create_conjecture(self):
        return copy.deepcopy(self._create_automat())
