

reg8bit = ['AL', 'CL', 'DL', 'BL', 'AH', 'CH', 'DH', 'BH'] ## if W = 0
reg16bit = ['AX', 'CX', 'DX', 'BX', 'SP', 'BP', 'SI', 'DI'] ## if W = 1
effective_addr = ['BX + SI', 'BX + DI', 'BP + SI', 'BP + DI', 'SI', 'DI', 'BP', 'BX']

jumps = {
    0b01110101: 'JNZ',
    0b01110100: 'JE',
    0b01111100: 'JL',
    0b01111110: 'JLE',
    0b01110010: 'JB',
    0b01110110: 'JBE',
    0b01111010: 'JP',
    0b01110000: 'JO',
    0b01111000: 'JS',
    0b01111101: 'JNL',
    0b01111111: 'JG',
    0b01110011: 'JNB',
    0b01110111: 'JA',
    0b01111011: 'JNP',
    0b01110001: 'JNO',
    0b01111001: 'JNS',
    0b11100010: 'LOOP',
    0b11100001: 'LOOPZ',
    0b11100000: 'LOOPNZ',
    0b11100011: 'JCXZ'
}

opcodes = {
    0b100010: ("MOV", 6),
    0b1100011: ("MOV", 7),
    0b1011: ("MOV", 4),
    0b000000: ("ADD", 6),
    0b100000: ("SPECIAL", 6),
    0b0000010: ("ADD", 7),
    0b001010: ("SUB", 6),
    0b0010110: ("SUB", 7),
    0b001110: ("CMP", 6),
    0b0011110: ("CMP", 7)
}

def match_opcode(byte:int):
    for pattern, (instruction, pattern_length) in opcodes.items():
        mask = (1 << pattern_length) - 1
        extracted_bits = (byte >> (8 - pattern_length)) & mask
        
        if extracted_bits == pattern:
            return pattern, instruction
    
    for jump_pattern, jump_instruction in jumps.items():
        if byte == jump_pattern:
            return jump_pattern, jump_instruction
    
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

def immediate_to_registermemory(file: bytes, index: int, word:int, pattern: int):
    w = ""
    bytes_consumed = 1
    second_byte = file[index + 1]
    bytes_consumed += 1
    mode = (second_byte >> 6) & 0b11
    rm = second_byte & 0b111    
    reg = (second_byte >> 3) & 0b111
    instruction = 'ERROR'

    if pattern == 0b1100011 and reg == 0b000:
        instruction = 'MOV' 
    elif reg == 0b000:
        instruction = 'ADD'
    elif reg == 0b101:
        instruction = 'SUB'
    elif reg == 0b111:  
        instruction = 'CMP'

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
    
    if pattern == 0b100000:  # Only ADD, SUB, CMP have 's' bit
        s = (file[index] >> 1) & 0b1
        if s == 1 and word == 1:
            imm8 = file[index + bytes_consumed]
            if imm8 & 0b10000000:
                source = imm8 | 0b1111111100000000
            else:
                source = imm8
            bytes_consumed += 1  # ← Fixed: moved outside the if/else
            
            # Apply the same prefix logic here too
            if '[' in str(destination) and ']' in str(destination):
                w = "word "
            else:
                w = ""
            return instruction, w + str(destination), source, bytes_consumed  

    if word == 1:
        low_byte = file[index + bytes_consumed]
        high_byte = file[index + bytes_consumed + 1]
        source = low_byte | (high_byte << 8)
        bytes_consumed += 2
    else:
        source = file[index + bytes_consumed]
        bytes_consumed += 1

    if '[' in str(destination) and ']' in str(destination):
        if word == 1:
            w = "word "
        else:
            w = "byte "
    else:
        w = ""  # No prefix for register destinations

    return instruction, w + str(destination), source, bytes_consumed


def immediate_to_register(file: bytes, index: int, word:int, pattern: int):
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

