; Addresses for I/O
.NAME	HEX= 0xFFFFF000
.NAME	LEDR=0xFFFFF020
.NAME	KEY= 0xFFFFF080
.NAME	SW=  0xFFFFF090

.ORIG 0x100

ANDI a0, a0, 0      ; set a0 to 0
ADDI a0, a0, 5      ; increment a0 to 5
ANDI zero, zero, 0  ; set zero to 0
NOT t0, zero        ; store 1 in t0
SW t0, LEDR(zero)   ; turn on LEDR
SW a0, HEX(zero)    ; show 5 on HEX

ANDI a1, a1, 0      ; set a1 to 0
ADDI a1, a1, 0x100  ; set a1 to 0x100

LOOP:
ADDI a0, a0, 1      ; increment a0 by 1
BNE a0, a1, LOOP    ; loop till a0 = 0x100

SW a0, HEX(zero)    ; show 0x100 on HEX

END:
BR END