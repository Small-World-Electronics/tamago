import pygame.midi as midi
import re
import time
import os
import win32file
import msvcrt
from tkinter import *

ws = None
text_box = None
stack = []
controller = None
prog = None

filename = 'prog.txt'

delay = .5

def POP():
    a = stack.pop()
    return a

# only used internally for now, in code it's just #100 for example
def PUSH(i):
    stack.append(i)

def ADD():
    b = POP()
    a = POP()
    PUSH(a + b)

def SUB():
    b = POP()
    a = POP()
    PUSH(a - b)

def MUL():
    b = POP()
    a = POP()
    PUSH(a * b)

def DIV():
    b = POP()
    a = POP()
    PUSH(a // b)

def SHL():
    b = POP()
    a = POP()
    a = a << b
    PUSH(a)

def SHR():
    b = POP()
    a = POP()
    a = a >> b
    PUSH(a)

def MOD():
    b = POP()
    a = POP()
    a = a % b
    PUSH(a)

def DUP():
    a = POP()
    PUSH(a)
    PUSH(a)

def PRINT():
    print(stack)

def BPM():
    a = POP()
    global delay
    delay = 60.0 / a

def MIDION():
    a = POP()
    controller.note_on(a, velocity = 100)

def MIDIOFF():
    a = POP()
    controller.note_off(a)

def midiInit():
    midi.init()

    # hardcoded loopmidi port for now
    global controller
    controller = midi.Output(3)

def graphicsInit():
    global ws
    global text_box
    ws = Tk()
    ws.geometry('700x700')
    text_box = Text(ws,height=50,width=100)
    text_box.pack(expand=True)
    
def midiClose():
    controller.close()
    midi.quit()

mapping = {"POP": POP, "PUSH": PUSH, "ADD": ADD, "SUB": SUB,
           "MUL": MUL, "DIV": DIV, "SHL": SHL, "SHR": SHR,
           "MOD": MOD, "PRINT": PRINT, "DUP": DUP, "MIDION": MIDION,
           "MIDIOFF": MIDIOFF, "BPM": BPM}

def Parse():
    # get file by lines and split on spaces or tabs
    global prog
    data = text_box.get("1.0",END)
    lines = data.splitlines()
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
    
def Init():
    midiInit()
    graphicsInit()

def ExecuteLine(linenum):
    global prog
    for command in prog[linenum]:
        if(type(command) is int):
            PUSH(command)
        else:
            command()
    

now = time.time()
def Run():    
    global prog
    global now
    
    commands = []
    linenum = 0
    while(True):
        Parse()
        ws.update_idletasks()
        ws.update()

        nownow = time.time()
        if(nownow - now >= delay):
            now = nownow
            linenum = (linenum + 1) % len(prog)
            ExecuteLine(linenum)
