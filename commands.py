stack = []
memory = [0 for i in range(256)]


def lencheck(length, funcname):
    if len(stack) < length:
        print(funcname + " Error: Too few items on stack")
        return True
    return False


def POP():
    if lencheck(1, "POP"):
        return  # short circuit if stack is empty
    a = stack.pop()
    return a


# only used internally for now, in code it's just #100 for example
def PUSH(i):
    stack.append(i)


def ADD():
    if lencheck(2, "ADD"):
        return
    b = POP()
    a = POP()
    PUSH(a + b)


def SUB():
    if lencheck(2, "SUB"):
        return
    b = POP()
    a = POP()
    PUSH(a - b)


def MUL():
    if lencheck(2, "MUL"):
        return
    b = POP()
    a = POP()
    PUSH(a * b)


def DIV():
    if lencheck(2, "DIV"):
        return
    b = POP()
    a = POP()

    # short circuit on divide by 0
    if b == 0:
        print("DIV Error: Divide by 0")
        PUSH(a)
        PUSH(b)
        return

    PUSH(a // b)


def SFT():
    if lencheck(2, "SFT"):
        return

    sft = POP()
    val = POP()

    left = (sft & 0xF0) >> 4
    right = sft & 0x0F

    val = val >> right
    val = val << left

    PUSH(val)


def MOD():
    if lencheck(2, "MOD"):
        return
    b = POP()
    a = POP()

    # short circuit on divide by 0
    if b == 0:
        print("MOD Error: Divide by 0")
        PUSH(a)
        PUSH(b)
        return

    a = a % b
    PUSH(a)


def DUP():
    if lencheck(1, "DUP"):
        return
    a = POP()
    PUSH(a)
    PUSH(a)


def SWP():
    if lencheck(2, "SWP"):
        return
    a = POP()
    b = POP()
    PUSH(a)
    PUSH(b)


def STA():
    if lencheck(2, "STA"):
        return
    add = POP()
    val = POP()
    if add < 0 or add > 255:
        return  # only allowing 255 vars for now
    memory[add] = val


def LDA():
    if lencheck(1, "LDA"):
        return
    add = POP()
    PUSH(memory[add])


def INC():
    if lencheck(1, "INC"):
        return
    a = POP() + 1
    PUSH(a)


def DEC():
    if lencheck(1, "DEC"):
        return
    a = POP() - 1
    PUSH(a)


def NIP():
    if lencheck(2, "NIP"):
        return
    a = POP()
    POP()
    PUSH(a)


# a b -- a b a
def OVR():
    if lencheck(2, "OVR"):
        return
    b = POP()
    a = POP()
    PUSH(a)
    PUSH(b)
    PUSH(a)


# a b c -- b c a
def ROT():
    if lencheck(3, "ROT"):
        return
    c = POP()
    b = POP()
    a = POP()
    PUSH(b)
    PUSH(c)
    PUSH(a)


def EQU():
    if lencheck(2, "EQU"):
        return
    b = POP()
    a = POP()
    PUSH(int(a == b))


def NEQ():
    if lencheck(2, "NEQ"):
        return
    b = POP()
    a = POP()
    PUSH(int(a != b))


def GTH():
    if lencheck(2, "GTH"):
        return
    b = POP()
    a = POP()
    PUSH(int(a > b))


def LTH():
    if lencheck(2, "LTH"):
        return
    b = POP()
    a = POP()
    PUSH(int(a < b))


def AND():
    if lencheck(2, "AND"):
        return
    b = POP()
    a = POP()
    PUSH(a & b)


def ORA():
    if lencheck(2, "ORA"):
        return
    b = POP()
    a = POP()
    PUSH(a | b)


def EOR():
    if lencheck(2, "EOR"):
        return
    b = POP()
    a = POP()
    PUSH(a ^ b)


# I like this name better. Probably confusing to have two...
def XOR():
    EOR()
