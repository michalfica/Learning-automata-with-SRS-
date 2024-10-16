from queue import Queue
import copy
import re

"""klasa implementująca więzy:
SYSTEM PRZEPISYWANIA SŁÓW"""


class OracleProf:
    NO_ANSWER = ""

    def __init__(self, pi):
        def check_permissible(xs):
            for l, r in xs:
                if len(l) < len(r):
                    return False
            return True

        assert check_permissible(pi), "Niedopuszczalny system! Można tylko skracać!"
        self.pi = pi

    """sprawdza czy odpowieć o należenie słowa 'w' do języka można wywnioskować 
    na podstawie zbioru słów, o krórych już wiem czy należą do języka ('answers')"""

    def ask_oracle(self, w, answers):
        def BFS():
            visited = dict()
            Q = Queue()

            def addToQueue(state):
                if not state in visited:
                    visited[state] = True
                    Q.put(state)

            addToQueue(w)
            while not Q.empty():
                q = Q.get()

                if q in answers:
                    return answers[q]

                adjacents = self.get_adjacents(q)
                for t in adjacents:
                    addToQueue(t)
            return OracleProf.NO_ANSWER

        result = BFS()
        return result

    def get_adjacents(self, w):
        s = set()
        for l, r in self.pi:
            find_all = [i.start() for i in re.finditer("(?=" + l + ")", w)]
            for i in find_all:
                t = "".join(w[:i]) + copy.deepcopy(r) + w[i + len(l) :]
                s.add(t)
        return s
