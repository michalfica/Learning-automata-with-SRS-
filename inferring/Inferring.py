from importlib import reload

import sys

sys.path.append("../")
sys.path.append("../utils")

import utils.automats.MM.MealyMachine
import utils.automats.DFA.DFA

reload(utils.automats.MM.MealyMachine)
reload(utils.automats.DFA.DFA)

import copy


class Inferring:
    NO_ANSWER = ""

    def __init__(self, target, oracle=None, check_consistency=False, debug=False):
        self.target = target
        self.oracle = oracle  # DFA or Mealy machine (for now)
        self.input_signs = self.target.input_signs
        self.output_signs = self.target.output_signs
        self.S = set()
        self.E = set()
        self.T = dict()
        self.cnt = [0, 0]
        self.counterexamples = []
        self.debug = debug

        self.queries = dict()
        self.check_consistency = check_consistency

    def _initialization(self):
        pass

    def run(self, counterexamples=False):
        self._initialization()

        while True:
            if self.debug:
                print(f"S = {sorted(self.S)}, rozmiar E = {sorted(self.E)}")
            check, x = self._closed()
            while check == False:
                self._extend_S(x)
                check, x = self._closed()

            if self.debug:
                print(
                    f"zamkniętość sprawdzona - S = {sorted(self.S)}, rozmiar E = {sorted(self.E)}"
                )

            conjecture = self._create_conjecture()

            if self.debug:
                print(f"hipoteza: ")
                conjecture.print_transitions()

            if self.check_consistency:
                assert (
                    self.oracle is not None
                ), "Nie można sprawdzać zgodności z więzami gdy nie ma więzów!"

                if self.debug:
                    print("sprawdzam ZGODNOŚĆ z więzami")

                xs = self._check_consistenticy_with_pi(
                    copy.deepcopy(conjecture), copy.deepcopy(self.oracle)
                )
                if self.debug:
                    print(f"z niezgodnośći wynikaja takie kontrprzykłady: {xs}")
                while len(xs) > 0:
                    for x in xs:
                        self.counterexamples.append(x)
                        self._process_counterexample(x)

                    check, x = self._closed()
                    while check == False:
                        self._extend_S(x)
                        check, x = self._closed()

                    conjecture = self._create_conjecture()
                    if self.debug:
                        print(f"stworzyłem nową hipoteze:")
                        conjecture.print_transitions()
                    xs = self._check_consistenticy_with_pi(
                        copy.deepcopy(conjecture), copy.deepcopy(self.oracle)
                    )
                    if self.debug:
                        print(f"z niezgodnośći wynikaja takie kontrprzykłady: {xs}")

            check, x = self._query_type2(conjecture)

            if check == False:
                if self.debug:
                    print(f"kontrprzyklad (z zapytania o równoważność)= {x}")
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

            if self.debug:
                print("\n\n")

    def _ask_oracle(self, w):
        return self.oracle.route(w)[1]

    def _query_type1(self, s, e):
        pass

    def _query_type2(self, conjecture):
        self.cnt[1] += 1
        return self.target.equiv(conjecture)

    def _E_realtion(self, s, t):
        for e in self.E:
            if self.T[(s, e)] != self.T[(t, e)]:
                return False
        return True

    def _closed(self):
        wlist = []
        for s in self.S:
            for a in self.input_signs:
                if s + a not in self.S:
                    wlist.append(s + a)
        wlist = sorted(wlist, key=len)

        for w in wlist:
            check = False
            for t in self.S:
                if self._E_realtion(w, t):
                    check = True
                    break
            if not check:
                return (False, w)
        return (True, "")

    def _extend_S(self, s):
        self.S.add(s)
        for a in self.input_signs:
            for e in self.E:
                self.T[(s + a, e)] = self._query_type1(s + a, e)

    def _extend_E(self, elist):
        for s in self.S:

            for e in elist:
                if e not in self.E:
                    self.T[(s, e)] = self._query_type1(s, e)

            for a in self.input_signs:
                for e in elist:
                    if e not in self.E and s + a not in self.S:
                        self.T[(s + a, e)] = self._query_type1(s + a, e)
        self.E.update(elist)

    def _create_conjecture(self):
        pass

    def _process_counterexample(self, w):
        states = copy.deepcopy(self.S)
        max_pref, idx = "", -1
        for a in w:
            if max_pref + a in states:
                max_pref += a
                idx += 1
            else:
                break

        max_pref += w[idx + 1]  # dokładam jedną literkę
        idx += 1

        w = w[idx + 1 :]  # zostawiam sobie sufiks
        w = w[::-1]  # odwracam go

        suffixes, suffix = [], ""
        for a in w:
            suffix = a + suffix
            suffixes.append(suffix)
        self._extend_E(suffixes)

    def _check_consistenticy_with_pi(self, conjecture, oracle):
        def get_distinction_word(q1, q2):
            for e in self.E:
                if e == "":
                    continue

                q1e, q2e = conjecture.route_and_return_q(
                    w=e, q0=q1
                ), conjecture.route_and_return_q(w=e, q0=q2)

                if (q1e in conjecture.F and q2e not in conjecture.F) or (
                    q1e not in conjecture.F and q2e in conjecture.F
                ):
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
                    c1, c2 = (
                        copy.deepcopy(s) + copy.deepcopy(l) + copy.deepcopy(y),
                        copy.deepcopy(s) + copy.deepcopy(r) + copy.deepcopy(y),
                    )
                    self.cnt[0] += 1
                    if self.target.route(c1)[1] != conjecture.route(c1)[1]:
                        counterexamples.add(c1)
                        return counterexamples
                    else:
                        counterexamples.add(c2)
                        return counterexamples
        return counterexamples
