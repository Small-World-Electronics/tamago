import pygame.midi as midi
import re
import time

stack = []
controller = None
f = None
prog = None

def POP():
    a = stack.pop()
    return a

# only used internally for now, in code it's just #100 for example
def PUSH(i):
    stack.append(i)

def ADD():
    a = POP()
    b = POP()
    PUSH(b + a)

def SUB():
    a = POP()
    b = POP()
    PUSH(b - a)

def MUL():
    a = POP()
    b = POP()
    PUSH(b * a)

def DIV():
    a = POP()
    b = POP()
    PUSH(b // a)

def SHL(i):
    a = POP()
    a = a << i
    PUSH(a)

def SHR(i):
    a = POP()
    a = a >> i
    PUSH(a)

def PRINT():
    print(stack)

def midiPop():
    a = POP()
    controller.note_on(a, velocity = 100)

def midiInit():
    midi.init()

    # hardcoded loopmidi port for now
    global controller
    controller = midi.Output(3)
    
def midiClose():
    controller.close()

def fileInit():
    global f
    f = open("prog.txt")

mapping = {"POP": POP, "PUSH": PUSH, "ADD": ADD, "SUB": SUB,
           "MUL": MUL, "DIV": DIV, "SHL": SHL, "SHR": SHR, "PRINT": PRINT}

def fileParse():
    # get file by lines and split on spaces or tabs
    global f
    global prog
    f.seek(0)
    lines = f.readlines()
    for i in range(len(lines)):
        lines[i] = re.split('[ |\t]', lines[i])

    # match tokens with commands from dict or data
    prog = []
    for i in lines:
        subprog = []
        for j in range(len(i)):
            item = i[j]
            if(item[0] == '#'):
                subprog.append(int(item[1:], 16))
            else:
                subprog.append(mapping[item])
        prog.append(subprog)
        
def main():
    global prog
    commands = []
    fileInit()
    while(True):
        fileParse()
        for line in prog:
            for command in line:
                if(type(command) is int):
                    PUSH(command)
                else:
                    command()
        time.sleep(500 / 1000)
