stack = []
memory = [0 for i in range(256)]


def POP():
    if stack == []:
        return  # short circuit if stack is empty
    a = stack.pop()
    return a


# only used internally for now, in code it's just #100 for example
def PUSH(i):
    stack.append(i)


def ADD():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(a + b)


def SUB():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(a - b)


def MUL():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(a * b)


def DIV():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()

    # short circuit on divide by 0
    if b == 0:
        PUSH(a)
        PUSH(b)
        return

    PUSH(a // b)


def SHL():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    a = a << b
    PUSH(a)


def SHR():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    a = a >> b
    PUSH(a)


def MOD():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()

    # short circuit on divide by 0
    if b == 0:
        PUSH(a)
        PUSH(b)
        return

    a = a % b
    PUSH(a)


def DUP():
    if len(stack) < 1:
        return
    a = POP()
    PUSH(a)
    PUSH(a)


def PRINT():
    print(stack)


def SWP():
    if len(stack) < 2:
        return
    a = POP()
    b = POP()
    PUSH(a)
    PUSH(b)


def STA():
    if len(stack) < 2:
        return
    add = POP()
    val = POP()
    if add < 0 or add > 255:
        return  # only allowing 255 vars for now
    memory[add] = val


def LDA():
    if len(stack) < 1:
        return
    add = POP()
    PUSH(memory[add])


def INC():
    if len(stack) < 1:
        return
    a = POP() + 1
    PUSH(a)


def DEC():
    if len(stack) < 1:
        return
    a = POP() - 1
    PUSH(a)


def NIP():
    if len(stack) < 2:
        return
    a = POP()
    POP()
    PUSH(a)


# a b -- a b a
def OVR():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(a)
    PUSH(b)
    PUSH(a)


# a b c -- b c a
def ROT():
    if len(stack) < 3:
        return
    c = POP()
    b = POP()
    a = POP()
    PUSH(b)
    PUSH(c)
    PUSH(a)


def EQU():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(int(a == b))


def NEQ():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(int(a != b))


def GTH():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(int(a > b))


def LTH():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(int(a < b))


def AND():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(a & b)


def ORA():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(a | b)


def EOR():
    if len(stack) < 2:
        return
    b = POP()
    a = POP()
    PUSH(a ^ b)


# I like this name better. Probably confusing to have two...
def XOR():
    EOR()
