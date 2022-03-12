stack = []
memory = [0 for i in range(256)]

# check the stack has enough items, and their type, then pop them
def typecheckandpop(length, funcname, type = "any"):
    if len(stack) < length:
        print(funcname + " Error: Too few items on stack")
        return []
    
    if type != "any":
        for i in range(length):
            if not isinstance(stack[-i -1], type):
                print(funcname, "Error:", stack[-1], 'is not of type', type)
                return []

    ret = [stack.pop() for i in range(length)]
    return ret


def POP():
    if not (ret := typecheckandpop(1, "POP")):
        return  # short circuit if stack is empty
    return ret[0]


# only used internally for now, in code it's just #100 for example
def PUSH(i):
    stack.append(i)


def ADD():
    if not (ret := typecheckandpop(2, "ADD", int)):
        return
    PUSH(ret[0] + ret[1])


def SUB():
    if not (ret := typecheckandpop(2, "SUB", int)):
        return
    PUSH(ret[1] - ret[0])


def MUL():
    if not (ret := typecheckandpop(2, "MUL", int)):
        return
    PUSH(ret[1] * ret[0])


def DIV():
    if not (ret := typecheckandpop(2, "DIV", int)):
        return

    # short circuit on divide by 0
    if ret[0] == 0:
        print("DIV Error: Divide by 0")
        PUSH(ret[1])
        PUSH(ret[0])
        return

    PUSH(ret[1] // ret[0])


def SFT():
    if not (ret := typecheckandpop(2, "SFT", int)):
        return

    left = (ret[0] & 0xF0) >> 4
    right = ret[0] & 0x0F

    ret[1] = ret[1] >> right
    ret[1] = ret[1] << left

    PUSH(ret[1])


def MOD():
    if not (ret := typecheckandpop(2, "MOD", int)):
        return

    # short circuit on divide by 0
    if ret[0] == 0:
        print("MOD Error: Divide by 0")
        PUSH(ret[1])
        PUSH(ret[0])
        return

    PUSH(ret[1] % ret[0])


def DUP():
    if not (ret := typecheckandpop(1, "DUP")):
        return

    PUSH(ret[0])
    PUSH(ret[0])


def SWP():
    if not (ret := typecheckandpop(2, "SWP")):
        return

    PUSH(ret[0])
    PUSH(ret[1])


def STA():
    if not (ret := typecheckandpop(2, "STA", int)):
        return

    if ret[0] < 0 or ret[0] > 255:
        print("STA Error: Address out of range")
        return  # only allowing 255 vars for now
    memory[ret[0]] = ret[1]


def LDA():
    if not (ret := typecheckandpop(1, "LDA", int)):
        return

    if ret[0] < 0 or ret[0] > 255:
        print("STA Error: Address out of range")
        return  # only allowing 255 vars for now

    PUSH(memory[ret[0]])


def INC():
    if not (ret := typecheckandpop(1, "INC", int)):
        return

    PUSH(ret[0] + 1)


def DEC():
    if not (ret := typecheckandpop(1, "DEC", int)):
        return

    PUSH(ret[0] - 1)


def NIP():
    if not (ret := typecheckandpop(2, "NIP")):
        return

    POP()
    PUSH(ret[0])


# a b -- a b a
def OVR():
    if not (ret := typecheckandpop(2, "OVR")):
        return

    PUSH(ret[1])
    PUSH(ret[0])
    PUSH(ret[1])


# a b c -- b c a
def ROT():
    if not (ret := typecheckandpop(3, "ROT")):
        return

    PUSH(ret[1])
    PUSH(ret[0])
    PUSH(ret[2])


def EQU():
    if not (ret := typecheckandpop(2, "EQU")):
        return

    PUSH(int(ret[1] == ret[0]))


def NEQ():
    if not (ret := typecheckandpop(2, "NEQ")):
        return

    PUSH(int(ret[1] != ret[0]))


def GTH():
    if not (ret := typecheckandpop(2, "GTH", int)):
        return

    PUSH(int(ret[1] > ret[0]))


def LTH():
    if not (ret := typecheckandpop(2, "LTH", int)):
        return

    PUSH(int(ret[1] < ret[0]))


def AND():
    if not (ret := typecheckandpop(2, "AND", int)):
        return

    PUSH(ret[1] & ret[0])


def ORA():
    if not (ret := typecheckandpop(2, "ORA", int)):
        return

    PUSH(ret[1] | ret[0])


def EOR():
    if not (ret := typecheckandpop(2, "EOR", int)):
        return

    PUSH(ret[1] ^ ret[0])


# I like this name better. Probably confusing to have two...
def XOR():
    EOR()
