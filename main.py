from circuits import *
from tqdm import trange

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

print('Running tests on maj3 and maj5...')
# constructs circuit for maj3 and checks
maj3 = make_maj3().circuit_to_and_not()
assert(agrees_with(maj3.evaluate, majority, 3))

# converts to alpha program and checks
maj3_prog = maj3.circuit_to_alpha_program()
assert(agrees_with(maj3_prog.evaluate, majority, 3))
# print(maj3_prog)

# constructs circuit for maj5 and checks
maj5 = make_maj5().circuit_to_and_not()
assert(agrees_with(maj5.evaluate, majority, 5))

# converts to alpha program and checks
maj5_prog = maj5.circuit_to_alpha_program()
assert(agrees_with(maj5_prog.evaluate, majority, 5))
# print(maj5_prog)


# constructs circuit for majk and checks
k = 13
print(f'Constructing circuit for maj{k}...')
majk = make_majk(k)
print(f'Circuit size for maj{k}: {majk.size()}')
print(f'Testing circuit...')
assert(agrees_with(majk.evaluate, majority, k))

# converts to alpha program and checks
print(f'Converting maj{k} circuit to alpha program...')
majk_prog = majk.circuit_to_alpha_program()
print(f'{len(majk_prog.instructions)} instructions in alpha program.')

inp = '1111100000011'
print(f'Now executing on {inp}. If k >= 11, this might take a while...')
result = majk_prog.evaluate(inp)
print(f'{inp} evaluates to {result}.')
# assert(agrees_with(majk_prog.evaluate, majority, k))