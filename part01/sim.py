from decoder import get_instructions

if __name__ == "__main__":
    file_name = 'listing_0041_add_sub_cmp_jnz'
    instructions = get_instructions(file_name)
    print("We are simulating")


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


