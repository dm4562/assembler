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
    'zero':   0,
    'A0':   1,
    'A1':   2,
    'A2':   3,
    'A3':   4,
    'RV':   4,
    'T0':   5,
    'T1':   6,
    'S0':   7,
    'S1':   8,
    'S2':   9,
    # 'R10'   :   10,
    # 'R11'   :   11,
    # 'R12'   :   12,
    'FP':   13,
    'SP':   14,
    'RA':   15
}

__RE_BLANK = re.compile(r'^\s*(;.*)?$')
__RE_PARTS = re.compile(
    r'^\s*((?P<Label>\w+):)?\s*((?P<Opcode>\.?[\w]+)(?P<Operands>[^;]*))?(;.*)?')
__RE_HEX = re.compile(r'0x[A-z0-9]*')
__RE_IMM = re.compile(
    r'^\s*(?P<RD>\w+?)\s*,\s*(?P<RS>\w+?)\s*,\s*(?P<Offset>\S+?)\s*$')
__RE_R = re.compile(
    r'^\s*(?P<RD>\w+?)\s*,\s*(?P<RS>\w+?)\s*,\s*(?P<RT>\S+?)\s*$')
__RE_MEM_JMP = re.compile(
    r'^\s*(?P<RT>\w+?)\s*,\s*(?P<Offset>\S+?)\s*\((?P<RS>\w+?)\)\s*$')


def is_blank(line):
    return __RE_BLANK.match(line) is not None


def get_parts(line):
    """Break an instruction into Opcode, Operands and Label"""
    m = __RE_PARTS.match(line)

    try:
        return (m.group('Label'), m.group('Opcode'), m.group('Operands'))
    except Exception as e:
        return None


def __zero_extend(binary, target, pad_right=False):
    if binary.startswith('0b'):
        bunary = bunary[2:]

    zeros = '0' * (target - len(binary))

    if pad_right:
        return binary + zeros
    else:
        return zeros + binary


def __sign_extend(binary, target):
    if binary.startswith('0b'):
        binary = binary[2:]

    return binary[0] * (target - len(binary)) + binary


def __bin2hex(binary):
    return '%0*X' % ((len(binary) + 3) // 4, int(binary, 2))


def __hex2bin(hexadecimal):
    return bin(int(hexadecimal, 16))[2:]


def __dec2bin(num, bits):
    """Compute the 2's complement binary of an int value."""
    return format(num if num >= 0 else (1 << bits) + num, '0{}b'.format(bits))


def __parse_r(operands):
    result_list = []

    match = __RE_R__.match(operands)

    if match is None:
        raise RuntimeError(
            "Operands '{}' are in an incorrect format.".format(operands.strip()))

    for op in (match.group('RD'), match.group('RS'), match.group('RT')):
        if op in REGISTERS:
            result_list.append(__zero_extend__(
                bin(REGISTERS[op])[2:], REGISTER_WIDTH))
        else:
            raise RuntimeError(
                "Register identifier '{}' is not valid in {}.".format(op, __name__))

    return ''.join(result_list)


def __parse_i__(operands, is_mem=False, pc=None):
    # Define result
    result_list = []

    match = __RE_MEM__.match(operands) if is_mem else __RE_I__.match(operands)

    if match is None:
        raise RuntimeError(
            "Operands '{}' are in an incorrect format.".format(operands.strip()))

    for op in (match.group('RX'), match.group('RY')):
        if op in REGISTERS:
            result_list.append(__zero_extend__(
                bin(REGISTERS[op]), REGISTER_WIDTH))
        else:
            raise RuntimeError(
                "Register identifier '{}' is not valid in {}.".format(op, __name__))

    result_list.append(__parse_value__(
        match.group('Offset'), __OFFSET_SIZE__, pc))

    return ''.join(result_list)


def __parse_j__(operands):
    # Define result
    result_list = []

    match = __RE_J__.match(operands)

    if match is None:
        raise RuntimeError(
            "Operands '{}' are in an incorrect format.".format(operands.strip()))

    for op in (match.group('RX'), match.group('RY')):
        if op in REGISTERS:
            result_list.append(__zero_extend__(
                bin(REGISTERS[op]), REGISTER_WIDTH))
        else:
            raise RuntimeError(
                "Register identifier '{}' is not valid in {}.".format(op, __name__))

    return ''.join(result_list)
