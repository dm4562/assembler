import re

"""cs3220.py: A definition of the CS3220 architecture"""
__authors__ = "Dhruv Mehra and Christopher Tam"

# Architecture name
__name__ = 'CS-3220'

# Overall architecture width (bits)
BIT_WIDTH = 32

# Primary opcode width (bits)
PRIMARY_OPCODE_WIDTH = 4

# Secondary opcode width (bits)
SECONDARY_OPCODE_WIDTH = 4

# Register width (bits)
REGISTERS = {
    'zero'  :   0,
    'A0'    :   1,
    'A1'    :   2,
    'A2'    :   3,
    'A3'    :   4,
    'RV'    :   4,
    'T0'    :   5,
    'T1'    :   6,
    'S0'    :   7,
    'S1'    :   8,
    'S2'    :   9,
    # 'R10'   :   10,
    # 'R11'   :   11,
    # 'R12'   :   12,
    'FP'    :   13,
    'SP'    :   14,
    'RA'    :   15
}

__RE_BLANK__ = re.compile(r'^\s*(!.*)?$')