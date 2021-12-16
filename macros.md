# Useful Macros

## Pseudo-random ( a -- b )
`%RAND { #4E6D MUL #3039 ADD #FFFF AND }`

Takes in the last random number a and generates a new one b.

## Note On ( a -- )
`%MIDI { ;note DEO #00 ;midi DEO }`

Takes a midi note a off the stack and starts that note.

## Note Converter ( a b -- c )
`%NOTE { #0C MUL ADD }`

Takes a chromatic note a, and an octave b and converts it to a midi note c.

