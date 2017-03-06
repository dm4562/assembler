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
    'fp':   13,
    'sp':   14,
    'ra':   15
}

SYMBOL_TABLE = {}

ALIASES = {
    'and': 'and_',
    'or': 'or_',
    'not': 'not_'
}

__R_BLANK_BITS__ = BIT_WIDTH - \
    (PRIMARY_OPCODE_WIDTH + SECONDARY_OPCODE_WIDTH + 3 * REGISTER_WIDTH)
__IMM_BLANK_BITS__ = BIT_WIDTH - \
    (PRIMARY_OPCODE_WIDTH + IMMEDIATE_WIDTH + 2 * REGISTER_WIDTH)

__RE_BLANK__ = re.compile(r'^\s*(;.*)?$')
__RE_PARTS__ = re.compile(
    r'^\s*(\.(?P<Keyword>\w+)?\s*((?P<Key>\w+)\s*\=)?\s*(?P<Value>[^;\s]+))?\s*((?P<Label>\w+):)?\s*((?P<Opcode>\.?[\w]+)\s*(?P<Operands>[^;]*))?(;.*)?')
__RE_HEX__ = re.compile(r'0x[A-z0-9]*')
__RE_IMM__ = re.compile(
    r'(^\s*(?P<RS>\w+?)\s*,)?\s*((?P<RT>\w+?)?\s*,)?\s*(?P<Immediate>\S+?)\s*$')
__RE_R__ = re.compile(
    r'^\s*(?P<RD>\S+?)\s*,\s*(?P<RS>\S+?)\s*(,\s*(?P<RT>\S+?))?\s*$')
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
        return (m.group('Keyword'), m.group('Key'), m.group('Value'), m.group('Label'), m.group('Opcode'), m.group('Operands'))
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


def __hex2bin__(hexadecimal):
    return bin(int(hexadecimal, 16))[2:]


def __dec2bin__(num, bits):
    """Compute the 2's complement binary of an int value."""
    binary = format(num if num >= 0 else (
        1 << bits) + num, '0{}b'.format(bits))
    return binary if len(binary) <= bits else binary[-bits:]


def __parse_value__(offset, size, pc=None, jmp=False):
    bin_offset = None

    if type(offset) is str:
        if jmp and offset in SYMBOL_TABLE:
            # assert(rs is not None)
            offset = SYMBOL_TABLE[offset]
        elif pc is not None and offset in SYMBOL_TABLE:
            offset = SYMBOL_TABLE[offset] - (pc + 1)
        elif offset.startswith('0x'):
            try:
                offset = int(offset, 16)
            except Exception:
                raise RuntimeError("'{}' is not valid hexadecimal format")
        elif offset.startswith('0b'):
            try:
                offset = int(offset, 2)
            except Exception:
                raise RuntimeError("'{}' is not valid binary format")
    try:
        offset = int(offset)
    except Exception:
        if pc is not None:
            raise RuntimeError(
                "'{}' cannot be resolved as a label or a value.".format(offset))
        else:
            raise RuntimeError(
                "'{}' cannot be resolved as a value.".format(offset))

    bin_offset = __dec2bin__(offset, size)

    return bin_offset


def __parse_mem_value__(offset, size=IMMEDIATE_WIDTH):
    bin_offset = None

    if offset in SYMBOL_TABLE:
        offset = SYMBOL_TABLE[offset]
    elif offset.startswith('0x'):
        try:
            offset = int(offset, 16)
        except Exception:
            raise RuntimeError("'{}' is not valid hexadecimal format")
    elif offset.startswith('0b'):
        try:
            offset = int(offset, 2)
        except Exception:
            raise RuntimeError("'{}' is not a valid binary format")

    try:
        offset = int(offset)
    except Exception:
        raise RuntimeError("'{}' cannot be resolved".format(offset))

    bin_offset = __dec2bin__(offset, size)

    return bin_offset


def __parse_r__(operands):
    result_list = []

    match = __RE_R__.match(operands)

    if match is None:
        raise RuntimeError(
            "Operands '{}' are in an incorrect format.".format(operands.strip()))

    for op in (match.group('RD'), match.group('RS'), match.group('RT')):
        if not op:
            result_list.append(None)
            continue

        if op in REGISTERS:
            result_list.append(__zero_extend__(
                bin(REGISTERS[op])[2:], REGISTER_WIDTH))
        else:
            raise RuntimeError(
                "Register identifier '{}' is not valid in {}.".format(op, __name__))

    return tuple(result_list)


