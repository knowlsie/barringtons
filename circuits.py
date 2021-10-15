from collections import Counter
from itertools import combinations
from groups import *
from pprint import pprint

id_counter = 0
class Gate(object):
    def __init__(self, in_gates, visited=False, name=None):
        global id_counter
        self.in_gates = in_gates
        self.__visited = visited
        if name is None:
            self.name = f'Gate{id_counter}'
            id_counter += 1
        else:
            self.name = name

    def __str__(self):
        l = [g.name for g in self.in_gates]
        return f'{self.name}{l}'

    def __mark_visited(self, boolean):
        if self.__visited == boolean:
            return
        else:
            self.__visited = boolean
            for gate in self.in_gates:
                gate.__mark_visited(boolean)

    def size(self, recurse=False):
        if not recurse:
            self.__mark_visited(False)

        if not self.__visited:
            self.__visited = True
            s = 1 + sum([g.size(recurse=True) for g in self.in_gates])
            # print(self, type(self))
            return s
        else:
            return 0

    def gate_to_and_not(self):
        raise NotImplementedError()

    def gate_to_alpha_program(self, subprograms):
        raise NotImplementedError()

    def circuit_to_and_not(self, recurse=False):
        if not recurse:
            self.__mark_visited(False)

        if not self.__visited:
            self.__visited = True
            self.in_gates = [g.circuit_to_and_not(recurse=True) for g in self.in_gates]
            self.__memo = self.gate_to_and_not()

        return self.__memo

    def circuit_to_alpha_program(self, recurse=False):
        global total
        if not recurse:
            total = 0
            self.__mark_visited(False)

        if not self.__visited:
            subprograms = [g.circuit_to_alpha_program(recurse=True) for g in self.in_gates]
            total += 1
            # print(total, self.name)
            self.__visited = True
            self.__memo = self.gate_to_alpha_program(subprograms)

        return self.__memo.copy()

class And(Gate):
    def evaluate(self, x: str):
        assert len(self.in_gates) == 2
        answer = (self.in_gates[0].evaluate(x) and self.in_gates[1].evaluate(x))
        # print(self, answer)
        return answer

    def gate_to_and_not(self):
        return self

    def gate_to_alpha_program(self, subprograms):
        assert len(subprograms) == 2
        sub0 = subprograms[0]
        sub1 = subprograms[1]
        sub1.convert_from_beta_to_alpha(ALPHA, BETA)
        sub0_inv = sub0.copy()
        sub1_inv = sub1.copy()
        sub0_inv.convert_from_beta_to_alpha(ALPHA, ALPHA_INV)
        sub1_inv.convert_from_beta_to_alpha(BETA, BETA_INV)
        program = GroupProgram(
            sub0.instructions + sub1.instructions + sub0_inv.instructions + sub1_inv.instructions,
            alpha = COMMUTATOR
        )
        program.convert_from_beta_to_alpha(COMMUTATOR, ALPHA)
        return program
        
class Or(Gate):
    def evaluate(self, x: str):
        assert len(self.in_gates) == 2
        answer = (self.in_gates[0].evaluate(x) or self.in_gates[1].evaluate(x))
        # print(self, answer)
        return answer

    def gate_to_and_not(self):
        return Not([And(
                [Not([self.in_gates[0]], visited=True), 
                Not([self.in_gates[1]], visited=True)], visited=True)], 
            visited=True, name=f'converted-{self.name}')

    def gate_to_alpha_program(self, subprograms):
        sub0 = Not.gate_to_alpha_program(self, [subprograms[0]])
        sub1 = Not.gate_to_alpha_program(self, [subprograms[1]])
        sub1.convert_from_beta_to_alpha(ALPHA, BETA)
        sub0_inv = sub0.copy()
        sub1_inv = sub1.copy()
        sub0_inv.convert_from_beta_to_alpha(ALPHA, ALPHA_INV)
        sub1_inv.convert_from_beta_to_alpha(BETA, BETA_INV)
        program = GroupProgram(
            sub0.instructions + sub1.instructions + sub0_inv.instructions + sub1_inv.instructions,
            alpha = COMMUTATOR
        )
        program.convert_from_beta_to_alpha(COMMUTATOR, ALPHA)
        program = Not.gate_to_alpha_program(self, [program])
        return program
    
class Not(Gate):
    def evaluate(self, x: str):
        assert len(self.in_gates) == 1
        ingate = self.in_gates[0]
        answer = (not ingate.evaluate(x))
        # print answer
        return answer

    def gate_to_and_not(self):
        return self

    def gate_to_alpha_program(self, subprograms):
        assert len(subprograms) == 1
        subprogram = subprograms[0]
        last_instruction = subprogram.instructions[-1]
        replacement_instruction = GroupInstruction(
            last_instruction.index,
            last_instruction.g0 * ALPHA_INV,
            last_instruction.g1 * ALPHA_INV
        )
        subprogram.instructions[-1] = replacement_instruction
        subprogram.alpha = ALPHA_INV
        subprogram.convert_from_beta_to_alpha(ALPHA_INV, ALPHA)
        return subprogram

class Input(Gate):
    def __init__(self, index, visited=False, name=None):
        self.index = index
        if name is None:
            name = str(self.index)
        super(Input, self).__init__([], visited=visited, name=name)

    def evaluate(self, x: str):
        assert x[self.index] == '0' or x[self.index] == '1'
        return (x[self.index] == '1')
        
    def gate_to_and_not(self):
        return self

    def gate_to_alpha_program(self, subprograms):
        assert len(subprograms) == 0
        instructions = [GroupInstruction(self.index, IDENTITY, ALPHA)]
        return GroupProgram(instructions, alpha=ALPHA)

