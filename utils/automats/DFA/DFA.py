from queue import Queue
from itertools import product
import random

import subprocess


class DFA:
    """
    Q                   - number of states,
    input_signs         - input alphabet,
    δ                   - transitions function (q,a) -> q'
    F                   - set of accepting states
    """

    NO_ANSWER = ""
    ACCEPT = 1
    NOT_DEFINED, SIMPLE_DFA = "not_defined", "DFA"
    RANDOM_DFA = "randomDFA"
    CONV_DFA = "convDFA"
    SYNCHRONICITY = "synchronicity"
    MARKEDWORDS = "markedwords"
    BITWISE_ADDITION = "bitwise_addition"
    AND_TYPE_PATTERN_DFA, OR_TYPE_PATTERN_DFA = "AND", "OR"
    EMPTY_STRING = ""
    NOT_RESETING_WORD = "-1"
    STATE_NOT_ACCESSIBLE = "-1"
    PARTIAL = "partial"
    INDEMPOTENT = "idempotent"

    def __init__(self, Q=0, input_signs=None, δ=None, F=None, type_=NOT_DEFINED):
        if input_signs is None:
            input_signs = []
        if δ is None:
            δ = dict()
        if F is None:
            F = set()

        self.Q = Q
        self.input_signs = input_signs
        self.output_signs = []
        self.δ = δ
        self.F = F
        self.type = type_
        self.reset_word = DFA.NOT_RESETING_WORD

        self.mapping = dict()
        self.pruned = False
        self.selectors = dict()

    def __str__(self):
        return f"DFA amount of states = {self.Q}, transitions = {self.δ}, accept states = {self.F}"

    def print_transitions(self):
        for q in range(self.Q):
            for a in self.input_signs:
                if (q, a) not in self.δ:
                    if self.pruned:
                        continue
                    assert False, "There is no such trasition in automaton!"
                print(f"({q},{a}) --> {self.δ[(q,a)]}")
        print(f"stany akceptujące - {self.F}")

    def route(self, w, q0=0, route_and_return_q=False):
        q = q0
        for a in w:
            assert (q, a) in self.δ, "There is no such trasition in automaton!"
            q = self.δ[(q, a)]
        if route_and_return_q:
            return q

        if q in self.F:
            return (w, 1)
        return (w, 0)

    def route_and_return_q(self, w, q0=0):
        q = q0
        for a in w:
            if self.pruned and (q, a) not in self.δ:
                return DFA.STATE_NOT_ACCESSIBLE

            assert (q, a) in self.δ, "There is no such trasition in automaton!"
            q = self.δ[(q, a)]
        return q

    def find_selectors(self):

        def BFS():
            visited = dict()
            Q = Queue()
            selectors = dict()

            def addToQueue(state, w):
                if not state in visited:
                    visited[state] = True
                    selectors[state] = w[1:]
                    Q.put((state, w))

            addToQueue(0, "0")
            while not Q.empty():
                q, w = Q.get()
                for a in self.input_signs:
                    if self.pruned and (q, a) not in self.δ:
                        continue
                    else:
                        addToQueue(self.δ[(q, a)], w + a)
            return selectors

        return BFS()

    def find_accepting_word(self, start_state=0):

        def BFS():
            visited = dict()
            Q = Queue()

            def addToQueue(state, w):
                if not state in visited:
                    visited[state] = True
                    Q.put((state, w))

            addToQueue(start_state, "0")
            while not Q.empty():
                q, w = Q.get()
                if q in self.F:
                    return w
                for a in self.input_signs:
                    addToQueue(self.δ[(q, a)], w + a)
            return ""

        accepted_word = BFS()
        if accepted_word == "":
            return (False, "")
        return (True, accepted_word[1:])

    """
    Retuened values:
        when automatons have different alphabets: 1 
        when automatons are equivalent: ""
        other wise : a counter example 
    """

    def equiv(self, other):

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
            assert False, "Different alphabets!"
        counterexample = BFS()
        if counterexample == "":
            return (True, "")
        return (False, counterexample[1:])

    def equiv_dfs(self, other):
        visited = dict()
        alp = []
        alp.extend([a for a in self.input_signs if a.islower()])
        alp.extend([a for a in self.input_signs if a.isupper()])

        def DFS(state, w):
            visited[state] = True
            q1, q2 = state
            if (q1 in self.F and q2 not in other.F) or (
                q1 not in self.F and q2 in other.F
            ):
                return w

            for a in alp:
                u1, u2 = self.δ[(q1, a)], other.δ[(q2, a)]
                if (u1, u2) not in visited:
                    s = DFS((u1, u2), w + a)
                    if s != "":
                        return s

            return ""

        if not self.input_signs == other.input_signs:
            assert False, "Different alphabets!"
        counterexample = DFS((0, 0), "0")
        if counterexample == "":
            return (True, "")
        return (False, counterexample[1:])

    """
    The function is given two automata and creates their convolution.

        Alphabet designation convention:
            * subset of input_signs consisting of only LOWER letters create the alphabet of the dfa1 machine,
            * subset of input_signs consisting of only UPPERCASE letters form the alphabet of the dfa2 machine.

    """

    def _compute_state_transitions_for_conv(self, dfa1, dfa2):

        def find_new_state(q, a):
            if a.isupper():
                if a.lower() not in set(dfa2.input_signs):  # add self loop
                    return self.state_mapping[(q[0], q[1])]
                return self.state_mapping[(q[0], dfa2.δ[(q[1], a.lower())])]
            else:
                if a.lower() not in set(dfa1.input_signs):  # add self loop
                    return self.state_mapping[(q[0], q[1])]
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

    def create_convolution(self, dfa1, dfa2):
        self.type = DFA.CONV_DFA
        self.Q = dfa1.Q * dfa2.Q
        self.input_signs = dfa1.input_signs + [a.upper() for a in dfa2.input_signs]
        self.state_mapping = dict()
        self._compute_state_transitions_for_conv(dfa1, dfa2)
        self.F = set([self.state_mapping[q] for q in product(dfa1.F, dfa2.F)])

    """
    A function that creates an automaton that accepts words containing patterns. There are 2 possible types:
        AND - ALL patterns specified in the 'patterns' field must appear in the word,
        OR - the word must contain AT LEAST 1 pattern specified in the 'patterns' field (except EMPTY_STRING), 
                additionally, if EMPTY_STRING appears in 'patterns', the initial state also includes the accepting states. 
    """

    def create_pattern_dfa(self, input_signs, patterns, _type=AND_TYPE_PATTERN_DFA):
        assert len(set(patterns)) == len(patterns), "All patterns must be different!"
        assert _type == DFA.OR_TYPE_PATTERN_DFA or DFA.EMPTY_STRING not in set(
            patterns
        ), "Empty string not permitted for PDdfa type AND!"

        def compute_number_of_states():
            k = 1
            for x in patterns:
                k *= len(x) + 1
            return k

        patterns.sort(key=lambda s: -len(s))
        if patterns[-1] == DFA.EMPTY_STRING:
            patterns.pop()
            self.mark_start_state_as_accepting = True
        else:
            self.mark_start_state_as_accepting = False

        self.Q = compute_number_of_states()
        self.input_signs = input_signs
        self.patterns = patterns
        self.n = len(patterns)
        self.state_mapping = dict()
        self.type = _type

        self._compute_state_transitions_for_pdfa()
        self._mark_accepting_states_for_pdfa()

    def _compute_state_transitions_for_pdfa(self):

        def find_new_state(x, a):
            words = [self.patterns[i][: x[i]] + a for i in range(self.n)]
            state = []
            for i in range(self.n):
                prefixes = set(
                    [self.patterns[i][:j] for j in range(len(self.patterns[i]) + 1)]
                )
                suffixes = [words[i][j:] for j in range(len(words[i]) + 1)]
                for s in suffixes:
                    if s in prefixes:
                        state.append(len(s) % (len(self.patterns[i]) + 1))
                        break
            for i in range(self.n):
                if x[i] == len(self.patterns[i]):
                    state[i] = x[i]

            return self.state_mapping[tuple(state)]

        xs = [range(len(x) + 1) for x in self.patterns]
        nested_loop1, nested_loop2 = product(*xs), product(*xs)

        cnt = 0
        for x in nested_loop1:
            self.state_mapping[x] = cnt
            cnt += 1
        for x in nested_loop2:
            for a in self.input_signs:
                self.δ[(self.state_mapping[x], a)] = find_new_state(x, a)

    def _mark_accepting_states_for_pdfa(self):
        if self.mark_start_state_as_accepting:
            start_state = self.state_mapping[tuple([0 for _ in range(self.n)])]
            self.F.add(start_state)

        if self.type == DFA.AND_TYPE_PATTERN_DFA:
            state = [len(x) for x in self.patterns]
            accept_state = self.state_mapping[tuple(state)]
            self.F.add(accept_state)
        elif self.type == DFA.OR_TYPE_PATTERN_DFA:
            xs = [range(len(x) + 1) for x in self.patterns]
            nested_loop = product(*xs)
            for state in nested_loop:
                for i in range(self.n):
                    if state[i] == len(self.patterns[i]):
                        self.F.add(self.state_mapping[tuple(state)])
        else:
            assert False, "Wrong type of PatternDFA, 'AND' or 'OR' type allowed only!"

    def create_random_dfa(self, Q, input_signs):
        self.Q = Q
        self.input_signs = input_signs
        self.type = DFA.RANDOM_DFA

        self.δ.clear()
        self.F.clear()

        for q in range(self.Q):
            for a in self.input_signs:
                self.δ[(q, a)] = random.randint(0, self.Q - 1)
        self.F = set(
            random.choices(
                population=range(self.Q), k=random.randint(0, (self.Q - 1) // 2)
            )
        )

    """
    A function that checks whether a given machine has a synchronization word.
    """

    def check_synchronicity(self):

        def create_product_automaton():
            dfa_ = DFA(Q=self.Q**2, input_signs=self.input_signs)

            states = product(range(self.Q), repeat=2)
            for i, (q_st, q_nd) in enumerate(states):
                for a in dfa_.input_signs:
                    q = (self.δ[(q_st, a)], self.δ[(q_nd, a)])
                    nxt_state = q[0] * self.Q + q[1]
                    dfa_.δ[(i, a)] = nxt_state
            for q in range(self.Q):
                state = q * self.Q + q
                dfa_.F.add(state)
            return dfa_

        def find_reseting_word(q1, q2):
            q = q1 * self.Q + q2
            ans, reset_word = product_dfa.find_accepting_word(start_state=q)
            return reset_word if ans else DFA.NOT_RESETING_WORD

        helpers = dict()
        product_dfa = create_product_automaton()
        for q1 in range(self.Q):
            for q2 in range(q1):
                w = find_reseting_word(q1, q2)
                if w != DFA.NOT_RESETING_WORD:
                    helpers[(q1, q2)] = w
                else:
                    return (False, DFA.NOT_RESETING_WORD)

        not_synchronized_states = [q for q in range(self.Q)]
        reset_word = ""
        while len(not_synchronized_states) > 1:
            q1 = not_synchronized_states[-1]
            q2 = not_synchronized_states[-2]
            w = helpers[(max(q1, q2), min(q1, q2))]

            reset_word += w

            xs = set()
            for q in not_synchronized_states:
                xs.add(self.route_and_return_q(w=w, q0=q))
            not_synchronized_states = list(xs)

        return (True, reset_word)

    """
    Heuristic to find short sync word
    """

    def find_sync_word_heuristic(self):
        synchronized, w = set([random.randint(0, self.Q - 1)]), ""
        while len(synchronized) < self.Q and len(w) < 35:
            largest_set = set()
            best_a = ""
            for a in self.input_signs:
                counterimage = set()
                for q in range(self.Q):
                    if self.δ[(q, a)] in synchronized:
                        counterimage.add(q)
                if len(counterimage) > len(largest_set):
                    largest_set = counterimage
                    best_a = a
            synchronized = largest_set
            w += best_a

        if len(synchronized) == self.Q:
            return (True, w[::-1])
        return (False, DFA.NOT_RESETING_WORD)

    def convert_tozyzik_format(self):
        dfa_format = ""
        dfa_format += str(len(self.input_signs)) + " " + str(self.Q) + "\n"
        for q in range(self.Q):
            for a in self.input_signs:
                dfa_format += str(self.δ[(q, a)]) + " "
        return dfa_format

    def find_minim_synch_word(self):
        dfa_format = self.convert_tozyzik_format()
        f = open("../synchrowords-main/data/dfa_format.txt", mode="w")
        f.write(dfa_format)
        f.close()

        with open("output.txt", "w") as outfile:
            subprocess.run(
                [
                    "../synchrowords-main/synchro",
                    "--config",
                    "../synchrowords-main/configs/readme_config.json",
                    "--file",
                    "../synchrowords-main/data/dfa_format.txt",
                    "-o",
                    "save.txt",
                ],
                stdout=outfile,
            )

        f = open("../synchrowords-main/save.txt")
        sync_word = DFA.NOT_RESETING_WORD
        for line in f:
            line = line.strip()
            s, e = line.find("{"), line.find("}")

            if s != -1:
                w = line[s + 1 : e]
                w = "".join(w.split())
                sync_word = "".join([self.input_signs[int(a)] for a in w])
                break

        return sync_word

    """
    A function that creates DFA self for a given machine, an machine for the language L(self)^M (marked words)
    """

    def create_marked_words_atomaton(self):
        dfa_ = DFA(Q=self.Q + 3, input_signs=self.input_signs + ["α", "β"])
        start_state = 1
        reject_state = self.Q + 1
        accept_state = self.Q + 2

        dfa_.δ[(0, "α")] = start_state
        dfa_.δ[(0, "β")] = reject_state
        for a in self.input_signs:
            dfa_.δ[(0, a)] = reject_state

        for (q, a), q_nxt in self.δ.items():
            dfa_.δ[(q + 1, a)] = q_nxt + 1

        for q in range(self.Q):
            dfa_.δ[(q + 1, "α")] = reject_state
            if q in self.F:
                dfa_.δ[(q + 1, "β")] = accept_state
            else:
                dfa_.δ[(q + 1, "β")] = reject_state

        for a in self.input_signs:
            dfa_.δ[(accept_state, a)] = reject_state
        dfa_.δ[(accept_state, "α")] = reject_state
        dfa_.δ[(accept_state, "β")] = reject_state

        for a in self.input_signs:
            dfa_.δ[(reject_state, a)] = reject_state
        dfa_.δ[(reject_state, "α")] = reject_state
        dfa_.δ[(reject_state, "β")] = reject_state

        dfa_.F = set([accept_state])
        dfa_.type = DFA.MARKEDWORDS

        return dfa_

    """
    Deletes almost all edges from transition function besides a random k edges (k in [k1, k2])
    """

    def prune(self, k1=10, k2=10):
        edges = []
        for (q, a), _ in self.δ.items():
            edges.append((q, a))

        k = random.randint(k1, k2)
        edges_to_delete = random.sample(population=edges, k=max(1, int(len(edges) - k)))
        for e in edges_to_delete:
            self.δ.pop(e, None)

        self.pruned = True

    def create_coppy_with_start_sign(self):
        dfa_ = DFA(Q=self.Q + 2, input_signs=self.input_signs + ["α"])
        start_state = 1
        reject_state = dfa_.Q - 1

        dfa_.δ[(0, "α")] = start_state
        for a in self.input_signs:
            dfa_.δ[(0, a)] = reject_state
        for a in dfa_.input_signs:
            dfa_.δ[(reject_state, a)] = reject_state

        for (q, a), q_nxt in self.δ.items():
            dfa_.δ[(q + 1, a)] = q_nxt + 1
        for q in range(self.Q):
            dfa_.δ[(q + 1, "α")] = reject_state
        dfa_.F = set([q + 1 for q in self.F])
        dfa_.type = DFA.PARTIAL
        return dfa_

    """
    Returns a random automaton that is indempotent due to transitions after the 'letter' character
    """

    def create_random_indempotent_automaton(self, Q, input_signs, letter="a"):
        self.create_random_dfa(Q=Q, input_signs=input_signs)
        self.type = DFA.INDEMPOTENT
        states = [q for q in range(self.Q)]
        random.shuffle(states)

        while len(states) > 0:
            q1 = states.pop()
            q2 = states.pop() if len(states) > 0 else q1

            self.δ[(q1, letter)] = q2
            self.δ[(q2, letter)] = q2

    """
    Checks whether a given machine is indempotent due to the 'letter' character
    """

    def check_if_idempotent(self, letter="a"):
        for q1 in range(self.Q):
            q2 = self.δ[(q1, letter)]
            if self.δ[(q2, letter)] != q2:
                return False
        return True
