.NAME	HEX= 0xFFFFF000
.NAME	LEDR=0xFFFFF020
.NAME	KEY= 0xFFFFF080
.NAME	SW=  0xFFFFF090

add zero, zero, zero
ne a0, a1, a2
and s0, s1, s2
or s0, t0, t1

addi		s1,s1,0x1
andi	Zero,Zero,0
addi	Zero,t0,0xBAD
;subi  s1,s1,7531

beq	s1,s2,FirstInstWorks

FirstInstWorks:
	; Our Zero and FP registers will be zero
	xor		fp,fp,fp
	add     Zero,fp,fp
	; Put 1 on LEDR
	addi	Zero,s0,1
	sw		s0,LEDR(fp)
	; Put 2 on LEDR should still be off
	addi	s0,s0,1
	sw		s0,LEDR(fp)
	addi	fp,t0,-1
	addi	fp,t1,2
	addi	fp,a0,1
	add		a1,t0,t1
	lw		s0,LEDR(fp)

jal		t0,JalTarg(fp)
JalRet:
	beq		zero, zero, JalRet
JalTarg:
	bne		t0,t1,0
	jal		t1,0(t0)
sw t0, LEDR(zero)

not a0, a1
ge a0, a0, a1
gt a0, a0, a1
subi zero, zero, 0
subi zero, zero, 1
ret
call 0b10(zero)
jmp JalTarg(zero)
;011010 01 111 0000 0010 0000 0000 0101 sw t0, LEDR(zero)