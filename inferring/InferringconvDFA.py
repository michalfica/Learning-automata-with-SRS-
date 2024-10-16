from InferringDFA import InferringDFA
from utils.DFA import DFA
from utils.convDFA import convDFA
from oracle1Conv import Oracle1Conv
import copy

"""
    Osobna klasa na czenie się splotu 2 DFA.
    bo hipoteza jest convDFA a nie DFA 
"""


class InferringconvDFA(InferringDFA):
    def __init__(self, target, oracle=None, debug=False, check_consistency=False):
        if oracle is not None:
            oracle = Oracle1Conv(target.input_signs)

        super().__init__(
            target=target,
            oracle=oracle,
            debug=debug,
            check_consistency=check_consistency,
        )

    def _create_conjecture(self):
        def _equivalent_in_S(s):
            for i, t in enumerate(self.S):
                if self._E_realtion(s, t):
                    return i

        conjecture = convDFA(
            type="dfa", Q=len(self.S), input_signs=self.input_signs, F=set()
        )
        for i, s in enumerate(self.S):
            conjecture.mapping[i] = s
            for a in self.input_signs:
                conjecture.δ[(i, a)] = _equivalent_in_S(s + a)
            if self.T[(s, "")] == DFA.ACCEPT:
                conjecture.F.add(i)
        return copy.deepcopy(conjecture)

    def _check_consistenticy_with_pi(self, conjecture, oracle):
        def get_distinction_word(q1, q2):
            for e in self.E:
                if e == "":
                    continue

                q1e, q2e = conjecture.route_and_return_q(
                    w=e, q0=q1
                ), conjecture.route_and_return_q(w=e, q0=q2)

                if q1e != q2e:
                    return copy.deepcopy(e)

            assert False, "Nie powiodło się szukanie słowa rozróżniającego!"

        counterexamples = set()
        for q in range(conjecture.Q):
            for l, r in oracle.pi:
                q1, q2 = conjecture.route_and_return_q(
                    w=l, q0=q
                ), conjecture.route_and_return_q(w=r, q0=q)

                if q1 != q2:
                    y = get_distinction_word(q1, q2)
                    s = conjecture.mapping[q]

                    print(
                        f"q = {q}, q1 = {q1}, q2 = {q2}, s = {s}, (l, r) = ({l},{r}), y = {y} "
                    )
                    c1, c2 = (
                        copy.deepcopy(s) + copy.deepcopy(l) + copy.deepcopy(y),
                        copy.deepcopy(s) + copy.deepcopy(r) + copy.deepcopy(y),
                    )
                    if self.target.route(c1)[1] != conjecture.route(c1)[1]:
                        counterexamples.add(c1)
                    if self.target.route(c2)[1] != conjecture.route(c2)[1]:
                        counterexamples.add(c2)
                    # self.cnt[0] += 2
        return counterexamples
