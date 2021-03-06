# 　たまご　★　たまご　★　たまご　#

import pygame.midi as midi
import re
import time
from tkinter import *
import commands
from threading import Timer

tk = None
prog_box = None
stack_box = None
var_box = None
midi_out = None
midi_in = None
prog = []

midi_in_list = []
midi_in_names = []
midi_out_list = []
midi_out_names = []
mi_var = None
mo_var = None

running = False

clkin = None
numrtc = 0

linenum = 0
lineidx = 0

#  midi, osc, etc. device values
dev_vals = {";len": 1, ";vel": 64, ";chn": 0, ";note": 0}

filename = "prog.txt"

delay = 0.125  # 16th notes at 120 BPM


def PRINT():
    UpdateStackBox()
    UpdateVarBox()


def BPM():
    if not (ret := commands.typecheckandpop(1, "BPM")):
        return

    if ret[0] == 0:
        print("BPM Error: BPM of 0 is invalid")
        commands.PUSH(ret[0])  # divide by 0 short circuit
        return

    global delay
    delay = 60.0 / ret[0]  # bpm = seconds / beat
    delay /= 4  # sixteenth notes


# stop running
def BRK():
    PRINT()
    stop()


# set midi, osc, etc values. send midi, osc messages and so on
# just midi noteon for now. Eventually I'll support cc, osc, etc.
# which of these does orca support and how?
def DEO():
    if not (ret := commands.typecheckandpop(2, "DEO", False)):
        return

    label = ret[0]
    val = ret[1]

    if not isinstance(label, str):
        print("DEO Error: Label is not string", label)
        return
    if not isinstance(val, int):
        print("DEO Error: Value is not an int", label)
        return
    if label in dev_vals:
        dev_vals[label] = val
    elif label == ";midi":  # simply noteon for now
        midiOn()
    else:
        print("DEO Error: No such device label", label)


def midiOn():
    global delay

    try:
        midi_out.note_on(
            dev_vals[";note"], velocity=dev_vals[";vel"], channel=dev_vals[";chn"]
        )

        # kill the note after a delay
        # this won't work right if call BPM before the cb triggers
        timer = Timer(
            delay * dev_vals[";len"] - .02,
            noteOff,
            args=[dev_vals[";note"], dev_vals[";chn"]],
        )
        timer.start()
    except:
        print("Midi Error: Failed to send midi")
        pass


def midiOff(a):
    midi_out.note_off(a)


def noteOff(note, channel):
    midi_out.note_off(note, channel=channel)


def JMP():
    if not (ret := commands.typecheckandpop(1, "JMP", False)):
        return False

    if not isinstance(ret[0], str):
        print("JMP Error: Label is not a string", ret[0])
        return False

    return goto(ret[0])


def JCN():
    if not (ret := commands.typecheckandpop(2, "JCN", False)):
        return False

    label = ret[0]
    con = ret[1]

    if not isinstance(label, str):
        print("JCN Error: Label is not a string", label)
        return False
    if not isinstance(con, int):
        print("JCN Error: Conditional is not an int", label)
        return False
    if con:
        return goto(label)

    return False


def goto(a):
    a = "@" + a[1:]
    global linenum, lineidx
    for line in range(len(prog)):
        for commidx in range(len(prog[line])):
            comm = prog[line][commidx]
            if comm == a:
                linenum = line
                lineidx = commidx
                return True
    print("Jump Error: No such label")
    return False


def midiInit():
    midi.init()


# called when you toggle the clock button
def ClkOn():
    global numrtc
    numrtc = 0


