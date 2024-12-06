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
        self.oracle = oracle
        self.input_signs = self.target.input_signs
        self.output_signs = self.target.output_signs

        self.S_set = set()
        self.S = []

        """
            self.S - list of pairs, i-th element: (s_i, s_i_binary), where 
                    * s_i        is a string representing i-th state, 
                    * s_i_binary is a list consisting of zeros and ones and it forms a binary representation of i-th state, based on self.T[(s, e)] 
        """

        self.E_set = set()
        self.E = []

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

        iter_nuber = 0
        while True:
            iter_nuber += 1
            print(f"iteracja nr: {iter_nuber}")

            if self.debug:
                print(f"S = {len(self.S)}, rozmiar E = {len(self.E)}")
            check, x, last_checked = self._closed(start_index=0)
            while check == False:
                self._extend_S(x)
                check, x, last_checked = self._closed(start_index=last_checked)

            if self.debug:
                print(
                    f"zamkniętość sprawdzona - S = {len(self.S)}, rozmiar E = {len(self.E)}"
                )

            conjecture = self._create_conjecture()

            if self.debug:
                print(f"hipoteza: {conjecture.Q}")
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

                    check, x, last_checked = self._closed(start_index=0)
                    while check == False:
                        self._extend_S(x)
                        check, x, last_checked = self._closed(start_index=last_checked)

                    conjecture = self._create_conjecture()
                    if self.debug:
                        print(f"stworzyłem nową hipoteze: {conjecture.Q}")
                        # conjecture.print_transitions()
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

    # NOTATKO DO _closed():

    #  to chciałbym poprawić
    # aktualnie sprawdzam po prostu czy jest jakiś stan t in self.S równoważny przejściu w
    # Robię to tak: iteruję się po wszystkich stanach t in self.S a potem sprawdzam czy w i t są zgodne dla wszytskich słów rozróżiających
    #
    # czyli time complexity: |liczba przejść do sprawdzenia| * |self.S| * |self.E| * |zapytanie do słownika|
    #
    # JAKA inną metodęużyć zeby usprawnić?
    # Gdybym miał binarną reprezentacje stanów z self.S i trzymał ją w słowniku,
    # to zapytanie czy dane przejśćie ma stan równoważny sprawdzałbym w czasie O(1)
    #
    # ALE co potrzebuję do tego?
    # binarną reprezentacje wszystkich stanów
    #
    # JAk ją utrzymywac, dla każdego stanu pamiętać liste zero-jedynkową, jego reprezentacje binarną
    # Jak ją aktualizować? gdy dodaję nowe słowo do zbioru słów testowych self.E to wynik na tym słowie dorzucam tez do reprezentacji binarnej
    #
    # a co gdy tworzę nowy stan?
    # jego reprezentacje odczytam patrząc się na wiersz w tablicy T w czasie |self.E|

    def _closed(self, start_index=0):
        transitions = []  # transistions to check
        for i in range(start_index, len(self.S)):
            s = self.S[i][0]
            for a in self.input_signs:
                if s + a not in self.S_set:
                    transitions.append((s + a, i))

        binary_rep_of_all_states = set()
        for s in self.S:
            binary_rep_of_all_states.add(tuple(s[-1]))

        for t, i in transitions:
            t_binary = []
            for e in self.E:
                t_binary.append(self.T[(t, e)])

            if tuple(t_binary) not in binary_rep_of_all_states:
                return (False, t, i)

        return (True, "", len(self.S))

        # --------- old, working version: ---------

        # transition_list = []  # transistions to check
        # for i in range(start_index, len(self.S)):
        #     s = self.S[i][0]
        #     for a in self.input_signs:
        #         if s + a not in self.S_set:
        #             transition_list.append((s + a, i))

        # for w, i in transition_list:
        #     check = False
        #     for t, t_binary in self.S:
        #         if self._E_realtion(w, t):
        #             check = True
        #             break
        #     if not check:
        #         return (False, w, i)
        # return (True, "", len(self.S))

    def _extend_S(self, s):
        s_binary = []
        for e in self.E:
            s_binary.append(self.T[(s, e)])

        self.S.append((s, s_binary))
        self.S_set.add(s)

        for a in self.input_signs:
            for e in self.E:
                query_result = self._query_type1(s + a, e)
                self.T[(s + a, e)] = query_result

    def _extend_E(self, elist):
        elist_only_new = [e for e in elist if e not in self.E_set]

        for s, s_binary in self.S:

            for e in elist_only_new:
                query_result = self._query_type1(s, e)
                self.T[(s, e)] = query_result
                s_binary.append(query_result)

            for a in self.input_signs:
                for e in elist_only_new:
                    if s + a not in self.S_set:
                        self.T[(s + a, e)] = self._query_type1(s + a, e)

        self.E_set.update(elist_only_new)
        self.E.extend(elist_only_new)

    def _create_conjecture(self):
        pass

    def _process_counterexample(self, w):
        states = copy.deepcopy(self.S_set)
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
