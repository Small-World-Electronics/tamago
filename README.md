# Stack Proto Alpha

Livecoding music sequencer based on [uxn](https://wiki.xxiivv.com/site/uxn.html) and more loosely [Orca](https://github.com/hundredrabbits/Orca), both by the wonderful [Hundred Rabbits](https://github.com/hundredrabbits).

## Language

The language is a modified version of the [uxntal](https://wiki.xxiivv.com/site/uxntal.html) used on the [Varvara Computer](https://wiki.xxiivv.com/site/varvara.html).

If you're familiar with uxntal, here's a list of the things that work differently.

#### Bitshifting

I've replaced the single bitshift command with a `SHR` and `SHL` command. These work how you might expect. I find this a bit easier to work with, and think it will be a bit more beginner friendly. Perhaps the original command can be added as well just to have additional options.

#### Push

There is no `LIT` command. If you want to push a number on the stack, use the `#` syntactic sugar. 

That's `#2F` to push 0x2F onto the stack.

#### DEO / DEI

This is overloaded to work with midi ( and eventually OSC and so on ).

| Command | Effect |
| --- | --- |
| `#50 ;note DEO` | Set the midi note value to 0x50 |
| `#50 ;vel DEO` | Set the midi velocity value to 0x50 |
| `#00 ;chn DEO` | Set the midi channel value to 0x00 |
| `#02 ;len DEO` | Set the midi note length (in 16th notes) to 0x02 |
| `#00 ;midi DEO` | Send a midi Note On message with the current settings |

`;midi DEO` will be extended soon with options for note off, control messages, etc.

#### Labels

These aren't really memory locations like they are in the full implementation, so no fun math tricks here! These are simply to be used as locations for the jump instructions.

The only label available borrows from the literal address absolute notation.  
That's `@label` to create a label and `;label` to push it onto the stack

So to create a loop for example: 
```
@loop
( do something here )
;loop JMP
```

Labels are also overloaded for the DEO / DEI midi implementation. Check that section for more details.

#### STA / LDA

This is overloaded with a simple store / load system for variables. There are 128 slots available to store integers. If you want to label your variables, for now the best way is with a macro.

```
%VAR1 { #00 } ( variable 1 )

#04 VAR1 STA ( store 0x04 in variable 1 )
VAR1 LDA ( load variable one onto the stack )
```

#### Missing Commands / things

- The return stack hasn't been implemented (yet). STH therefore is not implemented.
- SFT (todo)
- LDZ / STZ, LDR / STR. Addresses aren't really a thing as such, so we just use STA / LDA as described above.
- `| . $ , & : ' ~ "` We have no need for these things as of yet.
- BRK (todo)
- Short versions of commands. 

## Future Plans

- Add Midi ctrl, noteoff, pitchbend, etc. To DEO
- Add DEI
- Add OSC compatability
- Add clock out
- Improve graphics
- Create executable / installer / make it portable
- Unit testing
- Implement the return stack
- File load / write