def graphicsInit():
    global tk, prog_box, clkin, check, stack_box, var_box

    ## basic setup
    tk = Tk()
    tk.geometry("700x700")
    # tk.minsize = (700, 700) this doesn't work...
    # tk.resizable(width=False, height=False)
    # keep people from breaking the graphics for now

    try:
        photo = PhotoImage(file="resources/tamago_icon.png")
        tk.iconphoto(False, photo)
    except:
        pass

    tk.title("tamago")
    frame_relief = FLAT  # set this to RAISED to see the frames
    bg_color = "#FCFFD7"
    tk.configure(bg=bg_color)

    ## text boxes
    # stack display
    stack_frame = Frame(tk, relief=frame_relief, borderwidth=1, bg=bg_color)
    stack_frame.pack(side=LEFT, fill=NONE, expand=False)
    stack_box = Label(
        stack_frame, height=30, width=10, text="", font=("Arial", 10), bg=bg_color
    )
    stack_box.pack(expand=False, side=LEFT)

    # variable display
    var_frame = Frame(tk, relief=frame_relief, borderwidth=1, height=60, bg=bg_color)
    var_frame.pack(side=TOP, fill=X, expand=False)
    var_frame.pack_propagate(0)  # otherwise it wants to be chonky
    var_box = Label(
        var_frame, height=20, width=80, text="", font=("Arial", 10), bg=bg_color
    )
    var_box.pack(expand=False)
    UpdateVarBox()

    #  program box
    progframe = Frame(tk, relief=frame_relief, borderwidth=1, bg=bg_color)
    progframe.pack(fill=BOTH, expand=True)
    prog_box = Text(progframe, height=30, width=80)
    prog_box.pack(fill=BOTH, expand=True, side=BOTTOM, padx=10, pady=5)

    ## buttons and midi
    global midi_in_names, midi_out_names, mi_var, mo_var
    UpdateMidiDevices()

    butt_frame = Frame(tk, relief=frame_relief, borderwidth=1, height=60, bg=bg_color)
    butt_frame.pack(fill=X, expand=False, side=BOTTOM)
    butt_frame.pack_propagate(0)  # otherwise it wants to be chonky

    #  push the buttons to the left
    butt_pad_frame = Frame(
        butt_frame,
        relief=frame_relief,
        borderwidth=1,
        height=60,
        width=130,
        bg=bg_color,
    )
    butt_pad_frame.pack(fill=X, expand=False, side=RIGHT)
    butt_pad_frame.pack_propagate(0)  # otherwise it wants to be chonky

    # midi output dropdown
    mo_var = StringVar()
    mo_var.set(midi_out_names[0])
    mo_var.trace("w", setMidiOut)
    midi_out_drop = OptionMenu(butt_frame, mo_var, *midi_out_names)
    midi_out_drop.pack(side=RIGHT, padx=10, pady=5)

    # midi input dropdown
    mi_var = StringVar()
    mi_var.set(midi_in_names[0])
    mi_var.trace("w", setMidiIn)
    midi_in_drop = OptionMenu(butt_frame, mi_var, *midi_in_names)
    midi_in_drop.pack(side=RIGHT, padx=10, pady=5)

    # clk in checkbox
    clkin = BooleanVar()
    check = Checkbutton(
        butt_frame,
        text="Clk In",
        variable=clkin,
        onvalue=True,
        offvalue=False,
        command=ClkOn,
        bg=bg_color,
    )
    check.pack(side=RIGHT, padx=20, pady=5)

    # stop button
    stopbutt = Button(butt_frame, text="Stop", command=stop)
    stopbutt.pack(side=RIGHT, padx=5, pady=5)

    # start button
    butt = Button(butt_frame, text="Run", command=start)
    butt.pack(side=RIGHT, padx=10, pady=5)


def UpdateMidiDevices():
    global midi_in_list, midi_out_list
    global midi_in_names, midi_out_names

    midi_in_list = [("none", -1)]
    midi_in_names = ["none"]
    midi_out_list = [("none", -1)]
    midi_out_names = ["none"]

    num_devices = midi.get_count()
    for i in range(num_devices):
        dev = midi.get_device_info(i)
        name = str(dev[1])[2:-1]

        # input
        if dev[2] == 1:
            midi_in_list.append((name, i))
            midi_in_names.append(name)

        # output
        elif dev[3] == 1:
            midi_out_list.append((name, i))
            midi_out_names.append(name)


def setMidiIn(*args):
    global mi_var, midi_in_list
    global midi_in
    global midi_out

    name = mi_var.get()

    if name == "none":
        if midi_in != None:
            midi_in.close()
        return

    for i in midi_in_list:
        if i[0] == name:
            if midi_in != None:
                midi_in.close()

            # restart midi and reopen i/o
            midi.quit()
            midi.init()
            midi_in = midi.Input(i[1])

            if midi_out != None:
                midi_out = midi.Output(midi_out.device_id)

            return


def setMidiOut(*args):
    global mo_var, midi_out_list
    global midi_out
    global midi_in

    name = mo_var.get()
    if name == "none":
        if midi_out != None:
            midi_out.close()
        return

    for i in midi_out_list:
        if i[0] == name:
            if midi_out != None:
                midi_out.close()

            # restart midi and reopen i/o
            midi.quit()
            midi.init()
            midi_out = midi.Output(i[1])

            if midi_in != None:
                midi_in = midi.Input(midi_in.device_id)

            return


