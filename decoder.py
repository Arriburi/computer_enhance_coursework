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
effective_addr = ['BX + SI', 'BX + DI', 'BP + SI', 'BP + DI', 'SI', 'DI', 'BP', 'BX']


#def reg_to_reg(mode:int, reg:int, rm:int):
#    bytes_consumed = 0
#    return bytes_consumed
    
def process_mov_instruction(file:bytes, index : int, word:int, direction: int):
    bytes_consumed = 1
    second_byte = file[index + 1]
    bytes_consumed += 1

    mode = (second_byte >> 6) & 0b11
    reg = (second_byte >> 3) & 0b111  
    rm = second_byte & 0b111 

    reg_operand = reg16bit[reg] if word else reg8bit[reg]

    match mode:
        case 0b00: # No displacement except if R/M = 110 then 16-bit displacement
            if rm == 0b110:
                third_byte = file[index + 2]
                fourth_byte = file[index + 3]
                displacement = third_byte | (fourth_byte << 8)
                rm_operand = f"[{displacement}]"
                bytes_consumed += 2
            else:
                rm_operand = f"[{effective_addr[rm]}]"
        case 0b01: #Memory Mode, 8-bit
            print("Memory mode 8-bit")
            third_byte = file[index + 2]
            rm_operand = f"[{effective_addr[rm]} + {third_byte}]"
            bytes_consumed += 1
        case 0b10: # Memory Mode, 16-bit
            print("Memory mode 16-bit")
            third_byte = file[index + 2]
            fourth_byte = file[index + 3]
            displacement = third_byte | (fourth_byte << 8)
            rm_operand = f"[{effective_addr[rm]} + {displacement}]"
            bytes_consumed += 2
        case 0b11: # Register Mode, no displacement
            rm_operand = reg16bit[rm] if word else reg8bit[rm]
        case _: 
            print("something went wrong")

    if direction == 1:              # Memory/Register to Register
        source = rm_operand
        destination = reg_operand
    else:                           # Register to Memory/Register
        source = reg_operand
        destination = rm_operand
    
    
    return destination, source, bytes_consumed


def parser(file_name: str):
    with open(file_name, 'rb') as f:
        file = f.read()
    index = 0 
    while index < len(file):
        chunk = file[index]
        opcode = "MOV"    
        direction = (chunk >> 1) & 0b1 
        word = chunk & 0b1 
        print(f"Binary: {chunk:08b}")

        if (chunk & 0b11111100) == 0b10001000: ## 100010
            print("matched MOV")
            destination, source, bytes_consumed = process_mov_instruction(file, index, word, direction)
            index += bytes_consumed
        elif (chunk & 0b11111110) == 0b11000110:    ## 1100011x  
            print("matched MOV immediate to reg/mem")
            break
        elif (chunk & 0b11110000) == 0b10110000:    ## 1011xxxx
            print("matched MOV immediate to reg")
            word = (chunk >> 3) & 0b1
            reg = chunk & 0b111
            destination = reg16bit[reg] if word else reg8bit[reg]

            if word:  
                second_byte = file[index + 1]
                third_byte = file[index + 2]
                source = second_byte | (third_byte << 8)
                index += 3  
            else:     
                second_byte = file[index + 1]
                source = second_byte
                index += 2 
        else:
            print("Unknown instruction")
            break

        print(opcode, str(destination) +",", str(source))

    return 1


if __name__=="__main__":
    size = 1
    listing37 = 'listing_0037_single_register_mov'
    listing38 = 'listing_0038_many_register_mov'
    listing39 = 'listing_0039_more_movs'
    file_name = listing39
    parser(file_name)
