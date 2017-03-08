#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
import importlib
import operator
import re
import traceback

"""assembler.py: General, modular 2-pass assembler accepting ISA definitions to assemble code."""
__authors__ = "Christopher Tam and Dhruv Mehra"


VERBOSE = False
FILE_NAME = ''
ISA = None
RE_PARAMS = re.compile('^(?P<key>.+)=(?P<value>.+)$')


def verbose(s):
    if VERBOSE:
        print(s)


def error(line_number, message):
    print("Error {}:{}: {}.\n".format(FILE_NAME, line_number, message))


def pass1(file):
    verbose("\nBeginning Pass 1...\n")
    # use a program counter to keep track of addresses in the file
    pc = 0
    line_count = 1
    no_errors = True

    for line in file:
        # Skip blank lines and comments
        if ISA.is_blank(line):
            verbose(line)
            continue

        # Trim any leading and trailing whitespace
        line = line.strip()

        verbose('{}: {}'.format(pc, line))

        # Make line case-insensitive
        line = line.lower()

        # Parse line
        keyword, key, val, label, op, _ = ISA.get_parts(line)

        if keyword and op:
            error(line_number,
                  "Cannot have {} and {} in the same line".format(op, keyword))
            success = False

        if keyword == 'orig':
            # Sanity check
            if not val:
                error(line_count, "{} is not valid format for {}".format(keyword, val))
                success = False

            try:
                if val.startswith('0x'):
                    pc = int(val, 16)
                elif val.startswith('0b'):
                    pc = int(val, 2)
                else:
                    pc = int(val)

            except ValueError as e:
                error(line_count, "{} is not a valid number format".format(val))
                no_errors = False

        if label:
            if label in ISA.SYMBOL_TABLE:
                error(line_count, "label '{}' is defined more than once".format(label))
                no_errors = False
            else:
                ISA.SYMBOL_TABLE[label] = pc

        if keyword and key:
            if key in ISA.SYMBOL_TABLE:
                error(line_count, "label '{}' is defined more than once".format(key))
                no_errors = False
            else:
                try:
                    if val.startswith('0x'):
                        ISA.SYMBOL_TABLE[key] = int(val, 16)
                    elif val.startswith('0b'):
                        ISA.SYMBOL_TABLE[key] = int(val, 2)
                    else:
                        ISA.SYMBOL_TABLE[key] = int(val)
                except ValueError as e:
                    error(line_count, "{} is not a valid number format".format(val))
                    no_errors = False

        if keyword == 'word':
            try:
                pc += (getattr(ISA, ISA.instruction_class(keyword)).size()
                       * ISA.INSTRUCTION_OFFSET)
            except Exception as e:
                error(
                    line_count, "instruction '{}' is not defined in the current ISA".format(keyword))
                no_errors = False
        if op:
            try:
                pc += (getattr(ISA, ISA.instruction_class(op)).size()
                       * ISA.INSTRUCTION_OFFSET)
            except Exception as e:
                error(
                    line_count, "instruction '{}' is not defined in the current ISA".format(op))
                no_errors = False

        line_count += 1

    verbose("\nFinished Pass 1.\n")

    return no_errors


def pass2(input_file, use_hex):
    verbose("\nBeginning Pass 2...\n")

    pc = 0
    line_count = 1
    success = True
    results = []

    # Seek to beginning of file
    input_file.seek(0)

    for line in input_file:
        # Skip blank lines and comments
        if ISA.is_blank(line):
            verbose(line)
            continue

        # Trim any leading and trailing whitespace
        line = line.strip()

        verbose('{}: {}'.format(pc, line))

        # Make line case-insensitive
        line = line.lower()

        keyword, key, val, _, op, operands = ISA.get_parts(line)

        if keyword and op:
            error(line_number,
                  "Cannot have {} and {} in the same line".format(op, keyword))
            success = False

        if keyword == 'orig':
            # Sanity check
            if not val:
                error(line_count, "{} is not valid format for {}".format(keyword, val))
                success = False

            try:
                if val.startswith('0x'):
                    pc = int(val, 16)
                elif val.startswith('0b'):
                    pc = int(val, 2)
                else:
                    pc = int(val)

            except ValueError as e:
                error(line_count, "{} is not a valid number format".format(val))
                success = False

        if keyword == 'word':
            instr = getattr(ISA, ISA.instruction_class(keyword))
            assembled = None

            if not val:
                error(line_count, "{} is not valid format for {}".format(keyword, val))
                success = False

            try:
                if use_hex:
                    assembled = instr.hex(val, pc=pc, instruction=keyword)
                else:
                    assembled = instr.binary(val, pc=pc, instruction=keyword)
            except Exception as e:
                error(line_count, str(e))
                success = False

            if assembled:
                results.extend([(pc + (i * ISA.INSTRUCTION_OFFSET), instr)
                                for i, instr in enumerate(assembled)])
                pc += (instr.size() * ISA.INSTRUCTION_OFFSET)

        elif op:
            instr = getattr(ISA, ISA.instruction_class(op))
            assembled = None
            try:
                if use_hex:
                    assembled = instr.hex(operands, pc=pc, instruction=op)
                else:
                    assembled = instr.binary(operands, pc=pc, instruction=op)
            except Exception as e:
                error(line_count, str(e))
                success = False

            if assembled:
                results.extend([(pc + (i * ISA.INSTRUCTION_OFFSET), instr)
                                for i, instr in enumerate(assembled)])
                pc += (instr.size() * ISA.INSTRUCTION_OFFSET)

        line_count += 1

    verbose("\nFinished Pass 2.\n")
    return (success, results)


