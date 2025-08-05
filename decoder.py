

reg8bit = ['AL', 'CL', 'DL', 'BL', 'AH', 'CH', 'DH', 'BH'] ## if W = 0
reg16bit = ['AX', 'CX', 'DX', 'BX', 'SP', 'BP', 'SI', 'DI'] ## if W = 1
effective_addr = ['BX + SI', 'BX + DI', 'BP + SI', 'BP + DI', 'SI', 'DI', 'BP', 'BX']


opcodes = {
    0b100010: "MOV",
    0b1100011: "MOV",
    0b1011: "MOV",
    0b000000: "ADD",
    0b100000: "ADD",
    0b0000010: "ADD",
    0b001010: "SUB",
    0b100000: "SUB",
    0b0010110: "SUB",
    0b001110: "CMP",
    0b100000: "CMP",
    0b0011110: "CMP"
}

def match_opcode(byte:int):
    for pattern, instruction in opcodes.items():
        pattern_length = pattern.bit_length()
        mask = (1 << pattern_length) - 1
        extracted_bits = (byte >> (8 - pattern_length)) & mask
        if extracted_bits == pattern:
            return pattern, instruction
    
    return None, None

def process_mov_instruction(file:bytes, index : int, word:int, direction: int):
    rm_operand = 0
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
        case 0b01: 
            #print("Memory mode 8-bit")
            third_byte = file[index + 2]
            rm_operand = f"[{effective_addr[rm]} + {third_byte}]"
            bytes_consumed += 1
        case 0b10: 
            #print("Memory mode 16-bit")
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

def immediate_to_registermemory(file: bytes, index: int, word:int):

    bytes_consumed = 1
    second_byte = file[index + 1]
    bytes_consumed += 1
    mode = (second_byte >> 6) & 0b11
    rm = second_byte & 0b111 

    match mode:
        case 0b00: # No displacement except if R/M = 110 then 16-bit displacement
            if rm == 0b110:
                third_byte = file[index + 2]
                fourth_byte = file[index + 3]
                displacement = third_byte | (fourth_byte << 8)
                destination = f"[{displacement}]"
                bytes_consumed += 2
            else:
                destination = f"[{effective_addr[rm]}]"
        case 0b01: # Memory Mode, 8-bit displacement
            third_byte = file[index + 2]
            destination = f"[{effective_addr[rm]} + {third_byte}]"
            bytes_consumed += 1
        case 0b10: # Memory Mode, 16-bit displacement
            third_byte = file[index + 2]
            fourth_byte = file[index + 3]
            displacement = third_byte | (fourth_byte << 8)
            destination = f"[{effective_addr[rm]} + {displacement}]"
            bytes_consumed += 2
        case 0b11: # Register Mode, no displacement
            destination = reg16bit[rm] if word else reg8bit[rm]
        case _:
            print("something went wrong")
            destination = 0
    
    if word:  
        low_byte = file[index + bytes_consumed]
        high_byte = file[index + bytes_consumed + 1]
        source = low_byte | (high_byte << 8)  
        bytes_consumed += 2
    else:    
        source = file[index + bytes_consumed]
        bytes_consumed += 1
    
    return destination, source, bytes_consumed

def immediate_to_register(file: bytes, index: int, word:int):
    chunk = file[index]
    reg = chunk & 0b111        
    
    destination = reg16bit[reg] if word else reg8bit[reg]
    
    if word:  
        second_byte = file[index + 1]
        third_byte = file[index + 2]
        source = second_byte | (third_byte << 8)  
        bytes_consumed = 3  
    else:     
        second_byte = file[index + 1]
        source = second_byte
        bytes_consumed = 2 
    
    return destination, source, bytes_consumed

def parser(file_name: str):
    with open(file_name, 'rb') as f:
        file = f.read()
    index = 0 
    while index < len(file):
        chunk = file[index]
        pattern, instruction = match_opcode(chunk)
        direction = (chunk >> 1) & 0b1 
        word = chunk & 0b1 
        #print(f"Binary: {chunk:08b}")

        if pattern in (0b100010, 0b000000, 0b001010, 0b001110): ## 100010
            #print("matched: First row")
            destination, source, bytes_consumed = process_mov_instruction(file, index, word, direction)
            index += bytes_consumed
        elif pattern in (0b1100011, 0b100000):
            #print("matched: Second row")
            destination, source, bytes_consumed = immediate_to_registermemory(file, index, word)
            index += bytes_consumed
        elif pattern in (0b1011, 0b0000010, 0b0010110, 0b0011110):
            destination, source, bytes_consumed = immediate_to_registermemory(file, index, word)
            index += bytes_consumed
        else:
            #print("Unknown instruction")
            break




        print(instruction, str(destination) +",", str(source))
    return 1

if __name__=="__main__":
    size = 1
    listing37 = 'listing_0037_single_register_mov'
    listing38 = 'listing_0038_many_register_mov'
    listing39 = 'listing_0039_more_movs'
    listing41 = 'listing_0041_add_sub_cmp_jnz'
    file_name = listing39
    parser(file_name)