def __parse_imm__(operands, is_br=False, pc=None):
    result_list = []

    match = __RE_IMM__.match(operands)

    if match is None:
        raise RuntimeError(
            "Operands '{}' are in an incorrect format.".format(operands.strip()))

    result_list.append(__parse_value__(
        match.group('Immediate'), IMMEDIATE_WIDTH, pc))

    for op in (match.group('RS'), match.group('RT')):
        if not op:
            result_list.append(None)
            continue

        if op in REGISTERS:
            result_list.append(__zero_extend__(
                bin(REGISTERS[op]), REGISTER_WIDTH))
        else:
            raise RuntimeError(
                "Register identifier '{}' is not valid in {}.".format(op, __name__))

    return tuple(result_list)


def __parse_mem_jmp__(operands, pc=None, mem=False):
    result_list = []

    match = __RE_MEM_JMP__.match(operands)

    if match is None:
        raise RuntimeError(
            "Operands '{}' are in an incorrect format.".format(operands.strip()))

    if mem:
        result_list.append(__parse_mem_value__(match.group('Immediate')))
    else:
        result_list.append(__parse_value__(match.group(
            'Immediate'), size=IMMEDIATE_WIDTH, pc=pc, jmp=True))

    for op in (match.group('RS'), match.group('RT')):
        if op in REGISTERS:
            result_list.append(__zero_extend__(
                bin(REGISTERS[op]), REGISTER_WIDTH))
        else:
            raise RuntimeError(
                "Register identifier '{}' is not valid in {}.".format(op, __name__))

    return ''.join(result_list)


class RInstruction(Instruction):

    @classmethod
    def opcode(cls):
        return (cls.primary_opcode(), RInstruction.secondary_opcode())

    @classmethod
    def size(cls):
        return 1

    @classmethod
    def primary_opcode(cls):
        return 0

    @classmethod
    def secondary_opcode(cls):
        raise NotImplementedError()

    @classmethod
    def build_operands(cls, operands):
        return ''.join(__parse_r__(operands))

    @classmethod
    def binary(cls, operands, **kwargs):
        opcode = __zero_extend__(bin(cls.primary_opcode()), PRIMARY_OPCODE_WIDTH) + \
            __zero_extend__(bin(cls.secondary_opcode()),
                            SECONDARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + SECONDARY_OPCODE_WIDTH + __R_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)
        operands = cls.build_operands(operands)
        return [opcode + operands]

    @classmethod
    def hex(cls, operands, **kwargs):
        return [__bin2hex__(instr) for instr in cls.binary(operands, **kwargs)]


