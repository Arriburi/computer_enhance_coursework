from decoder import get_instructions

if __name__ == "__main__":
    file_name = 'listing_0043_immediate_movs'
    instructions = get_instructions(file_name) # type: ignore
    print("We are simulating")
    print(instructions)


registers = {
    'AX': 0x0000,
    'BX': 0x0000, 
    'CX': 0x0000,
    'DX': 0x0000,
    'SP': 0x0000,
    'DP': 0x0000,
    'SI': 0x0000,
    'DI': 0x0000
}



