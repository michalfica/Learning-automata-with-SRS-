from importlib import reload
import Mealymachine

reload(Mealymachine)
from Mealymachine import MealyMachine


class InferringMM:
    def __init__(self, target_mm):
        self.target_mm = target_mm
        self.input_signs = self.target_mm.input_signs
        self.output_signs = self.target_mm.output_signs
        self.S = set()
        self.E = set()
        self.T = dict()
        self.cnt = [0, 0]

    def run(self):
        debug_k = 0
        # 1 krok inicljalizacja
        self._extend_E(self.input_signs)
        self._extend_S("")

        print(f"poczatkowo tabela obserwacji:")
        print(f"S : {self.S}")
        print(f"E : {self.E}")
        print(f"T :")
        for key, value in self.T.items():
            print(f"key={key}, value={value}")
        # 2 krok:
        while True:
            debug_k += 1
            print("sprawdzam czy zamnkieta")
            check, x = self._closed()
            while check == False:
                print(f"nie jest zamknieta - {x}")
                self._extend_S(x)
                check, x = self._closed()
            print(f"S : {self.S}")
            print(f"E : {self.E}")

            print(f"tworze hipoteze")
            conjecture = self._create_conjecture()
            conjecture.print_transitions()
            check, x = self._query_type2(conjecture)

            if check == False:
                print(f"nie jest dobra - {x}")
                self._process_counterexample(x)
                print(f"tabela obserwacji, po zobaczeniu kontrprzykładu:")
                print(f"S : {self.S}")
                print(f"E : {self.E}")
                print(f"T :")
                for key, value in self.T.items():
                    print(f"key={key}, value={value}")
            else:
                return (conjecture, self.cnt)
            print("\n\n")
            # if debug_k >= 3:
            #     return (MealyMachine(), [0, 0])

    def _E_realtion(self, s, t):
        for e in self.E:
            if self.T[(s, e)] != self.T[(t, e)]:
                return False
        return True

    def _query_type1(self, w):
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

        # DO POPRAWY !!! znajdowanie maxsymalnego prefiksu który jest prefiksem
        states = set(self.S)
        print(f"states = {states}, w = {w}")

        max_pref = ""
        idx = -1
        for a in w:
            if max_pref + a in states:
                max_pref += a
                idx += 1
            else:
                break

        print(f"max_prefiks = {max_pref}, zaczyna sie w {idx}")
        w = w[::-1]
        if idx != -1:
            w = w[: -(idx + 1)]

        suffixes, suffix = [], ""
        for a in w:
            suffix = a + suffix
            suffixes.append(suffix)
        print(f"ddodaje do E {suffixes} po popatrzeniu na kontrprzykład")
        self._extend_E(suffixes)
