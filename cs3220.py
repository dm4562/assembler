import re

"""cs3220.py: A definition of the CS3220 architecture"""
__authors__ = "Dhruv Mehra and Christopher Tam"

# Architecture name
__name__ = 'CS-3220'

# Overall architecture width (bits)
BIT_WIDTH = 32

# Primary opcode width (bits)
PRIMARY_OPCODE_WIDTH = 6

# Secondary opcode width (bits)
SECONDARY_OPCODE_WIDTH = 8

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

_RE_BLANK_ = re.compile(r'^\s*(;.*)?$')
_RE_PARTS_ = re.compile(r'^\s*((?P<Label>\w+):)?\s*((?P<Opcode>\.?[\w]+)(?P<Operands>[^;]*))?(;.*)?')
_RE_HEX_ = re.compile(r'0x[A-z0-9]*')
_RE_IMM_ = re.compile(r'^\s*(?P<RD>\w+?)\s*,\s*(?P<RS>\w+?)\s*,\s*(?P<Offset>\S+?)\s*$')
_RE_R_ = re.compile(r'^\s*(?P<RD>\w+?)\s*,\s*(?P<RS>\w+?)\s*,\s*(?P<RT>\S+?)\s*$')
_RE_MEM_JMP_ = re.compile(r'^\s*(?P<RT>\w+?)\s*,\s*(?P<Offset>\S+?)\s*\((?P<RS>\w+?)\)\s*$')