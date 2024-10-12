from InferringDFA import InferringDFA
from utils.DFA import DFA
from utils.convDFA import convDFA
import copy

"""
    Osobna klasa na czenie się splotu 2 DFA.
    Z powodu, że alfabet dla convDFA składa się z liter, które są dwuznakowe np 'a1' lub 'b2', 
    troche inaczej musze przetwarzać kontrprzykład - grupować literki w słowie po dwie.
    i jako hipoteze muszę zwrócić convDFA
"""


class InferringconvDFA(InferringDFA):
    def __init__(self, target, oracle=None, debug=False):
        super().__init__(target=target, oracle=oracle, debug=debug)

    def _process_counterexample(self, w):
        w = [
            w[i : i + 2] for i in range(0, len(w), 2)
        ]  # <- jedyna ważna nowa linika, potencjalnie można ją dodać do Inferring, a 2 zparametryzować

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

    def _create_conjecture(self):
        def _equivalent_in_S(s):
            for i, t in enumerate(self.S):
                if self._E_realtion(s, t):
                    return i

        conjecture = convDFA(
            type="dfa", Q=len(self.S), input_signs=self.input_signs, F=set()
        )
        for i, s in enumerate(self.S):
            for a in self.input_signs:
                conjecture.δ[(i, a)] = _equivalent_in_S(s + a)
            if self.T[(s, "")] == DFA.ACCEPT:
                conjecture.F.add(i)
        return copy.deepcopy(conjecture)
