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

reg8bit = ['AL', 'CL', 'DL', 'BL', 'AH', 'CH', 'DH', 'BH'] ## if W = 0

reg16bit = ['AX', 'CX', 'DX', 'BX', 'SP', 'BP', 'SI', 'DI'] ## if W = 1

#def reg_to_reg(mode:int, reg:int, rm:int):
#    bytes_consumed = 0
#    return bytes_consumed
    
def memreg_to_reg(file:bytes, index : int, word:int):
    bytes_consumed = 1
    second_byte = file[index + 1]
    bytes_consumed += 1

    mode = (second_byte >> 6) & 0b11
    reg = (second_byte >> 3) & 0b111  
    rm = second_byte & 0b111 

    match mode:
        case 0b00:
            print("No displacement except if R/M = 110 then 16-bit displacement")
        case 0b01:
            print("Memory Mode, 8-bit")
        case 0b10:
            print("Memory mode, 16-bit")
        case 0b11:
            print("Register Mode, no displacement")
            if word:
                source = reg16bit[reg]
                destination = reg16bit[rm]
            else:
                source = reg8bit[reg]
                destination = reg8bit[rm]
        case _: 
            print("something went wrong")

    return  source, destination, bytes_consumed

def reg_to_memreg(file:bytes, index : int, word:int):
    bytes_consumed = 1
    second_byte = file[index + 1]
    bytes_consumed += 1

    mode = (second_byte >> 6) & 0b11
    reg = (second_byte >> 3) & 0b111  
    rm = second_byte & 0b111 

    match mode:
        case 0b00:
            print("No displacement except if R/M = 110 then 16-bit displacement")
        case 0b01:
            print("Memory Mode, 8-bit")
        case 0b10:
            print("Memory mode, 16-bit")
        case 0b11:
            print("Register Mode, no displacement")
            if word:
                source = reg16bit[rm] 
                destination = reg16bit[reg]
            else:
                source = reg8bit[rm]
                destination = reg8bit[reg]
        case _: 
            print("something went wrong")

    return  source, destination, bytes_consumed


def parser(file_name: str):
    with open(file_name, 'rb') as f:
        file = f.read()
    index = 0 
    while index < len(file):
        chunk = file[index] 
        opcode = (chunk >> 2) & 0b111111      
        direction = (chunk >> 1) & 0b1 
        word = chunk & 0b1 
        print(f"Byte value: {chunk}, Binary: {chunk:08b}")

        match opcode, direction:
            case 0b100010, 1:
                print("MOV Memory/Register to Register")
                source, destination, bytes_consumed = memreg_to_reg(file, index, word)
                index += bytes_consumed
            case 0b100010, 0:
                print("MOV Register to Memory/Register")
                source, destination, bytes_consumed = reg_to_memreg(file, index, word)
                index += bytes_consumed
            case 0b1100011, _:
                print("MOV immediate to register/memory")
                index += 1 
            case 0b1011, _:
                print("MOV immediate to register")
                index += 1  
            case _:
                break
        print(Opcode(opcode).name, source, destination)
    return 1


if __name__=="__main__":
    size = 1
    listing37 = 'listing_0037_single_register_mov'
    listing38 = 'listing_0038_many_register_mov'
    listing39 = 'listing_0039_more_movs'
    file_name = listing38
    parser(file_name)
