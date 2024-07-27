import numpy as np


class MealyMachine:
    """konwencja:
    Q                   - liczba stanów maszyny,
    input, output_signs - alfabet wejściowy/wyjściowy jako lista?
    λ                   - funkcja (q,a) -> a (jaką literke wypisać przy danym przejściu), jako słownik
    δ                   - funkcja (q,a) -> q'(funkcja przejścia automatu), jako słownik
    """

    def __init__(self, Q=0, input_signs=None, output_signs=None, λ=dict(), δ=dict()):
        self.Q = Q
        self.input_signs = sorted(input_signs)  # sortowanie by móc porównywac
        self.output_signs = sorted(output_signs)
        self.λ = λ
        self.δ = δ

    def __str__(self):
        return f"Mealy Machine amount of states = {self.Q}, I = {self.input_signs}, O = {self.output_signs}"

    def random_route(self, n=10):
        w, v, q = "".join(np.random.choice(self.input_signs, n, replace=True)), "", 0
        for a in w:
            v += self.λ[(q, a)]
            q = self.δ[(q, a)]
        return (w, v)

    def print_transitions(self):
        for q in range(self.Q):
            for a in self.input_signs:
                assert (q, a) in self.λ and (
                    q,
                    a,
                ) in self.δ, (
                    "nie ma taiego przejścia w maszynie, potencjalnie zły alfabet!"
                )
                print(f"({q},{a}) --> '{self.λ[(q,a)]}',{self.δ[(q,a)]}")

    # TO DO: NIE WIEM JAK SPRAWDZAĆ RÓWNOWAŻNOŚĆ DWÓCH STANÓW (żęby sie nie zapętlać w ∞)
    # def __eq__(self, other):
    #     if not (
    #         self.input_signs == other.input_signs
    #         and self.output_signs == other.output_signs
    #     ):
    #         return 1  # nie zgadzaja sie alfabety wiec na pewno nie są równoważne

    #     def state_equivalance(q1, q2):
    #         for a in self.input_signs:
    #             if not (
    #                 self.λ[(q1, a)] == other.λ[(q2, a)]
    #                 and state_equivalance(self.δ[(q1, a)], other.δ[(q2, a)])
    #             ):
    #                 return False
    #         return True

    #     return state_equivalance(0, 0)