class eq(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('08', 16)


class lt(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('09', 16)


class le(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('0a', 16)


class ne(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('0b', 16)


class add(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('20', 16)


class and_(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('24', 16)


class or_(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('25', 16)


class xor(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('26', 16)


class sub(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('28', 16)


class nand(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('2c', 16)


class nxor(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('2e', 16)


class rshf(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('30', 16)


class lshf(RInstruction):

    @classmethod
    def secondary_opcode(cls):
        return int('31', 16)


class IInstruction(Instruction):

    @classmethod
    def opcode(cls):
        raise NotImplementedError()

    @classmethod
    def size(cls):
        return 1

    @classmethod
    def build_operands(cls, operands, pc=None):
        return ''.join(__parse_imm__(operands, pc=pc))

    @classmethod
    def binary(cls, operands, **kwargs):
        opcode = __zero_extend__(bin(cls.opcode()), PRIMARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + __IMM_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)
        operands = cls.build_operands(operands)
        return [opcode + operands]

    @classmethod
    def hex(cls, operands, **kwargs):
        return [__bin2hex__(instr) for instr in cls.binary(operands, **kwargs)]


class beq(IInstruction):

    @classmethod
    def opcode(cls):
        return int('001000', 2)

    @classmethod
    def build_operands(cls, operands, pc=None):
        return ''.join(__parse_imm__(operands, pc=pc))

    @classmethod
    def binary(cls, operands, **kwargs):
        assert('pc' in kwargs)  # Sanity check

        opcode = __zero_extend__(bin(cls.opcode()), PRIMARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + __IMM_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)
        operands = cls.build_operands(operands, pc=kwargs['pc'])
        return [opcode + operands]


class blt(IInstruction):

    @classmethod
    def opcode(cls):
        return int('001001', 2)

    @classmethod
    def build_operands(cls, operands, pc=None):
        return ''.join(__parse_imm__(operands, pc=pc))

    @classmethod
    def binary(cls, operands, **kwargs):
        assert('pc' in kwargs)  # Sanity check

        opcode = __zero_extend__(bin(cls.opcode()), PRIMARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + __IMM_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)
        operands = cls.build_operands(operands, pc=kwargs['pc'])
        return [opcode + operands]


class ble(IInstruction):

    @classmethod
    def opcode(cls):
        return int('001010', 2)

    @classmethod
    def build_operands(cls, operands, pc=None):
        return ''.join(__parse_imm__(operands, pc=pc))

    @classmethod
    def binary(cls, operands, **kwargs):
        assert('pc' in kwargs)  # Sanity check

        opcode = __zero_extend__(bin(cls.opcode()), PRIMARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + __IMM_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)
        operands = cls.build_operands(operands, pc=kwargs['pc'])
        return [opcode + operands]


class bne(IInstruction):

    @classmethod
    def opcode(cls):
        return int('001011', 2)

    @classmethod
    def build_operands(cls, operands, pc=None):
        return ''.join(__parse_imm__(operands, pc=pc))

    @classmethod
    def binary(cls, operands, **kwargs):
        assert('pc' in kwargs)  # Sanity check

        opcode = __zero_extend__(bin(cls.opcode()), PRIMARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + __IMM_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)
        operands = cls.build_operands(operands, pc=kwargs['pc'])
        return [opcode + operands]


class beq(IInstruction):

    @classmethod
    def opcode(cls):
        return int('001000', 2)

    @classmethod
    def build_operands(cls, operands, pc=None):
        return ''.join(__parse_imm__(operands, pc=pc))

    @classmethod
    def binary(cls, operands, **kwargs):
        assert('pc' in kwargs)  # Sanity check

        opcode = __zero_extend__(bin(cls.opcode()), PRIMARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + __IMM_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)
        operands = cls.build_operands(operands, pc=kwargs['pc'])
        return [opcode + operands]


class addi(IInstruction):

    @classmethod
    def opcode(cls):
        return int('100000', 2)


class andi(IInstruction):

    @classmethod
    def opcode(cls):
        return int('100100', 2)


class ori(IInstruction):

    @classmethod
    def opcode(cls):
        return int('100101', 2)


class xori(IInstruction):

    @classmethod
    def opcode(cls):
        return int('100110', 2)


class jal(IInstruction):

    @classmethod
    def opcode(cls):
        return int('001100', 2)

    @classmethod
    def binary(cls, operands, **kwargs):
        assert('pc' in kwargs)  # sanity check

        opcode = __zero_extend__(bin(cls.opcode()), PRIMARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + __IMM_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)

        operands = __parse_mem_jmp__(operands, pc=kwargs['pc'])
        return [opcode + operands]


class lw(IInstruction):

    @classmethod
    def opcode(cls):
        return int('010010', 2)

    @classmethod
    def binary(cls, operands, **kwargs):
        opcode = __zero_extend__(bin(cls.opcode()), PRIMARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + __IMM_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)

        operands = __parse_mem_jmp__(operands, mem=True)
        return [opcode + operands]


class sw(IInstruction):

    @classmethod
    def opcode(cls):
        return int('011010', 2)

    @classmethod
    def binary(cls, operands, **kwargs):
        opcode = __zero_extend__(bin(cls.opcode()), PRIMARY_OPCODE_WIDTH)
        length = PRIMARY_OPCODE_WIDTH + __IMM_BLANK_BITS__
        opcode = __zero_extend__(opcode, length, pad_right=True)

        operands = __parse_mem_jmp__(operands, mem=True)
        return [opcode + operands]

class not_(nand):
    @classmethod
    def build_operands(cls, operands):
        rd, rs, rt = __parse_r__(operands)
        return ''.join((rd, rs, rs))

class ge(le):
    @classmethod
    def build_operands(cls, operands):
        rd, rs, rt = __parse_r__(operands)
        return ''.join((rd, rt, rs))

class gt(lt):
    @classmethod
    def build_operands(cls, operands):
        rd, rs, rt = __parse_r__(operands)
        return ''.join((rd, rt, rs))