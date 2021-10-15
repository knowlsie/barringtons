from sympy.combinatorics import Permutation, Cycle
from sympy.combinatorics.named_groups import SymmetricGroup

S5 = SymmetricGroup(5)
S5_elems = list(S5.generate_schreier_sims())
IDENTITY = Permutation(4)
ALPHA = Permutation(Cycle(0,1,2,3,4))
BETA = Permutation(Cycle(0,2,4,3,1))
ALPHA_INV = (~ALPHA)
BETA_INV = (~BETA)
COMMUTATOR = ALPHA * BETA * ALPHA_INV * BETA_INV
ELEMENTS = [ALPHA, ALPHA_INV, BETA, BETA_INV, COMMUTATOR]
CONJUGATORS = {e: {} for e in ELEMENTS}

for e1 in ELEMENTS:
    for e2 in ELEMENTS:
        for gamma in S5_elems:
            if gamma * e1 * (~gamma) == e2:
                CONJUGATORS[e1][e2] = (gamma, ~gamma)
                break

class GroupInstruction(object):
    def __init__(self, index, g0, g1):
        self.index = index
        self.g0 = g0
        self.g1 = g1
    
    def __str__(self):
        return str(self.index).ljust(4) + str(self.g0).ljust(15) + str(self.g1).ljust(13)

    def execute(self, x):
        assert x[self.index] == '0' or x[self.index] == '1'
        if x[self.index] == '0':
            return self.g0
        else:
            return self.g1

class GroupProgram():
    def __init__(self, instructions, alpha=ALPHA):
        self.alpha = alpha
        self.instructions = instructions

    def __str__(self):
        s = 'i |'.ljust(4) + 'g0'.ljust(13) + '| ' + 'g1'.ljust(13) + '' + '\n'
        s += '-' * 34 + '\n'
        for ins in self.instructions:
            s += str(ins)
            s += '\n'
        s += '-' * 34
        return s

    def copy(self):
        return GroupProgram(self.instructions[:], self.alpha)

    def alpha_compute(self, x):
        state = IDENTITY
        for ins in self.instructions:
            bit = x[ins.index]
            assert bit == '0' or bit == '1'
            if bit == '0':
                state = state * ins.g0
            if bit == '1':
                state = state * ins.g1
        return state

    def evaluate(self, x):
        output = self.alpha_compute(x)
        assert (output == IDENTITY or output == self.alpha)
        return output == self.alpha

    def convert_from_beta_to_alpha(self, beta, alpha):
        gamma, gamma_inv = CONJUGATORS[beta][alpha]

        first_instruction = self.instructions[0]
        new_first = GroupInstruction(
            first_instruction.index,
            gamma * first_instruction.g0,
            gamma * first_instruction.g1
        )
        self.instructions[0] = new_first

        last_instruction = self.instructions[-1]
        new_last = GroupInstruction(
            last_instruction.index,
            last_instruction.g0 * gamma_inv,
            last_instruction.g1 * gamma_inv
        )
        self.instructions[-1] = new_last
        self.alpha = alpha