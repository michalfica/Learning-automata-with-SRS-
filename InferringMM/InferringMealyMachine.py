import sys

# from importlib import reload
sys.path.append("../")

from utils.InferringMM import InferringMM


class InferringMealyMachine(InferringMM):
    def __init__(self, target_mm, oracle=None, debug=False):
        super().__init__(target_mm=target_mm, oracle=oracle, debug=debug)

    def _query_type1(self, w):
        # return "kurwamac!" # dlaczego się z tym zapętla ? tego  nie wiem
        if self.oracle is not None:

            ans = self.queries[w] if w in self.queries else self._ask_oracle(w)

            if ans != self.NO_ANSWER and ans == self.target_mm.route(w)[1]:
                self.queries[w] = ans
                return ans

        if w not in self.queries:
            self.cnt[0] += 1
            if self.debug and self.oracle is not None:
                print(f"zapytanie o słowo {w}")
            self.queries[w] = self.target_mm.route(w)[1]

        return self.queries[w]
