import pygame.midi as midi
import re
import time
from tkinter import *
import commands

tk = None
prog_box = None
macro_box = None
controller = None
prog = []

filename = 'prog.txt'

delay = .5

def midiInit():
    midi.init()

    # hardcoded loopmidi port for now
    global controller
    controller = midi.Output(3)

def graphicsInit():
    global tk, prog_box, text_box
    tk = Tk()
    tk.geometry('700x700')
    macro_box = Text(tk, height=10, width = 100)
    macro_box.pack(expand=True)
    prog_box = Text(tk,height=20,width=100)
    prog_box.pack(expand=True)

def midiClose():
    controller.close()
    midi.quit()

mapping = {"POP": commands.POP, "PUSH": commands.PUSH, "ADD": commands.ADD, "SUB": commands.SUB,
           "MUL": commands.MUL, "DIV": commands.DIV, "SHL": commands.SHL, "SHR": commands.SHR,
           "MOD": commands.MOD, "PRINT": commands.PRINT, "DUP": commands.DUP, "MIDION": commands.MIDION,
           "MIDIOFF": commands.MIDIOFF, "BPM": commands.BPM, "SWP": commands.SWP, "STA": commands.STA,
           "LDA": commands.LDA}

def Parse():
    global prog
    data = prog_box.get("1.0",END)
    
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
        commands.SUBprog = []
        for j in range(len(i)):
            item = i[j]
            if(item == ''):
                return # short citcuit on empty item
            elif(item[0] == '#'):
                try:
                    commands.SUBprog.append(int(item[1:], 16))
                except:
                    continue
            elif item in mapping:
                commands.SUBprog.append(mapping[item])                
            else:
                return # short circuit on bad command name
        temp_prog.append(commands.SUBprog)
    prog = temp_prog.copy()
    
def Init():
    midiInit()
    graphicsInit()

def ExecuteLine(linenum):
    global prog
    for command in prog[linenum]:
        if(type(command) is int):
            commands.PUSH(command)
        else:
            command()

now = time.time()
def Run():    
    global prog, now

    prog = []
    commands = []
    linenum = 0
    while(True):
        Parse()
        tk.update_idletasks()
        tk.update()

        nownow = time.time()
        if(nownow - now >= delay):
            if(len(prog) > 0):
                now = nownow
                linenum = (linenum + 1) % len(prog)
                ExecuteLine(linenum)

def main():
    Init()
    Run()

main()