def separator(s):
    return s.replace('\s', ' ').encode().decode('unicode_escape')


def parse_params(values):
    if values is None:
        return None

    parsed = {}
    values = values.split(',')

    for val in values:
        m = RE_PARAMS.match(val)
        if m is None:
            print("Error: '{}' is not a valid custom parameter".format(val))
            exit(1)

        parsed[m.group('key')] = m.group('value')

    return parsed


def build_hex(number, width):
    return "{0:0{1}X}".format(number, width)

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(
        'assembler.py', description='Assembles generic ISA-defined assembly code into hex or binary.')
    parser.add_argument('asmfile', help='the .s file to be assembled')
    parser.add_argument('-i', '--isa', required=False, type=str, default='isa',
                        help='define the Python ISA module to load [default: isa]')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable verbose printing of assembler')
    parser.add_argument('--bin', '--logisim', action='store_true', default=False,
                        help='assemble code into binary (Not compatible with .mif format)')
    parser.add_argument('-s', '--separator', required=False, type=separator, default='\\n',
                        help='the separator to use between instructions (accepts \s for space and standard escape characters) [default: \\n]')
    parser.add_argument('--sym', '--symbols', action='store_true',
                        help="output an additional file containing the assembled program's symbol table")
    parser.add_argument('--params', required=False, type=str,
                        help='custom parameters to pass to an architecture, formatted as "key1=value1, key2=value2, key3=value3"')
    args = parser.parse_args()

    # Try to dynamically load ISA module
    try:
        ISA = importlib.import_module(args.isa)
    except Exception as e:
        print("Error: Failed to load ISA definition module '{}'. {}\n".format(
            args.isa, str(e)))
        exit(1)

    print("Assembling for {} architecture...".format(ISA.__name__))

    # Pass in custom parameters
    try:
        ISA.receive_params(parse_params(args.params))
    except Exception as e:
        print("Error: Failed to parse custom parameters for {}. {}\n".format(
            ISA.__name__, str(e)))
        exit(1)

    VERBOSE = args.verbose
    FILE_NAME = os.path.basename(args.asmfile)

    with open(args.asmfile, 'r') as read_file:
        if not pass1(read_file):
            print("Assemble failed.\n")
            exit(1)

        success, results = pass2(read_file, not args.bin)
        if not success:
            print("Assemble failed.\n")
            exit(1)

    outFileName = os.path.splitext(args.asmfile)[0]
    code_ext = '.bin' if args.bin else '.mif'
    sep = args.separator

    if args.sym:
        sym_ext = '.sym'
        print("Writing symbol table to {}...".format(
            outFileName + sym_ext), end="")

        sym_sorted = sorted(ISA.SYMBOL_TABLE.items(),
                            key=operator.itemgetter(1))

        with open(outFileName + sym_ext, 'w') as write_file:
            for (symbol, addr) in sym_sorted:
                write_file.write("{}: {}\n".format(symbol, hex(addr)))

        print('done!')

    print("Writing to {}...".format(outFileName + code_ext), end="")

    with open(outFileName + code_ext, 'w') as write_file:
        mem_size = 2048
        data_radix = 'BIN' if args.bin else 'HEX'
        write_file.write("WIDTH={};{}".format(ISA.BIT_WIDTH, sep))
        write_file.write("DEPTH={};{}".format(mem_size, sep))
        write_file.write("ADDRESS_RADIX={};{}".format('HEX', sep))
        write_file.write("DATA_RADIX={};{}".format(data_radix, sep))
        write_file.write("CONTENT BEGIN{}".format(sep))

        pre_mem = -1
        for pc, instr in results:
            mem_addr = pc // ISA.INSTRUCTION_OFFSET

            if pre_mem + 1 != mem_addr:
                write_file.write("[{}..{}] : {};{}".format(
                    build_hex(pre_mem + 1, 8), build_hex(mem_addr - 1, 8), 'DEAD', sep))

            write_file.write("-- @ 0x{}{}".format(build_hex(pc, 8), sep))
            write_file.write("{} : {};{}".format(
                build_hex(mem_addr, 8), instr, sep))
            pre_mem = mem_addr

        if pre_mem < mem_size:
            write_file.write("[{}..{}] : {};{}".format(
                build_hex(pre_mem + 1, 8), build_hex(mem_size, 8), 'DEAD', sep))

        write_file.write("END;")

    print('done!')
