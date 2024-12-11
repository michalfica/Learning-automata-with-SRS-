from utils.automats.DFA.DFA import DFA
import copy
from itertools import product

from queue import Queue

"""Automat, który jest splotem dwóch automatów"""


class convDFA(DFA):
    """
    Dwa rodzaje konstrukci:
    (1) dane dwa automaty, tworzę ich splot,
    (2) dany odrazu splot 'pewnych' dwóch automatów.

    Konwencja dotycząca alfabetu:
        * pozdbiór input_signs zawierający tylko MAŁE litery tworzy alfabet jednego automatu (ze splotu)
        * pozdbiór input_signs zawierający tylko WIELKIE litery tworzy alfabet drugiego automatu (ze splotu)

    """

    def __init__(self, *args, **kwargs):
        if kwargs.get("type") == "dfa":
            super().__init__(
                Q=kwargs.get("Q"),
                input_signs=kwargs.get("input_signs"),
                F=kwargs.get("F"),
            )
            self.type = "dfa"
        elif kwargs.get("type") == "conv":
            dfa1, dfa2 = kwargs.get("dfa1"), kwargs.get("dfa2")
            input_signs_ = dfa1.input_signs + [a.upper() for a in dfa2.input_signs]

            super().__init__(Q=dfa1.Q * dfa2.Q, input_signs=input_signs_)
            self.type = "conv"
            self.state_mapping = dict()
            self._compute_state_transitions(dfa1, dfa2)
            self.F = copy.deepcopy(
                set([self.state_mapping[q] for q in product(dfa1.F, dfa2.F)])
            )
        else:
            assert False, "coś nie tak z argumentami do konstruktora !"

    def _compute_state_transitions(self, dfa1, dfa2):
        def find_new_state(q, a):
            if a.isupper():
                return self.state_mapping[(q[0], dfa2.δ[(q[1], a.lower())])]
            else:
                return self.state_mapping[(dfa1.δ[(q[0], a)], q[1])]

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

    """
    zwracane wartości:
        1  -> różne alfabety obu maszyn
        "" -> maszyny równoważne
        s  -> słowo rozróżniające automaty
    """

    def equiv(self, other):
        visited = dict()
        alp = []
        alp.extend([a for a in self.input_signs if a.islower()])
        alp.extend([a for a in self.input_signs if a.isupper()])

        print(f"alp = {alp}")

        def DFS(state, w):
            visited[state] = True

            print(f"state = {state}, w = {w}")

            q1, q2 = state
            if (q1 in self.F and q2 not in other.F) or (
                q1 not in self.F and q2 in other.F
            ):

                print(f"zwracam kontrprzykład = {w}")

                return w

            for a in alp:
                u1, u2 = self.δ[(q1, a)], other.δ[(q2, a)]
                if (u1, u2) not in visited:
                    s = DFS((u1, u2), w + a)
                    if s != "":
                        return s

            return ""

        if not self.input_signs == other.input_signs:
            assert (
                False
            ), "automaty pracują na różnych alfabetach - nie moga być równoważne!"
        counterexample = DFS((0, 0), "0")

        print(f"kontrprzykład to {counterexample}")

        if counterexample == "":
            return (True, "")
        return (False, counterexample[1:])

    def equiv_(self, other):
        def BFS():
            visited = dict()
            Q = Queue()

            def addToQueue(state, w):
                if not state in visited:
                    visited[state] = True
                    Q.put((state, w))

            addToQueue((0, 0), "0")
            while not Q.empty():
                item = Q.get()
                q1, q2, w = item[0][0], item[0][1], item[1]
                if (q1 in self.F and q2 not in other.F) or (
                    q1 not in self.F and q2 in other.F
                ):
                    return w
                for a in self.input_signs:
                    addToQueue((self.δ[(q1, a)], other.δ[(q2, a)]), w + a)
            return ""

        if not self.input_signs == other.input_signs:
            assert (
                False
            ), "automaty pracują na różnych alfabetach - nie moga być równoważne!"
        counterexample = BFS()

        print(f"zwracam kontrprzykład = {counterexample}")
        if counterexample == "":
            return (True, "")
        return (False, counterexample[1:])
