## BYTE          BYTE 
## 6, 1, 1       2, 3, 3
## [101010|D|W]  [MOD|REG|R/M]
## OPCODE | DIRECTION | BYTE OR WORD
## MODE (should always be 11 for reg to reg for now) | REGISTER  | REGISTER / MEMORY

#bits 16

#mov cx, bx

from enum import Enum

class Opcode(Enum):
    MOV = 0b100010

class Registers0(Enum): ## if W = 0
    AL = 0b000
    CL = 0b001
    DL = 0b010
    BL = 0b011
    AH = 0b100
    CH = 0b101
    DH = 0b110
    BH = 0b111

class Registers1(Enum): # if W = 1
    AX = 0b000
    CX = 0b001
    DX = 0b010
    BX = 0b011
    SP = 0b100
    BP = 0b101
    SI = 0b110
    DI = 0b111


def decode(binary_chunk: str):
    
    opcode = binary_chunk[0:6]      ## type of instruction
    direction = binary_chunk[6]     ## register destination/source
    word = binary_chunk[7]          ## 8 bits or 16 bits
    mode = binary_chunk[8:10]       ## 11 register to register
    reg = binary_chunk[10:13]       ## register source/destination
    regmem = binary_chunk[13:16]    ## register source/destination

   ## print(f"OPCODE={opcode} D={direction} W={word} MOD={mode} REG={reg} RM={regmem}")

    if word == '0': 
        to_copy = binary_chunk[:8] ## BYTE
        registers = Registers0
    else:
        to_copy = binary_chunk ## WORD
        registers = Registers1

    if direction == '0': ## 0 Instruction source is specified in REG field 
        destination = registers(int(regmem, 2)).name
        source = registers(int(reg, 2)).name
    else: 
        destination = registers(int(reg, 2)).name
        source = registers(int(regmem, 2)).name    

    opcode_val = int(opcode, 2)
    instruction = Opcode(opcode_val)   

    print(instruction.name,  destination + ",", source)
  

    return 1

size = 2
with open('listing_0038_many_register_mov', 'rb') as file:
    while True:
        chunk = file.read(size)
        if not chunk:
            break
        binary_chunk = bin(int.from_bytes(chunk))[2:]
        decode(binary_chunk)


