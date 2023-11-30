# Parse binary files to asm

register_map = [["al", "cl", "dl", "bl", "ah", "ch", "dh", "bh"],
                ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di"]]

opcode_map = {
    0b00100010: "mov"
}


# All the handlers
def mov(d, w, reg, reg_m):
    r = register_map[w][reg]
    m = register_map[w][reg_m]

    return (r, m) if d == 1 else (m, r)


with open('data/listing_0038_many_register_mov', 'r+b') as file:
    while (byte := file.read(2)):
        first_byte_in_int = byte[0]
        opcode_key = first_byte_in_int >> 2

        opcode = opcode_map[opcode_key]

        if opcode == "mov":
            d_bit = (first_byte_in_int >> 1) & 1
            w_bit = (first_byte_in_int) & 1

            second_byte_in_int = byte[1]
            mod = second_byte_in_int >> 6
            reg = (second_byte_in_int & 0b00111000) >> 3
            reg_or_mem = second_byte_in_int & 0b00000111

            source, destination = mov(d_bit, w_bit, reg, reg_or_mem)

            print(f"mov {source}, {destination}")
