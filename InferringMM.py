from importlib import reload
import Mealymachine
import OracleDFA

reload(Mealymachine)
reload(OracleDFA)
from Mealymachine import MealyMachine
from OracleDFA import OracleDFA


class InferringMM:
    NO_ANSWER = ""

    def __init__(self, target_mm, oracle=None):
        self.target_mm = target_mm
        self.oracle = oracle  # DFA (for now)
        self.input_signs = self.target_mm.input_signs
        self.output_signs = self.target_mm.output_signs
        self.S = set()
        self.E = set()
        self.T = dict()
        self.cnt = [0, 0]
        self.counterexamples = []

    def run(self, counterexamples=False):
        # 1 krok inicljalizacja
        self._extend_E(self.input_signs)
        self._extend_S("")
        # 2 krok:
        while True:
            check, x = self._closed()
            while check == False:
                self._extend_S(x)
                check, x = self._closed()

            conjecture = self._create_conjecture()
            check, x = self._query_type2(conjecture)

            if check == False:
                self.counterexamples.append(x)
                self._process_counterexample(x)
            else:
                if counterexamples:
                    return (
                        conjecture,
                        self.cnt,
                        [len(x) for x in self.counterexamples],
                    )
                else:
                    return (conjecture, self.cnt)

    def _ask_oracle(self, w):
        return self.oracle.route(w)

    def _E_realtion(self, s, t):
        for e in self.E:
            if self.T[(s, e)] != self.T[(t, e)]:
                return False
        return True

    def _query_type1(self, w):
        if self.oracle is not None:
            print("ucze sie z wyrocznia :) !!! hahaha")
            ans = self._ask_oracle(w)
            if ans != self.NO_ANSWER:
                print(f"wyocznia mi powiedziała za darmo :)) ")
                return ans

        self.cnt[0] += 1
        return self.target_mm.route(w)[1]

    def _query_type2(self, conjecture):
        self.cnt[1] += 1
        return self.target_mm.equiv(conjecture)

    def _closed(self):
        for s in self.S:
            for a in self.input_signs:
                check = False
                for t in self.S:
                    if self._E_realtion(s + a, t):
                        check = True
                        break
                if not check:
                    return (False, s + a)
        return (True, "")

    def _extend_S(self, s):
        self.S.add(s)
        for a in [""] + self.input_signs:
            for e in self.E:
                self.T[(s + a, e)] = self._query_type1(s + a + e)[-len(e) :]

    def _extend_E(self, elist):
        self.E.update(elist)
        for s in self.S:
            for a in [""] + self.input_signs:
                for e in elist:
                    self.T[(s + a, e)] = self._query_type1(s + a + e)[-len(e) :]

    def _create_conjecture(self):
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

    def _process_counterexample(self, w):
        states = set(self.S)
        max_pref = ""
        idx = -1
        for a in w:
            if max_pref + a in states:
                max_pref += a
                idx += 1
            else:
                break
        w = w[::-1]
        if idx != -1:
            w = w[: -(idx + 1)]

        suffixes, suffix = [], ""
        for a in w:
            suffix = a + suffix
            suffixes.append(suffix)
        self._extend_E(suffixes)
