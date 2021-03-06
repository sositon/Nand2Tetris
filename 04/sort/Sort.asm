// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 

@R14
D=M
@OuterIndex
M=D 


(OuterLoop)
@R14
D = M
@InnerIndex
M=D 
        
        
(InnerLoop)
@InnerIndex
A = M+1
D = M 
A = A-1 
D = D - M 

@SWAP
D;JGT

(IncrementInner)
@InnerIndex
M = M + 1
@R14
D = M
@R15
D = D + M
@InnerIndex
D = D - M
D = D - 1
@InnerLoop
D;JGT


@OuterIndex
M=M+1
@R14
D = M
@R15
D=D+M
@OuterIndex
D=D-M
D=D-1

@OuterLoop 
D;JGT

@END
0;JMP

(SWAP)
@InnerIndex
A = M + 1
D = M

@Temp
M = D

@InnerIndex
A = M
D = M
A =A+1
M = D

@Temp
D = M

@InnerIndex
A = M
M = D

@IncrementInner
0;JMP

(END)

