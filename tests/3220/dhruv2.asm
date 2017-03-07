; Addresses for I/O
.NAME	HEX= 0xFFFFF000
.NAME	LEDR=0xFFFFF020
.NAME	KEY= 0xFFFFF080
.NAME	SW=  0xFFFFF090

; The stack is at the top of memory
.NAME	StkTop=65536

;  Number of sorting iterations
.NAME	ItNum=4

; The array starts at data address 0x1000 and has 4096 elements (16kB)
.NAME	Array=0x1000
.NAME	ArrayBytes=0x4000

; LED Errors
.NAME ErrDes=0x01F 						; Lower Half on
.NAME ErrAsc=0x3E0						; Upper Half on
.NAME DoneSort=0x2AA 					; 1010101010
.NAME AllDone=0x2AA 					;

; -----------------------------------------------------------------
; Processor Initialization
	.ORIG 0x100
	XOR		Zero,Zero,Zero						; Put a zero in the Zero register
	LW		SP,StackTopVal(Zero)			; Load the initial stack-top value into the SP
	SW		Zero,LEDR(Zero)						; Turn off LEDR

; Initialize the array with numbers 13, 13+11, 13+2*11, etc.
	ADDI 	Zero,T0,Array							; T0 is CurPtr, set to start of array
	LW		T1,ArrayBytesVal(Zero)
	ADD		T1,T1,T0									; T1 is EndPtr, set to end of array
	ADDI	Zero,S1,13								; S1 is the current value of the array element for initialization
	XOR		A1,S1,A0
Init:
	SW		S1,0(T0)									; Store value into an element
	ADDI	S1,S1,11									; Add 11 to the value for next element
	ADDI	T0,T0,4										; Move to next element
	BNE		T0,T1,Init								; if(CurPtr!=EndPtr) goto Init;

; Initialization done. Now check if the array is sorted in ascending order (it should be)
;	CALL	ChkAsc(Zero)

;------------------
StackTopVal:
.WORD StkTop
ArrayBytesVal:
.WORD ArrayBytes