def start():
    global running, linenum, lineidx, prog
    linenum = 0
    lineidx = 0
    prog = []
    Parse()
    running = True


def stop():
    global running, linenum, lineidx, prog
    running = False
    linenum = 0
    lineidx = 0
    prog = []


def midiClose():
    midi_out.close()
    midi_in.close()
    midi.quit()


mapping = {
    "POP": commands.POP,
    "ADD": commands.ADD,
    "SUB": commands.SUB,
    "MUL": commands.MUL,
    "DIV": commands.DIV,
    "SFT": commands.SFT,
    "MOD": commands.MOD,
    "PRINT": PRINT,
    "DUP": commands.DUP,
    "BPM": BPM,
    "SWP": commands.SWP,
    "STA": commands.STA,
    "DEO": DEO,
    "LDA": commands.LDA,
    "INC": commands.INC,
    "DEC": commands.DEC,
    "NIP": commands.NIP,
    "OVR": commands.OVR,
    "ROT": commands.ROT,
    "EQU": commands.EQU,
    "NEQ": commands.NEQ,
    "GTH": commands.GTH,
    "LTH": commands.LTH,
    "AND": commands.AND,
    "ORA": commands.ORA,
    "EOR": commands.EOR,
    "XOR": commands.XOR,
    "JMP": JMP,
    "JCN": JCN,
    "BRK": BRK,
    "CLS": commands.CLS,
}

# get the code that goes with that macro name
# this still misses some kinds of errors for sure but it's pretty robust for now
def GetMacro(prog, macro_name):
    match = re.search(r"\%" + macro_name + "[ |\t]", prog)
    if match == None:
        return -1
    prog = prog[match.start(0) :]  # start prog from macro label
    prog = prog[len(macro_name) + 1 :]  # cut out macro name

    split = re.split("\{[ |\t]", prog)  # split out opening brace
    if len(split) < 2:
        return -1  # short circuit no opening brace
    prog = split[1]

    split = re.split("[ |\t]\}", prog)  # split out closing brace
    if len(split) < 2:
        return -1
    prog = split[0]

    return " " + prog + " "


# valid commands e.g. PRINT
def ValidCommand(token):
    if len(token) == 0:
        return True

    global mapping
    return token in mapping


# valid non-command code e.g. { or #31
def ValidNonCommand(token):
    if len(token) == 0:
        return True

    ret = False

    ret |= (token == "{") or (token == "}")  # macro braces
    ret |= token[0] == "#"  # this should check for all ints after the #...
    ret |= (token[0] == ";") or (token[0] == "@")  # tokens / "addresses" for JMP
    ret |= token[0] == "%"  # macros
    ret |= token == "CLK"  # CLK commands (technically not a command)
    ret |= token == "*"  # * commands (technically not a command)

    return ret


def AllValidCode(prog_data):
    tokenized = re.split("[ |\t]", prog_data)
    for token in tokenized:
        if not (ValidCommand(token) or ValidNonCommand(token)):
            return False
    return True


def DestroyMacros(prog_data):
    # destroy the macros
    # this isn't done correctly but good enough for now!
    mac_loc = prog_data.find("%")
    end_loc = prog_data.find("}")
    while mac_loc != -1:
        if end_loc == -1:
            return -1  # no end to macro
        prog_data = prog_data[:mac_loc] + prog_data[end_loc + 1 :]
        mac_loc = prog_data.find("%")
        end_loc = prog_data.find("}")
    return prog_data


# find and destroy all macros recursively
def Macros(prog_data):
    if AllValidCode(prog_data):
        return DestroyMacros(prog_data)

    ret = ""
    tokenized = re.split("[ |\t]", prog_data)
    for token in tokenized:
        if ValidCommand(token) or ValidNonCommand(token):
            ret += token + " "
        else:
            macro_code = GetMacro(prog_data, token)
            if macro_code == -1:
                return -1
            else:
                ret += macro_code

    return Macros(ret)


def Comments(prog):
    match = re.search("\(\S", prog)
    if match != None:
        return -1

    match = re.search("\S\)", prog)
    if match != None:
        return -1

    # prog = re.sub('\( .* \)', '', prog)
    for i in range(len(prog) - 1):
        # search for '( '
        if prog[i : i + 2] == "( ":
            # search for ' )'
            for j in range(i, len(prog) - 1):
                if prog[j : j + 2] == " )":
                    prog = prog[0:i] + prog[j + 2 :]
                    return Comments(prog)
            return -1  # unclosed comment
    return prog


