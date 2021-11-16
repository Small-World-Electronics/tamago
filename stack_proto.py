import pygame.midi as midi
import re
import time
import os
import win32file
import msvcrt

stack = []
controller = None
f = None
prog = None

filename = 'prog.txt'

# black magic to allow editing a file on windows while its open in python
#handle = win32file.CreateFile(filename,
 #                               win32file.GENERIC_READ,
  #                              win32file.FILE_SHARE_DELETE |
   #                             win32file.FILE_SHARE_READ |
    #                            win32file.FILE_SHARE_WRITE,
     #                           None,
      #                          win32file.OPEN_EXISTING,
       #                         0,
        #                        None)

# detach the handle
#detached_handle = handle.Detach()

# get a file descriptor associated to the handle
#file_descriptor = msvcrt.open_osfhandle(
 #S   detached_handle, os.O_RDONLY)

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

mapping = {"POP": POP, "PUSH": PUSH, "ADD": ADD, "SUB": SUB,
           "MUL": MUL, "DIV": DIV, "SHL": SHL, "SHR": SHR, "PRINT": PRINT}

def fileParse():
    # get file by lines and split on spaces or tabs
    global f
    global prog
    f = open(filename)
    f.seek(0)
    lines = f.read().splitlines()
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
    f.close()
        
def main():
    global prog
    commands = []
    fileParse()
    while(True):
        for line in prog:
            for command in line:
                if(type(command) is int):
                    PUSH(command)
                else:
                    command()
            fileParse()
            time.sleep(500 / 1000)
