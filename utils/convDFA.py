from DFA import DFA
import copy
from itertools import product

"""Automat, który jest splotem dwóch automatów"""


class convDFA(DFA):
    def __init__(self, dfa1, dfa2):
        input_signs_ = [a + "1" for a in dfa1.input_signs] + [
            a + "2" for a in dfa2.input_signs
        ]
        super().__init__(Q=dfa1.Q * dfa2.Q, input_signs=[])
        self.input_signs = input_signs_
        self.state_mapping = dict()
        self._compute_state_transitions(dfa1, dfa2)
        self.F = copy.deepcopy(
            set([self.state_mapping[q] for q in product(dfa1.F, dfa2.F)])
        )

    def _compute_state_transitions(self, dfa1, dfa2):
        def find_new_state(q, a):
            symbol_type = a[-1]
            if symbol_type == "1":
                return self.state_mapping[(dfa1.δ[(q[0], a[:-1])], q[1])]
            elif symbol_type == "2":
                return self.state_mapping[(q[0], dfa2.δ[(q[1], a[:-1])])]
            else:
                print(f"symbol_type = {symbol_type}")
                assert (
                    False
                ), "zły alfabet! dopuszczam tylko literki zakoczone '1' lub '2'"

        nested_loop1, nested_loop2 = product(range(dfa1.Q), range(dfa2.Q)), product(
            range(dfa1.Q), range(dfa2.Q)
        )

        cnt = 0
        for x in nested_loop1:
            self.state_mapping[x] = cnt
            cnt += 1
        for x in nested_loop2:
            for a in self.input_signs:
                self.δ[(self.state_mapping[x], a)] = find_new_state(x, a)

    def route(self, w):
        assert len(w) % 2 == 0, "splot przyjmuje tylko słowa parzystej długości!"

        # print(f"pronuje sprawdzić słowo = {w}")
        q = 0
        letter = ""
        for i, a in enumerate(w):
            if i % 2 == 0:
                letter = a
            else:
                letter += a
                # print(f"odpytka o przejsci {q}, {letter}")
                assert (q, letter) in self.δ, "nie ma takie przejścia w maszynie!"
                q = self.δ[(q, letter)]
        if q in self.F:
            return (w, 1)
        return (w, 0)
