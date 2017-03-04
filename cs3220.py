import re
from lc2200 import Instruction

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
REGISTER_WIDTH = 4

# Immediate value width
IMMEDIATE_WIDTH = BIT_WIDTH - PRIMARY_OPCODE_WIDTH - 2 - (2 * REGISTER_WIDTH)

REGISTERS = {
    'zero':   0,
    'a0':   1,
    'a1':   2,
    'a2':   3,
    'a3':   4,
    'rV':   4,
    't0':   5,
    't1':   6,
    's0':   7,
    's1':   8,
    's2':   9,
    # 'R10'   :   10,
    # 'R11'   :   11,
    # 'R12'   :   12,
    'fp':   13,
    'sp':   14,
    'ra':   15
}

SYMBOL_TABLE, ALIASES = {}, {}

__R_BLANK_BITS__ = BIT_WIDTH - (PRIMARY_OPCODE_WIDTH + SECONDARY_OPCODE_WIDTH + 3 * REGISTER_WIDTH)
__IMM_BLANK_BITS__ = BIT_WIDTH - (PRIMARY_OPCODE_WIDTH + IMMEDIATE_WIDTH + 2 * REGISTER_WIDTH)

__RE_BLANK__ = re.compile(r'^\s*(;.*)?$')
__RE_PARTS__ = re.compile(
    r'^\s*((?P<Label>\w+):)?\s*((?P<Opcode>\.?[\w]+)(?P<Operands>[^;]*))?(;.*)?')
__RE_HEX__ = re.compile(r'0x[A-z0-9]*')
__RE_IMM__ = re.compile(
    r'^\s*(?P<RS>\w+?)\s*,\s*(?P<RT>\w+?)\s*,\s*(?P<Immediate>\S+?)\s*$')
__RE_R__ = re.compile(
    r'^\s*(?P<RD>\w+?)\s*,\s*(?P<RS>\w+?)\s*,\s*(?P<RT>\S+?)\s*$')
__RE_MEM_JMP__ = re.compile(
    r'^\s*(?P<RT>\w+?)\s*,\s*(?P<Immediate>\S+?)\s*\((?P<RS>\w+?)\)\s*$')

def receive_params(value_table):
    if value_table:
        raise RuntimeError('Custom parameters are not supported')


def is_blank(line):
    return __RE_BLANK__.match(line) is not None


def get_parts(line):
    """Break an instruction into Opcode, Operands and Label"""
    m = __RE_PARTS__.match(line)

    try:
        return (m.group('Label'), m.group('Opcode'), m.group('Operands'))
    except Exception as e:
        return None


def instruction_class(name):
    """Translate a given instruction name to its corresponding class name."""
    return ALIASES.get(name, name)


def __zero_extend__(binary, target, pad_right=False):
    if binary.startswith('0b'):
        binary = binary[2:]

    zeros = '0' * (target - len(binary))

    if pad_right:
        return binary + zeros
    else:
        return zeros + binary


def __sign_extend__(binary, target):
    if binary.startswith('0b'):
        binary = binary[2:]

    return binary[0] * (target - len(binary)) + binary


def __bin2hex__(binary):
    return '%0*X' % ((len(binary) + 3) // 4, int(binary, 2))


def __hex2bin(__hexadecimal):
    return bin(int(hexadecimal, 16))[2:]


def __dec2bin__(num, bits):
    """Compute the 2's complement binary of an int value."""
    return format(num if num >= 0 else (1 << bits) + num, '0{}b'.format(bits))


def __parse_value__(offset, size, pc=None):
    bin_offset = None

    if type(offset) is str:
        if pc is not None and offset in SYMBOL_TABLE:
            offset = SYMBOL_TABLE[offset] - (pc + 1)
        elif offset.startswith('0x'):
            try:
                bin_offset = __hex2bin__(offset)
            except:
                raise RuntimeError(
                    "'{}' is not in a valid hexadecimal format.".format(offset))

            if len(bin_offset) > size:
                raise RuntimeError(
                    "'{}' is too large for {}.".format(offset, __name__))

            bin_offset = __zero_extend__(bin_offset, size)
        elif offset.startswith('0b'):
            try:
                bin_offset = bin(int(offset))
            except:
                raise RuntimeError(
                    "'{}' is not in a valid binary format.".format(offset))

            if len(bin_offset) > size:
                raise RuntimeError(
                    "'{}' is too large for {}.".format(offset, __name__))

            bin_offset = __zero_extend__(bin_offset, size)

    # TODO: Ask Chris if this is correct
    if bin_offset is None:
        try:
            offset = int(offset)
        except:
            if pc is not None:
                raise RuntimeError(
                    "'{}' cannot be resolved as a label or a value.".format(offset))
            else:
                raise RuntimeError(
                    "'{}' cannot be resolved as a value.".format(offset))

        bound = 2**(size - 1)
        if offset < -bound or offset >= bound:
            raise RuntimeError(
                "'{}' is too large (values) or too far away (labels) for {}.".format(offset, __name__))

        bin_offset = __dec2bin__(offset, size)

    return bin_offset


def __parse_r__(operands):
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


def __parse_imm__(operands, is_br=False, pc=None):
    result_list = []

    match = __RE_IMM__.match(operands)

    if match is None:
        raise RuntimeError(
            "Operands '{}' are in an incorrect format.".format(operands.strip()))

    result_list.append(__parse_value__(match.group('Immediate'), IMMEDIATE_WIDTH, pc))

    for op in (match.group('RS'), match.group('RT')):
        if op in REGISTERS:
            result_list.append(__zero_extend__(
                bin(REGISTERS[op]), REGISTER_WIDTH))
        else:
            raise RuntimeError(
                "Register identifier '{}' is not valid in {}.".format(op, __name__))

    return ''.join(result_list)

def __parse_mem_jmp__(operands, pc=None):
    result_list = []

    match = __RE_MEM_JMP__.match(operands)

    if match is None:
        raise RuntimeError(
            "Operands '{}' are in an incorrect format.".format(operands.strip()))

    result_list.append(__parse_value__(match.group('Immediate'), IMMEDIATE_WIDTH, pc))

    for op in (match.group('RS'), match.group('RT')):
        if op in REGISTERS:
            result_list.append(__zero_extend__(
                bin(REGISTERS[op]), REGISTER_WIDTH))
        else:
            raise RuntimeError(
                "Register identifier '{}' is not valid in {}.".format(op, __name__))

    return ''.join(result_list)

class add(Instruction):
    @staticmethod
    def opcode():
        return (add.__primary_opcode__(), add.__secondary_opcode__())

    @staticmethod
    def size():
        return 1

    @staticmethod
    def __primary_opcode__():
        return 0;

    @staticmethod
    def __secondary_opcode__():
        return 2 ** 5

    @staticmethod
    def binary(operands, **kwargs):
        opcode = __zero_extend__(bin(add.__primary_opcode__()), PRIMARY_OPCODE_WIDTH) + __zero_extend__(bin(add.__secondary_opcode__()), SECONDARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + SECONDARY_OPCODE_WIDTH + __R_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)
        operands = __parse_r__(operands)
        return [opcode + operands]

    @staticmethod
    def hex(operands, **kwargs):
        return [__bin2hex(instr) for instr in add.binary(operands, **kwargs)]
