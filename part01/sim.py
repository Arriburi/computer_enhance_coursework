from decoder import get_instructions

if __name__ == "__main__":
    file_name = 'listing_0044_register_movs'
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

    new_value = get_reg(source)
    old_value = set_reg(destination, new_value)

    print(f"{operation} {destination}, {source} ; {destination}:0x{old_value:04x}->0x{new_value:04x}")


print("\nFinal registers: ")
for reg in registers:
    value = registers[reg]
    print(f"      {reg}: 0x{value:04x} ({value})")









