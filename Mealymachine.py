class MealyMachine:
    def __init__(self):
        self.Q = {}
        self.input_signs = {}
        self.output_signs = {}
        self.α = dict()
        self.δ = dict()

    def __str__(self):
        return f"I = {self.input_signs}, O = {self.output_signs}"
    
    # TO DO:
    # def _print(self)        <- wypisać krawędzie maszyny jakoś zgrabnie (albo jak kolwiek)
    # 
    # def __eq__(self, other) <- sprawdzić czy dwie maszyny są równoważne, (sprawdzając czy stany poczatkowe są, zgodnie z reguła)  

