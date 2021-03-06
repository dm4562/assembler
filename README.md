# Assembler
A general 2-pass assembler with implementations of LC-2200 and LC3-2200a.

## Requirements
The assembler runs on any version of Python 2.6+.  An instruction set architecture definition file is required along with the assembler.  In this repository, several sample ISA definitions have been provided (see below).

## Sample Definitions
* [LC-2200 (32-bit)](lc2200.py)
* [LC3-2200a (32-bit)](lc32200a.py)
* [CS-3220 (32-bit)](cs3220.py)

## Options
The assembler contains multiple options.

`python assembler.py -h` prints:
```
usage: Assembles generic ISA-defined assembly code into hex or binary.
       [-h] [-i ISA] [-v] [-b] [-s SEPARATOR] [--sym] [--params PARAMS]
       asmfile

positional arguments:
  asmfile               the .asm file to be assembled

optional arguments:
  -h, --help            show this help message and exit
  -i ISA, --isa ISA     define the Python ISA module to load [default: cs3220]
  -v, --verbose         enable verbose printing of assembler
  --b, --bin            assemble code into binary (Quartus compatible)
  -s SEPARATOR, --separator SEPARATOR
                        the separator to use between instructions (accepts \s
                        for space and standard escape characters) [default:
                        \n]
  --sym, --symbols      output an additional file containing the assembled
                        program's symbol table
  --params PARAMS       custom parameters to pass to an architecture,
                        formatted as "key1=value1, key2=value2, key3=value3"

```

## How to Use
Typical usage:
```
python3 assmebler.py <assembly_file> -i <isa_definition>
```

Example usage with the `cs3220.py` definition:
```
python3 assmebler.py assembly.asm -i cs3220
```

To output assembled code in binary (compatible with *Quartus* images):
```
python3 assmebler.py assembly.s -i lc2200 --logisim
```

To separate entries by a space:
```
python3 assmebler.py assembly.s -i lc2200 --separator \s
```
