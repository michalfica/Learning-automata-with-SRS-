import sys

from importlib import reload

sys.path.append("../")

import utils.Inferring

reload(utils.Inferring)
from utils.Inferring import Inferring

import utils.Mealymachine as Mealymachine
from utils.Mealymachine import MealyMachine


class InferringDFA(Inferring):
    def __init__(self, target_mm, oracle=None, debug=False):
        super().__init__(target_mm=target_mm, oracle=oracle, debug=debug)

    def initialization(self):
        pass

    def _query_type1(self, w):
        pass

    def create_conjecture(self):
        pass
