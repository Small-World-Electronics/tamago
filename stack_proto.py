#　スタック　★　スタック　★　スタック　#

import pygame.midi as midi
import re
import time
from tkinter import *
import commands
from threading import Timer

tk = None
prog_box = None
controller = None
prog = []

filename = 'prog.txt'

delay = .5

def BPM():
    if(len(commands.stack) < 1):
        return
    a = commands.POP()
    if(a == 0):
        commands.PUSH(a) # divide by short circuit
        return
    global delay
    delay = 60.0 / a

def MIDION():
    global delay, midi_len
    if(len(commands.stack) < 1):
        return
    a = commands.POP()

    controller.note_on(a, velocity = commands.midi_vel, channel = commands.midi_chn)

    # kill the note after a delay
    # this won't work right if call BPM before the cb triggers
    timer = Timer(delay * commands.midi_len, noteOff, args = [a])
    timer.start()

def MIDIOFF():
    if(len(commands.stack) < 1):
        return
    a = commands.POP()
    controller.note_off(a)

def noteOff(note):
    controller.note_off(note)

def midiInit():
    midi.init()

    # hardcoded loopmidi port for now
    global controller
    controller = midi.Output(3)

def graphicsInit():
    global tk, prog_box, text_box
    tk = Tk()
    tk.geometry('700x700')
    prog_box = Text(tk,height=20,width=100)
    prog_box.pack(expand=True)

def midiClose():
    controller.close()
    midi.quit()

mapping = {"POP": commands.POP, "PUSH": commands.PUSH, "ADD": commands.ADD, "SUB": commands.SUB,
            "MUL": commands.MUL, "DIV": commands.DIV, "SHL": commands.SHL, "SHR": commands.SHR,
            "MOD": commands.MOD, "PRINT": commands.PRINT, "DUP": commands.DUP, "MIDION": MIDION,
            "MIDIOFF": MIDIOFF, "BPM": BPM, "SWP": commands.SWP, "STA": commands.STA,
            "LDA": commands.LDA, "INC": commands.INC, "DEC": commands.DEC, "NIP": commands.NIP,
            "OVR": commands.OVR, "ROT": commands.ROT, "EQU": commands.EQU, "NEQ": commands.NEQ,
            "GTH": commands.GTH, "LTH": commands.LTH, "AND": commands.AND, "ORA": commands.ORA,
            "EOR": commands.EOR, "XOR": commands.XOR, "VEL": commands.VEL, "CHN": commands.CHN,
            "LEN": commands.LEN}

# given a string, split it at the first space or tab
def SingleToken(data):
    data = re.split('[ |\t|\n]', data)
    if(len(data[0]) < 2):
        return -1
    return data[0][1:]

# get the code that goes with that macro name
# this still misses some kinds of errors for sure but it's pretty robust for now
def GetMacro(prog, macro_name):
    match = re.search(r"\%"+macro_name+'[ |\t]', prog)
    if(match == None):
        return -1
    prog = prog[match.start(0):] # start prog from macro label
    prog = prog[len(macro_name) + 1:] # cut out macro name

    split = re.split('\{[ |\t]', prog)# split out opening brace
    if(len(split) < 2):
        return -1 # short circuit no opening brace
    prog = split[1]

    split = re.split('[ |\t]\}', prog) # split out closing brace
    if(len(split) < 2):
        return -1
    prog = split[0]

    return ' ' + prog + ' '

# fill in the given maco label with the macro code
def MacroFill(program, macro_name, macro_code):
    return program.replace('!' + macro_name, macro_code)

# find and destroy all macros recursively
def Macros(prog_data):
    fill_loc = prog_data.find('!')
    while(fill_loc != -1):
        macro_name = SingleToken(prog_data[fill_loc:])
        if(macro_name == -1):
            return -1

        macro_code = GetMacro(prog_data, macro_name)
        if(macro_code == -1):
            return -1

        prog_data = MacroFill(prog_data, macro_name, macro_code)
        if(prog_data == -1):
            return -1

        fill_loc = prog_data.find('!')

    # destroy the macros
    # this isn't done correctly but good enough for now!
    mac_loc = prog_data.find('%')
    end_loc = prog_data.find('}')
    while(mac_loc != -1):
        if(end_loc == -1):
            return -1 # no end to macro
        prog_data = prog_data[:mac_loc] + prog_data[end_loc + 1:]
        mac_loc = prog_data.find('%')
        end_loc = prog_data.find('}')
    return prog_data

def Parse():
    global prog
    prog_data = prog_box.get("1.0",END)
    
    # short circuit on empty code
    lines = prog_data.splitlines()
    if(lines == [['']]):
        return

    prog_data = Macros(prog_data)
    if(prog_data == -1):
        return

    # split into lines then tokenize
    lines = prog_data.splitlines()
    for i in range(len(lines)):
        lines[i] = re.split('[ |\t]', lines[i])

    temp_prog = []

    # strip out empty lines
    lines[:] = [x for x in lines if x != ['']]

    # strip out empty commands
    lines[:] = [[x for x in y if x != ''] for y in lines]

    # match tokens with commands from dict or data
    for i in lines:
        commands.subprog = []
        for j in range(len(i)):
            item = i[j]
            if(item == ''):
                return # short circuit on empty item
            elif(item[0] == '#'):
                try:
                    commands.subprog.append(int(item[1:], 16))
                except:
                    continue
            elif item in mapping:
                commands.subprog.append(mapping[item])                
            else:
                return # short circuit on bad command name
        temp_prog.append(commands.subprog)
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
    try:
        midiClose()
    except:
        pass
    Init()
    Run()