def immediate_accumulator(file: bytes, index: int, word:int, pattern: int):
    bytes_consumed = 0
    destination = 'mistake in defining destination for immediate accumulator'
    source = 'mistake in defining source for immediate accumulator'
    if pattern == 0b0000010: #Immediate to accumulator
        if word:
            destination = 'AX'
            second_byte = file[index + 1]
            third_byte = file[index + 2]
            source = second_byte | (third_byte << 8)  
            bytes_consumed = 3  
        else:
            destination = 'AL'
            second_byte = file[index + 1]
            source = second_byte
            bytes_consumed = 2 
    elif pattern == 0b0010110: #Immediate from accumulator
        if word:
            destination = 'AX'
            second_byte = file[index + 1]
            third_byte = file[index + 2]
            source = second_byte | (third_byte << 8)  
            bytes_consumed = 3  
        else:
            destination = 'AL'
            second_byte = file[index + 1]
            source = second_byte
            bytes_consumed = 2
    elif pattern == 0b0011110: #Immediate with accumulator
        if word:
            destination = 'AX'
            second_byte = file[index + 1]
            third_byte = file[index + 2]
            source = second_byte | (third_byte << 8)  
            bytes_consumed = 3  
        else:
            destination = 'AL'
            second_byte = file[index + 1]
            source = second_byte
            bytes_consumed = 2
    elif pattern == 0b1011:
        byte = file[index]
        word = (byte >> 3) & 0b1
        reg = byte & 0b111
        if word:
            destination = reg16bit[reg]
            second_byte = file[index + 1]
            third_byte = file[index + 2]
            source = second_byte | (third_byte << 8)  
            bytes_consumed = 3  
        else:
            destination = reg8bit[reg]
            second_byte = file[index + 1]
            source = second_byte
            bytes_consumed = 2

    return destination, source, bytes_consumed

def parser(file_name: str):
    instructions = []

    with open(file_name, 'rb') as f:
        file = f.read()
    index = 0 
    while index < len(file):
        chunk = file[index]
        pattern, instruction = match_opcode(chunk)
        direction = (chunk >> 1) & 0b1 
        word = chunk & 0b1 
        #print(f"Binary: {chunk:08b}")

        if pattern in (0b100010, 0b000000, 0b001010, 0b001110):
            destination, source, bytes_consumed = process_mov_instruction(file, index, word, direction)
            index += bytes_consumed
        elif pattern in (0b1100011, 0b100000):
            #print("matched: Second row")
            instruction, destination, source, bytes_consumed = immediate_to_registermemory(file, index, word, pattern)
            index += bytes_consumed
        elif pattern in (0b0000010, 0b0010110, 0b0011110, 0b1011):
            destination, source, bytes_consumed = immediate_accumulator(file, index, word, pattern)
            index += bytes_consumed
        elif pattern in jumps:
            instruction = jumps[pattern] 
            displacement_byte = file[index+1]
            # Convert to signed 8-bit value
            if displacement_byte & 0x80:  # If negative (sign bit set)
                destination = displacement_byte - 256
            else:
                destination = displacement_byte
            source = ""
            index += 2
        else:
            print("Unknown instruction2")
            index += 1

        if str(source):
            instructions.append({
                'operation': instruction,
                'destination': str(destination),
                'source': source
            })
        else:
            instructions.append({
                'operation': instruction, 
                'destination': str(destination),
                'source': None
            })
    return instructions

listing37 = 'listing_0037_single_register_mov'
listing38 = 'listing_0038_many_register_mov'
listing39 = 'listing_0039_more_movs'
listing41 = 'listing_0041_add_sub_cmp_jnz'

listing43 = 'listing_0043_immediate_movs'



def get_instructions(file_name: str):
    instructions = parser(file_name)
    return instructions

if __name__=="__main__":
    
    listing = listing43

    instructions =  get_instructions(listing)
    print("Printing" + listing)
    for instr in instructions:
        print(instr)

