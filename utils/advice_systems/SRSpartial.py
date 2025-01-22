# from advice_system1 import advice_system1
from importlib import reload
import utils.advice_systems.SRS as SRS

reload(SRS)

from utils.advice_systems.SRS import SRS
from utils.automats.DFA.DFA import DFA

"""klasa implementująca więzy:
 SYSTEM PRZEPISYWANIA SŁÓW, reguła: Alpha w Betha"""


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
                # print(f"dodaje regule: {u + a} -> {state_to_selsector[q]}")
                pi.append(("α" + u + a, "α" + state_to_selsector[q]))

        for a in alphabet:
            pi.append((a + "α", "αα"))
        for a in alphabet + ["α"]:
            pi.append(("αα" + a, "αα"))
        self.pi = pi

    """
    zakładam ze slowa w sa nad alfabetem, który ma wsobie znak 'α' 
    """

    # def get_normal_form(self, w):
    #     l = w.rfind("α")
    #     if l == -1:
    #         return w
    #     if l > 0:
    #         return "αα"

    #     print(f"w = {w}")

    #     q, length = 0, 0
    #     for i in range(len(w) - 1):
    #         nxt_q = self.partial_dfa.route_and_return_q(w[1 : i + 1])
    #         if nxt_q == DFA.STATE_NOT_ACCESSIBLE:
    #             break
    #         q = nxt_q
    #         length = i + 1
    #     print(f"length = {length}, q = {q}")
    #     print(
    #         f"podział w  = {w[0]}, {w[1:1+length]}, {w[1+length:]} q = {q}, selsctor = {self.state_to_selector[q]}"
    #     )
    #     return "α" + self.state_to_selector[q] + w[1 + length :]