class TrueGate(Gate):
    def __init__(self, visited=False, name='True'):
        super(TrueGate, self).__init__([], visited=visited, name=name)

    def evaluate(self, x: str):
        return True
    
    def gate_to_and_not(self):
        return self

    def gate_to_alpha_program(self, subprograms):
        assert len(subprograms) == 0
        instructions = [GroupInstruction(0, ALPHA, ALPHA)]
        return GroupProgram(instructions, alpha=ALPHA)

class FalseGate(Gate):
    def __init__(self, visited=False, name='False'):
        super(FalseGate, self).__init__([], visited=visited, name=name)

    def evaluate(self, x: str):
        return False
    
    def gate_to_and_not(self):
        return self

    def gate_to_alpha_program(self, subprograms):
        assert len(subprograms) == 0
        instructions = [GroupInstruction(0, IDENTITY, IDENTITY)]
        return GroupProgram(instructions, alpha=ALPHA)


def maj3(inps, name=None):
    if name is not None:
        a1 = And((inps[0], inps[1]), name=f'{name}-a1')
        a2 = And((inps[1], inps[2]), name=f'{name}-a2')
        a3 = And((inps[0], inps[2]), name=f'{name}-a3')
        o1 = Or((a1, a2), name=f'{name}-o1')
        o2 = Or((o1, a3), name=f'{name}-o2')
    else:
        a1 = And((inps[0], inps[1]))
        a2 = And((inps[1], inps[2]))
        a3 = And((inps[0], inps[2]))
        o1 = Or((a1, a2))
        o2 = Or((o1, a3), name=name)
    return o2

def make_maj3(indices=None):
    if not indices:
        indices = list(range(3))
    
    inps = [Input(i) for i in indices]
    return maj3(inps)

def maj5(inps, name=None):
    ands = []
    for c in combinations(inps, 3):
        c1, c2, c3 = c
        a1 = And((c1, c2))
        a2 = And((a1, c3))
        ands.append(a2)

    ors_1 = []
    for i in range(0, 10, 2):
        ors_1.append(Or((ands[i], ands[i+1])))
    assert len(ors_1) == 5
    
    ors_2 = []
    ors_2.append(Or((ors_1[0], ors_1[1])))
    ors_2.append(Or((ors_1[2], ors_1[3])))

    o3 = Or((ors_2[0], ors_1[4]))
    o4 = Or((o3, ors_2[1]), name=name)

    return o4

def make_maj5(indices=None):
    if not indices:
        indices = list(range(5))

    inps = [Input(i) for i in indices]
    return maj5(inps)

def make_majk(k, indices=None):
    # makes majk, but not using the correct construction for Barrington's Theorem.
    # it turns out the constants on that construction are way too high, at least
    # for small numbers. this uses a much simpler method which grows polynomially,
    # but has much better constants, so works for small numbers here.
    if not indices:
        indices = list(range(k))
    
    # # some fun old code for maj7. it's too deep, so is VERY slow.
    # maj_51 = make_maj5((indices[0], indices[1], indices[2], indices[3], indices[4]))
    # maj_52 = make_maj5((indices[0], indices[1], indices[4], indices[5], indices[6]))
    # maj_53 = make_maj5((indices[0], indices[2], indices[3], indices[5], indices[5]))
    # maj_54 = make_maj5((indices[1], indices[2], indices[2], indices[4], indices[5]))
    # maj_55 = make_maj5((indices[1], indices[3], indices[4], indices[6], indices[6]))

    # maj_final = maj5((maj_51, maj_52, maj_53, maj_54, maj_55))
    # return maj_final

    to_or = []
    for c in combinations(indices, (k+1) // 2):
        to_and = [Input(ci) for ci in c]
        while len(to_and) > 1:
            if len(to_and) % 2 == 1:
                a1 = to_and.pop()
                a2 = to_and.pop()
                a3 = And((a1, a2))
                to_and.append(a3)
            else:
                new_to_and = []
                for i in range(0, len(to_and), 2):
                    new_to_and.append(And((to_and[i], to_and[i+1])))
                to_and = new_to_and
        to_or.append(to_and[0])
    
    while len(to_or) > 1:
        if len(to_or) % 2 == 1:
            o1 = to_or.pop()
            o2 = to_or.pop()
            o3 = Or((o1, o2))
            to_or.append(o3)
        else:
            new_to_or = []
            for i in range(0, len(to_or), 2):
                new_to_or.append(Or((to_or[i], to_or[i+1])))
            to_or = new_to_or

    return to_or[0]

def make_majk2(k, indices=None):
    if not indices:
        indices = list(range(k))

    t = TrueGate()
    f = FalseGate()
    layers = [[] for i in range(k)]
    layers[0] = [t, Input(k - 1), f]
    for i in range(1, k):
        for j in range((i + 1) if (i < (k + 1) // 2) else (k - i)):
            layers[i].append(
                maj3([layers[i-1][j], layers[i-1][j+1], Input(k - 1 - i)], name=f'maj3-{i}-{j}')
            )
        if i < (k + 1) // 2 - 1:
            layers[i].insert(0, t)
            layers[i].append(f)

    return layers[k - 1][0]