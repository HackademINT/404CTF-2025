# Read the number from number.txt and display it in hexadecimal
import sys
from PIL import Image

# Increase the limit for integer string conversion
sys.set_int_max_str_digits(50000)

with open("number.txt", "r") as file:
    number = int(file.read().strip()) 
    hex_number = hex(number)[2:] 
    formatted_hex = " ".join(hex_number[i:i+4] for i in range(0, len(hex_number), 4))
    print(formatted_hex)

a = int(hex_number[:16], 16)

key = a ^ 0xFFFF_FFFF_FFFF_FFFF
print(hex(key))

new_number = 0
shift = 0
while number:
    bloc = (number & 0xFFFF_FFFF_FFFF_FFFF) ^ key
    new_number |= (bloc << shift) 
    number >>= 64
    shift += 64

def decrypt_image(binary_number, width, height, output_path):
    binary_representation = bin(binary_number)[2:].zfill(width * height)
    pixels = [255 if bit == '1' else 0 for bit in binary_representation]
    image = Image.new('L', (width, height))
    image.putdata(pixels)
    image.save(output_path)

decrypt_image(new_number, width=400, height=200, output_path='decrypted_flag.png')

