from circuits import *
from tqdm import trange
import time

# print('Sleeping!')
# time.sleep(7200)

def majority(x):
    c = Counter(x)
    return c['1'] >= c['0']

def agrees_with(f, g, n):
    for i in trange(2 ** n):
        s = bin(i)[2:].zfill(n)
        # print('\n', i, bin(i), s, '-----')
        if f(s) != g(s):
            print(s, f(s), g(s))
            return False
    return True

# constructs circuit for maj3 and checks
maj3 = make_maj3().circuit_to_and_not()
assert(agrees_with(maj3.evaluate, majority, 3))

# converts to alpha program and checks
maj3_prog = maj3.circuit_to_alpha_program()
assert(agrees_with(maj3_prog.evaluate, majority, 3))
print(maj3_prog)

# constructs circuit for maj5 and checks
maj5 = make_maj5().circuit_to_and_not()
assert(agrees_with(maj5.evaluate, majority, 5))

# converts to alpha program and checks
maj5_prog = maj5.circuit_to_alpha_program()
assert(agrees_with(maj5_prog.evaluate, majority, 5))
print(maj5_prog)


# constructs circuit for majk and checks
k = 7
majk = make_majk(k)
print(majk.size())
assert(agrees_with(majk.evaluate, majority, k))

# converts to alpha program and checks
majk_prog = majk.circuit_to_alpha_program()
print(len(majk_prog.instructions))
print(majk_prog.evaluate('1111100'))
assert(agrees_with(majk_prog.evaluate, majority, k))