import operator
import functools
from itertools import chain
from collections import defaultdict

ops = [operator.add, operator.mul, operator.and_, operator.or_]
def opr(op, registers: [int], inpA: int, inpB: int, outC: int) -> None:
    registers[outC] = op(registers[inpA], registers[inpB])
def opi(op, registers: [int], inpA: int, B: int, outC: int) -> None:
    registers[outC] = op(registers[inpA], B)

def setr(registers: [int], inpA: int, inpB: int, outC: int) -> None:
    registers[outC] = registers[inpA]
def seti(registers: [int], A: int, inpB: int, outC: int) -> None:
    registers[outC] = A

rels = [operator.gt, operator.eq]
def relir(op, registers: [int], A: int, inpB: int, outC: int) -> None:
    registers[outC] = 1 if op(A, registers[inpB]) else 0
def relri(op, registers: [int], inpA: int, B: int, outC: int) -> None:
    registers[outC] = 1 if op(registers[inpA], B) else 0
def relrr(op, registers: [int], inpA: int, inpB: int, outC: int) -> None:
    registers[outC] = 1 if op(registers[inpA], registers[inpB]) else 0

funcs = list(chain.from_iterable((functools.partial(opr, f), functools.partial(opi, f)) for f in ops))
funcs.extend([setr, seti])
funcs.extend(list(chain.from_iterable((functools.partial(relir, f), functools.partial(relri, f), functools.partial(relrr, f)) for f in rels)))

def parseLineList(line: str) -> [int]:
    l = line[line.find('[') + 1 : line.find(']')]
    l.split(', ')
    return list(map(int, l.split(', ')))

# (before, instr, after)
def parseSection(section: [str]) -> ([int], [int], [int]):
    before = parseLineList(section[0].strip())
    instr = list(map(int, section[1].strip().split(' ')))
    after = parseLineList(section[2].strip())
    return (before, instr, after)

""" x = parseSection(['Before: [1, 3, 2, 2]', \
              '6 2 3 2', \
              'After:  [1, 3, 1, 2]'])
print(x) """

def test():
    before = [2, 1, 1, 0]
    instr = [9,2,1,3]
    after = [2, 1, 1, 2]

    correct = 0
    for func in funcs:
        app = list(before)
        func(app, instr[1], instr[2], instr[3])
        if app == after:
            correct += 1
    print(correct)

#test()

def getNameForFunc(f) -> str:
    if hasattr(f, 'func'):
        return '{}:{}'.format(f.func.__name__, f.args[0].__name__)
    else:
        return f.__name__

opcodes = {}
# map opcodes -> function
with open('input_1.txt', 'r') as f:
    lines = f.readlines()
    sections = [lines[i : i + 3] for i in range(0, len(lines), 4)]
    data = list(map(parseSection, sections))

    # opcode -> {func. name -> occurances}
    matches = defaultdict(dict)

    for entry in data:
        before = entry[0]
        instr = entry[1]
        after = entry[2]

        correct = 0
        for func in funcs:
            appTo = list(before)
            func(appTo, instr[1], instr[2], instr[3])
            if appTo == after:
                vals = matches[instr[0]]
                funcName = getNameForFunc(func)
                vals[funcName] = 1 if funcName not in vals else vals[funcName] + 1

    # func -> opcodes used in
    funcsIn = {}
    for k,v in matches.items():
        for ff in v:
            if ff in funcsIn:
                funcsIn[ff].append(k)
            else:
                funcsIn[ff] = [k]
    
    checked = set()
    while len(checked) < 16:
        for k,v in funcsIn.items():
            diff = set(v) - checked
            if len(diff) == 1:
                opcode = diff.pop()
                for ff in funcs:
                    if getNameForFunc(ff) == k:
                        opcodes[opcode] = ff
                checked.add(opcode)

    f.close()

with open('input_2.txt', 'r') as f:
    registers = [0, 0, 0, 0]
    for line in f:
        instr = list(map(int, line.split(' ')))
        opcodes[instr[0]](registers, instr[1], instr[2], instr[3])
    print(registers)
    f.close()