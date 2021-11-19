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
prog = []

filename = 'prog.txt'

delay = .5

def POP():
    if(stack == []):
        return # short circuit if stack is empty
    a = stack.pop()
    return a

# only used internally for now, in code it's just #100 for example
def PUSH(i):
    stack.append(i)

def ADD():
    if(len(stack) < 2):
        return
    b = POP()
    a = POP()
    PUSH(a + b)

def SUB():
    if(len(stack) < 2):
        return
    b = POP()
    a = POP()
    PUSH(a - b)

def MUL():
    if(len(stack) < 2):
        return
    b = POP()
    a = POP()
    PUSH(a * b)

def DIV():
    if(len(stack) < 2):
        return
    b = POP()
    a = POP()

    # short circuit on divide by 0
    if(b == 0):
        PUSH(a)
        PUSH(b)
        return
    
    PUSH(a // b)

def SHL():
    if(len(stack) < 2):
        return
    b = POP()
    a = POP()
    a = a << b
    PUSH(a)

def SHR():
    if(len(stack) < 2):
        return
    b = POP()
    a = POP()
    a = a >> b
    PUSH(a)

def MOD():
    if(len(stack) < 2):
        return
    b = POP()
    a = POP()
    
    # short circuit on divide by 0
    if(b == 0):
        PUSH(a)
        PUSH(b)
        return

    a = a % b
    PUSH(a)

def DUP():
    if(len(stack) < 1):
        return
    a = POP()
    PUSH(a)
    PUSH(a)

def PRINT():
    print(stack)

def BPM():
    if(len(stack) < 1):
        return
    a = POP()
    global delay
    delay = 60.0 / a

def MIDION():
    if(len(stack) < 1):
        return
    a = POP()
    controller.note_on(a, velocity = 100)

def MIDIOFF():
    if(len(stack) < 1):
        return
    a = POP()
    controller.note_off(a)

def SWP():
    if(len(stack) < 2):
        return
    a = POP()
    b = POP()
    PUSH(a)
    PUSH(b)

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
           "MIDIOFF": MIDIOFF, "BPM": BPM, "SWP": SWP}

def Parse():
    global prog
    data = text_box.get("1.0",END)
    
    # split into lines then tokenize
    lines = data.splitlines()
    for i in range(len(lines)):
        lines[i] = re.split('[ |\t]', lines[i])

    temp_prog = []

    # short circuit on empty code
    if(lines == [['']]):
        return

    # match tokens with commands from dict or data
    for i in lines:
        subprog = []
        for j in range(len(i)):
            item = i[j]
            if(item == ''):
                return # short citcuit on empty item
            elif(item[0] == '#'):
                try:
                    subprog.append(int(item[1:], 16))
                except:
                    continue
            elif item in mapping:
                subprog.append(mapping[item])                
            else:
                return # short circuit on bad command name
        temp_prog.append(subprog)
    prog = temp_prog.copy()
    
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

    prog = []
    commands = []
    linenum = 0
    while(True):
        Parse()
        ws.update_idletasks()
        ws.update()

        nownow = time.time()
        if(nownow - now >= delay):
            if(len(prog) > 0):
                now = nownow
                linenum = (linenum + 1) % len(prog)
                ExecuteLine(linenum)

def main():
    Init()
    Run()
