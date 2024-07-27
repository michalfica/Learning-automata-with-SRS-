class MealyMachine:
    """konwencja:
    Q                   - liczba stanów maszyny,
    input, output_signs - alfabet wejściowy/wyjściowy jako lista?
    λ                   - funkcja (q,a) -> a (jaką literke wypisać przy danym przejściu), jako słownik
    δ                   - funkcja (q,a) -> q'(funkcja przejścia automatu), jako słownik
    """

    def __init__(self, Q=0, input_signs=None, output_signs=None, λ=dict(), δ=dict()):
        self.Q = Q
        self.input_signs = input_signs
        self.output_signs = output_signs
        self.λ = λ
        self.δ = δ

    def __str__(self):
        return f"I = {self.input_signs}, O = {self.output_signs}"

    def print_transitions(self):
        for q in range(self.Q):
            for a in self.input_signs:
                print(f"({q},{a}) --> '{self.λ[(q,a)]}',{self.δ[(q,a)]}")

    # TO DO:
    # def _print(self)        <- wypisać krawędzie maszyny jakoś zgrabnie (albo jak kolwiek)
    #
    # def __eq__(self, other) <- sprawdzić czy dwie maszyny są równoważne, (sprawdzając czy stany poczatkowe są, zgodnie z reguła)
