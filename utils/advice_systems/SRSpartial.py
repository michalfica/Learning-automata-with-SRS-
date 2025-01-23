# from advice_system1 import advice_system1
from importlib import reload
import utils.advice_systems.SRS as SRS

reload(SRS)

from utils.advice_systems.SRS import SRS
from utils.automats.DFA.DFA import DFA


class SRSpartial(SRS):

    def __init__(self, alphabet, partial_dfa):
        pi = []
        state_to_selsector = partial_dfa.find_selectors()
        selectors = [u for _, u in state_to_selsector.items()]

        self.partial_dfa = partial_dfa
        self.state_to_selector = state_to_selsector

        for u in selectors:
            for a in alphabet:
                if u + a in set(selectors):
                    continue
                q = partial_dfa.route_and_return_q(u + a)
                if q == DFA.STATE_NOT_ACCESSIBLE:
                    continue
                pi.append(("α" + u + a, "α" + state_to_selsector[q]))

        for a in alphabet:
            pi.append((a + "α", "αα"))
        for a in alphabet + ["α"]:
            pi.append(("αα" + a, "αα"))
        self.pi = pi
