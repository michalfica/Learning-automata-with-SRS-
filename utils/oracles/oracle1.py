from queue import Queue


"""klasa implementująca więzy:
 SYSTEM PRZEPISYWANIA SŁÓW, reguła: ZAMIEŃ SĄSIEDNIE LITERY"""


class Oracle1:

    NO_ANSWER = ""

    def __init__(self):
        pass

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
            return Oracle1.NO_ANSWER

        result = BFS()
        return result

    def get_adjacents(self, w):
        s = set()
        for i in range(len(w) - 1):
            t = "".join(w[:i]) + w[i + 1] + w[i] + w[i + 2 :]
            s.add(t)
        return s
