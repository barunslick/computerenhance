# Parse binary files to asm

file_name = "data/listing_0039_more_movs"
#  Decides what to do with stream of data.. can be changed this to write to file
#  Right now, it just prints to stdout
code_handler = print

register_map = [
    #  8 bit registers, used when W(wide) bit is 0
    ["al", "cl", "dl", "bl", "ah", "ch", "dh", "bh"],
    #  16 bit registers, used when W(wide) bit is 1
    ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di"]
]

effective_address_list = ["bx + si", "bx + di", "bp + si",
                          "bp + di", "si", "di", "bp", "bx"]


# All the handlers

#  Mov from register/memory to/from register
def mov_reg_mem_to_from_reg(first_byte, rest_byte_stream) -> str:
    # if first_byte_in_int & 0b11111100 == 0b10001000
    d_bit = (first_byte_in_int >> 1) & 1
    w_bit = (first_byte_in_int) & 1

    second_byte_in_int = int.from_bytes(rest_byte_stream.read(1))
    mod = second_byte_in_int >> 6
    reg = (second_byte_in_int & 0b00111000) >> 3
    reg_or_mem = second_byte_in_int & 0b00000111

    to_from_register = register_map[w_bit][reg]

    source = ""
    destination = ""

    if mod == 0b11:
        m = register_map[w_bit][reg_or_mem]

        destination, source = (to_from_register, m) if d_bit == 1 else (m, to_from_register)
    elif mod == 0b00:
        if reg_or_mem != 0b110:
            effective_address = effective_address_list[reg_or_mem]

            destination, source = (to_from_register, f"[{effective_address}]") \
                                            if d_bit == 1 else (f"[{effective_address}]", to_from_register)
        else:
            direct_displacement_byte = int.from_bytes(rest_byte_stream.read(2))
            destination, source = (to_from_register, f"[{direct_displacement_byte}]") \
                                            if d_bit == 1 else (f"[{direct_displacement_byte}]", to_from_register)

    elif mod == 0b01:
        effective_address = effective_address_list[reg_or_mem]
        displacement_byte = int.from_bytes(rest_byte_stream.read(1))

        destination, source = (to_from_register, f"[{effective_address} + {displacement_byte}]") \
                                         if d_bit == 1 else (f"[{effective_address} + {displacement_byte}]", to_from_register)

    elif mod == 0b10:
        effective_address = effective_address_list[reg_or_mem]
        displacement_byte = int.from_bytes(rest_byte_stream.read(2), byteorder="little")

        destination, source = (to_from_register, f"[{effective_address} + {displacement_byte}]") \
                                        if d_bit == 1 else (f"[{effective_address} + {displacement_byte}]", to_from_register)

    return f"mov {destination}, {source}"


def mov_imm_to_reg(first_byte, rest_byte_stream) -> str:
    w_bit = (first_byte_in_int >> 3) & 1
    reg_bits = (first_byte_in_int) & 0b00000111

    dest_reg = register_map[w_bit][reg_bits]

    source = ""
    if w_bit == 0:
        imm = rest_byte_stream.read(1)
        source = int.from_bytes(imm)
    else:
        source = int.from_bytes(rest_byte_stream.read(2), byteorder="little")
    return f"mov {dest_reg}, {source}"


print("bits 16")


with open(file_name, 'r+b') as file:
    while (byte := file.read(1)):
        first_byte_in_int = int.from_bytes(byte)
        if first_byte_in_int & 0b11111100 == 0b10001000:  # mov
            code_handler(mov_reg_mem_to_from_reg(first_byte_in_int, file))
        elif first_byte_in_int & 0b11110000 == 0b10110000: #mov
            code_handler(mov_imm_to_reg(first_byte_in_int, file))
