// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// pseudo-code
// res=0
//LOOP:
// if (R1 = 0) goto STOP
//  res = R0+res
//  R1 = R1-1
//
//STOP:
//  R2=res

@res
M=0
(LOOP)
    // if (R1=0) goto STOP
    @R1
    D=M
    @STOP
    D;JEQ
    //res=res+R0
    @R0
    D=M
    @res
    M=D+M
    //R1=R1-1
    @R1
    M=M-1
    @LOOP
    0;JMP
(STOP)
    // R2=res
    @res
    D=M
    @R2
    M=D
(END)
    @END
    0;JMP

