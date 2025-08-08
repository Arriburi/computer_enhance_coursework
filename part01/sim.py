from decoder import get_instructions

if __name__ == "__main__":
    file_name = 'listing_0046_add_sub_cmp'
    instructions = get_instructions(file_name) # type: ignore
    print("\n---We are simulating: " + file_name+"---\n")

registers = {
    'AX': 0x0000,
    'BX': 0x0000, 
    'CX': 0x0000,
    'DX': 0x0000,
    'SP': 0x0000,
    'BP': 0x0000,
    'SI': 0x0000,
    'DI': 0x0000
}

flags = 0b0000 
ZF = 1 << 0  # Zero Flag: first bit 
SF = 1 << 1  # Sign Flag: second bit 


def flag_check(result): 
    global flags
    messages = []

    if result == 0:
        flags |= ZF
    else:
        flags &= ~ZF
    messages.append(f"ZF = {1 if flags & ZF else 0}")

    if (result & 0x8000) != 0:
        flags |= SF
    else:
        flags &= ~SF
    messages.append(f"SF = {1 if flags & SF else 0}")

    return messages

def subtract(op1, op2):
    result = op1 - op2
    messages = flag_check(result)
    return result, messages

def addition(op1, op2):
    result = op1 + op2
    messages = flag_check(result)
    return result, messages

def compare(op1, op2):
    result = op1 - op2
    messages = flag_check(result)
    return messages

def set_reg(reg, value): ##lets say mov cx, 3
    old_value = registers[reg]
    registers[reg] = value
    return old_value 

def get_reg(reg):
    if reg in registers:
        return registers[reg]
    else:
        return reg 

for instr in instructions:
    operation = instr['operation']
    destination = instr['destination']
    source = instr['source']


    if operation == 'MOV':
        new_value = get_reg(source)
        old_value = set_reg(destination, new_value) 
        print(f"{operation} {destination}, {source} ; {destination}:0x{old_value:04x}->0x{new_value:04x}")
    elif operation == 'SUB':
        op1 = get_reg(destination)
        op2 = get_reg(source)
        difference, messages = subtract(op1, op2)
        set_reg(destination, difference)
        print(f"{operation} {destination}, {source} ; {destination}:0x{op1:04x}->0x{difference:04x} {messages}")
    elif operation == 'ADD':
        op1 = get_reg(destination)
        op2 = get_reg(source)
        sum, messages = addition(op1, op2)
        set_reg(destination, sum)
        print(f"{operation} {destination}, {source} ; {destination}:0x{op1:04x}->0x{sum:04x}  {messages}")
    elif operation == 'CMP':
        op1 = get_reg(destination)
        op2 = get_reg(source)
        messages = compare(op1, op2)
        print(f"{operation} {destination}, {source} ; {messages}")


print("\nFinal registers: ")
for reg in registers:
    value = registers[reg]
    print(f"      {reg}: 0x{value:04x} ({value})")
print("Flags:")
print("  ZF:", bool(flags & ZF))
print("  SF:", bool(flags & SF))





