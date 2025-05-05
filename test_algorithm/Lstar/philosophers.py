from itertools import product
import copy

N = 3
P_STATES = [
    "idle",
    "grabL",
    "grabR",
    "grabLR",
    "grabRL",
    "eating",
    "putR",
    "putL",
    "error",
]
SUCCESSORS = {
    "grabR": "grabRL",
    "grabL": "grabLR",
    "grabRL": "eating",
    "grabLR": "eating",
    "eating": "putR",
    "putR": "putL",
    "putL": "idle",
    "error": "error",
}


def one_ph_states(i):
    return [(state, i) for state in P_STATES]


def all_ph_states(n):
    philosophers = [P_STATES for i in range(1, n + 1)]
    return product(memory_states(n), *philosophers)


def grab_fork(mem, k):
    mem = list(mem)
    if mem[k] == 1:
        return None
    mem[k] = 1
    return tuple(mem)


def put_fork(mem, k):
    mem = list(mem)
    mem[k] = 0
    return tuple(mem)


def memory_states(n):
    return product(*([[0, 1]] * n))


def error_state(n):
    return tuple([tuple([0] * n)] + ["error"] * n)


def state_action_pre(state, letter, n):
    k = letter[1]

    if letter[0] == "think":
        return state, ("thinking", k)

    if state[1] == "error":
        return error_state(n), "Error"

    if letter[0] == "eat" and state[k] == "idle":
        new_state = list(state)

        output = ("get first fork", k)

        if k < n:
            new_state[k] = "grabL"
            if state[0][k - 1] == 1:
                return (state, "waiting")

            new_state[0] = grab_fork(state[0], k - 1)
        else:
            new_state[k] = "grabR"
            if state[0][0] == 1:
                return (state, "waiting")

            new_state[0] = grab_fork(state[0], 0)

        new_state = tuple(new_state)

        return (new_state, output)

    output = ""

    if letter[0] == "eat" and state[k] != "idle":
        new_state = list(state)
        new_state[k] = SUCCESSORS[state[k]]

        if new_state[k] == "grabLR":
            if state[0][0] == 1:
                return (state, "waiting")

            new_state[0] = grab_fork(state[0], k % n)
            output = ("get second fork", k)

        if new_state[k] == "grabRL":
            if state[0][0] == 1:
                return (state, "waiting")

            new_state[0] = grab_fork(state[0], k - 1)
            output = ("get second fork", k)

        if new_state[k] == "eating":
            output = ("eating", k)

        if new_state[k] == "putR":
            output = ("put second fork", k)
            new_state[0] = put_fork(state[0], k - 1)

        if new_state[k] == "putL" and k < n:
            output = ("put first fork", k)
            new_state[0] = put_fork(state[0], k)

        if new_state[k] == "putL" and k == n:
            output = ("put first fork", k)
            new_state[0] = put_fork(state[0], 0)

    new_state = tuple(new_state)
    return new_state, output


def state_action(state, letter, n):
    new_state, output = state_action_pre(state, letter, n)
    if new_state[0] is None:
        return error_state(n), "Error"

    return new_state, output


input_alphabet = [(act, i) for act, i in product(["think", "eat"], range(1, N + 1))]

states = all_ph_states(N)

# transitions = [(state,letter,*state_action(state,letter,N)) for state, letter in product(states, input_alphabet)]

# print(len(transitions))

# transitions_dict = {(state,letter): (new_state,output) for (state,letter,new_state,output) in transitions}


def dfs(transitions, inputs, n):
    visited = []
    queue = [tuple([tuple([0] * n)] + ["idle"] * n)]

    while len(queue) > 0:
        node = queue.pop(0)

        if node not in visited:
            visited.append(node)
            for letter in inputs:
                queue.append(state_action(node, letter, n)[0])

    return visited


reachable_states = dfs({}, input_alphabet, N)

transitions = [
    (state, letter, *state_action(state, letter, N))
    for state in reachable_states
    for letter in input_alphabet
]
transitions_dict = {
    (state, letter): (new_state, output)
    for (state, letter, new_state, output) in transitions
}


# print((transitions))

import string

number_of_states = 0
states_mapping = dict()

input_alphabet_size = 0
in_alphabet = dict()
output_alphabet_size = 0
out_alphabet = dict()

for t in transitions:
    if t[0] not in states_mapping:
        states_mapping[t[0]] = number_of_states
        number_of_states += 1
    if t[2] not in states_mapping:
        states_mapping[t[2]] = number_of_states
        number_of_states += 1

    if "".join([str(x) for x in t[1]]) not in input_alphabet:
        input_alphabet["".join([str(x) for x in t[1]])] = string.ascii_lowercase[
            input_alphabet_size
        ]
        input_alphabet_size += 1

    if "".join([str(x) for x in t[3]]) not in out_alphabet:
        out_alphabet[("".join([str(x) for x in t[3]]))] = output_alphabet_size
        output_alphabet_size += 1

    print(
        str(states_mapping[t[0]]),
        input_alphabet["".join([str(x) for x in t[1]])],
        str(states_mapping[t[2]]),
        str(out_alphabet["".join([str(x) for x in t[3]])]),
    )

    # print(
    #     'from("q'
    #     + str(states_mapping[t[0]])
    #     + "\").on('"
    #     + input_alphabet["".join([str(x) for x in t[1]])]
    #     + "').withOutput('"
    #     + str(states_mapping[t[2]])
    #     + "').to(\"q"
    #     + str(output_alphabet["".join([str(x) for x in t[3]])])
    #     + '").'
    # )

print("number_of_states = ", number_of_states)
print(in_alphabet)
print(out_alphabet)

for k, v in states_mapping.items():
    print(k, v)

# from("q0").on('a').withOutput('1').to("q1")
# print(dfs(transitions_dict, input_alphabet, N))
