import argparse
import os
import importlib

"""lc2200-as.py: Assembles LC-2200 code into hex or binary."""
__author__ = "Christopher Tam"


VERBOSE = False
FILE_NAME = ''
ISA = None

def verbose(s):
    if VERBOSE:
        print(s)
        
def error(line_number, message):
    print("Error {}:{}: {}.\n".format(FILE_NAME, line_number, message))

def pass1(file):
    verbose("Beginning Pass 1...\n")
    # use a program counter to keep track of addresses in the file
    pc = 0
    line_count = 1
    no_errors = True

    # Seek to beginning of file
    #f.seek(0)

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
        label, op, _ = ISA.get_parts(line)
        if label:
            if label in ISA.SYMBOL_TABLE:
                error(line_count, "label '{}' is defined more than once".format(label))
                no_errors = False
            else:
                ISA.SYMBOL_TABLE[label] = pc
                
        if op:
            try:
                pc += getattr(ISA, ISA.instruction_class(op)).size()
            except:
                error(line_count, "instruction '{}' is not defined in the current ISA".format(op))
                no_errors = False
                
        line_count += 1
        
    verbose("Finished Pass 1.\n")
        
    return no_errors


def pass2(input_file, use_hex):
    verbose("Beginning Pass 2:\n")

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

        _, op, operands = ISA.get_parts(line)
                
        if op:
            instr = getattr(ISA, ISA.instruction_class(op))
            assembled = None
            try:
                assembled = instr.hex(operands, pc) if use_hex else instr.binary(operands, pc)
                #print(op + ' ' + str(assembled))
            except Exception as e:
                error(line_count, str(e))
                success = False
            
            if assembled:
                results.extend(assembled)
                pc += instr.size()
            
        line_count += 1
    
    verbose("Finished Pass 2\n")
    return (success, results)

def separator(s):
    return s.replace('\s', ' ').encode().decode('unicode_escape')

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser('Assembles LC-2200 code into hex or binary.')
    parser.add_argument('asmfile', help='the .s file to be assembled')
    parser.add_argument('-i', '--isa', required=False, type=str, default='isa', help='define the Python ISA module to load [default: isa]')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose printing of assembler')
    parser.add_argument('--hex', '--logisim', action='store_true', help='assemble code into hexadecimal (Logisim-compatible)')
    parser.add_argument('-s', '--separator', required=False, type=separator, default=' ', help='the separator to use between instructions (accepts \s for space and standard escape characters) [default: \s]')
    # parser.add_argument('-o' '--opcode', nargs=1, type=int, default=4, help='the bit width of the opcodes')
    # parser.add_argument('-r' '--register', nargs=1, type=int, default=4, help='the bit width of the register identifiers')
    # parser.add_argument('-b' '--bits', nargs=1, type=int, default=32, help='the bit width of the architecture to assemble for')
    args = parser.parse_args()
    
    # Try to dynamically load ISA module
    try:
        ISA = importlib.import_module(args.isa)
    except:
        raise
        print("Error: Failed to load ISA definition module '{}'.\n".format(args.isa))
        exit(1)
        
    print("Assembling for {} architecture...".format(ISA.__name__))

    VERBOSE = args.verbose
    FILE_NAME = os.path.basename(args.asmfile)
    
    with open(args.asmfile, 'r') as read_file:
        if not pass1(read_file):
            print("Assemble failed.\n")
            exit(1)
        
        success, results = pass2(read_file, args.hex)
        if not success:
            print("Assemble failed.\n")
            exit(1)
        
    outFileName = os.path.splitext(args.asmfile)[0]
    outFileName += '.hex' if args.hex else '.bin'
    sep = args.separator
        
    print("Writing to {}...".format(outFileName))
        
    with open(outFileName, 'w') as write_file:
        for r in results:
            #print(r)
            write_file.write(r + sep)