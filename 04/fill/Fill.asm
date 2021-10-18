// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

//pseudo-code
//LOOP:
//  if kb_is_not_pressed
//     white_screen()
//  black_screen()

(LOOP)
    @KBD
    D=M
    @white
    D;JEQ
    (LOOP)
        @i
        M=1