def UpdateVarBox():
    global var_box

    vars = ""

    for i in range(8):
        vars += str(i)
        vars += ": "
        vars += hex(commands.memory[i])
        vars += "       "

    var_box.config(text=vars)


def UpdateStackBox():
    global stack_box

    stack = ""
    counter = 0
    for item in reversed(commands.stack):
        # ints as hex strings
        if type(item) == int:
            stack += hex(item) + "\n"
        else:
            stack += item + "\n"
        counter += 1
        if counter > 25:
            break

    stack_box.config(text=stack)


def Parse():
    global prog
    prog_data = prog_box.get("1.0", END)

    # replace newlines with spaces
    prog_data = prog_data.replace("\n", " ")
    prog_data = prog_data.replace("*", " CLK ")

    # short circuit on empty code
    lines = re.split("CLK", prog_data)  # split on CLK command
    if lines == [[""]]:
        return

    prog_data = Comments(prog_data)  # do comment stuff

    if prog_data == -1:
        print("Parse Error: Malformed comment")
        return

    prog_data = Macros(prog_data)  # do macro stuff

    if prog_data == -1:
        print("Parse Error: Bad macro")
        return

    # split into lines then tokenize
    lines = re.split("CLK", prog_data)  # split on CLK command again
    for i in range(len(lines)):
        lines[i] = re.split("[ |\t]", lines[i])

    temp_prog = []

    # strip out empty lines
    lines[:] = [x for x in lines if x != [""]]

    # strip out empty commands
    lines[:] = [[x for x in y if x != ""] for y in lines]

    # match tokens with commands from dict or data
    for i in lines:
        commands.subprog = []
        for j in range(len(i)):
            item = i[j]
            if item == "":
                return  # short circuit on empty item
            elif item[0] == "#":
                try:
                    # push number on stack
                    commands.subprog.append(int(item[1:], 16))
                except:
                    continue
            elif item[0] == "@" or item[0] == ";":
                # label (just for jumps for now)
                if len(item) > 1:  # don't want '@' or ';' to be valid
                    commands.subprog.append(item)
            elif item in mapping:
                commands.subprog.append(mapping[item])
            else:
                return  # short circuit on bad command name
        temp_prog.append(commands.subprog)
    prog = temp_prog.copy()


def Init():
    midiInit()
    graphicsInit()


def ExecuteLine():
    global prog, linenum, lineidx
    thisline = prog[linenum]
    lineidx = 0
    while lineidx < len(thisline):
        command = thisline[lineidx]
        if type(command) is int:
            commands.PUSH(command)  # push ints
        elif type(command) is str:
            if command[0] == "@":
                pass  # skip labels
            elif command[0] == ";":
                commands.PUSH(command)  # push 'rel addr' onto stack
        elif command == JMP or command == JCN:
            # give him a call!
            if command():
                thisline = prog[linenum]
                continue  # skip the increment
        elif command == BRK:
            command()
            return
        else:
            command()  # run commands
        lineidx += 1


now = time.time()
linenum = 0


def EmptyMidiIn():
    global midi_in
    if midi_in != None:
        while midi_in.read(1):
            pass


def ClockCheck():
    global now, midi_in, delay, numrtc

    if clkin.get():
        if midi_in == None:
            return False
        try:
            midi_in.poll()
        except:
            return False

        msg = midi_in.read(1)
        while msg:
            msg = msg[0]

            # start or continue
            if msg[0][0] == 250 or msg[0][0] == 251:
                numrtc = 0

            # timing clock, 24 ticks per quarter note
            elif msg[0][0] == 248:
                if numrtc == 0:
                    numrtc = (numrtc + 1) % 6
                    return True
                numrtc = (numrtc + 1) % 6
            msg = midi_in.read(1)
        return False

    # dump the midi in queue
    elif midi_in != None:
        EmptyMidiIn()

    # local clock
    nownow = time.time()
    if nownow - now >= delay:
        now = nownow
        return True

    return False


def Run():
    global prog, now, linenum, running

    prog = []
    while True:
        try:
            tk.update_idletasks()
            tk.update()
        except:
            return

        if not running:
            # empty midi in queue
            EmptyMidiIn()
            continue

        if ClockCheck():
            UpdateStackBox()
            UpdateVarBox()
            if len(prog) > 0:
                if linenum >= len(prog):
                    linenum = len(prog)
                else:
                    ExecuteLine()
                    linenum += 1
            else:
                linenum = 0


def main():
    try:
        midiClose()
    except:
        pass
    Init()
    Run()


main()
