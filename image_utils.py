from PIL import Image
import numpy as np

def text_to_bits(text):
    bits = bin(int.from_bytes(text.encode('utf-8'), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def bits_to_text(bits):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('utf-8', errors='ignore')

def get_range_info(diff):
    ranges = [(7, 2), (15, 3), (31, 4), (63, 5), (127, 6), (255, 7)]
    for upper, bits_to_embed in ranges:
        if diff <= upper:
            lower = 0
            if ranges.index((upper, bits_to_embed)) > 0:
                lower = ranges[ranges.index((upper, bits_to_embed)) - 1][0] + 1
            return lower, upper, bits_to_embed
    return 0, 255, 8

def embed_message_pvd(image_path, message, output_path):
    img = Image.open(image_path).convert("L")
    pixels = np.array(img)
    height, width = pixels.shape

    message_bits = text_to_bits(message) + "1111111111111110"
    idx = 0

    for r in range(height):
        for c in range(0, width - 1, 2):
            if idx >= len(message_bits):
                break
            p1 = int(pixels[r, c])
            p2 = int(pixels[r, c + 1])
            d = abs(p2 - p1)
            lower, _, n_bits = get_range_info(d)

            available = len(message_bits) - idx
            n = min(n_bits, available)

            b = int(message_bits[idx:idx + n], 2)
            new_d = lower + b

            if p1 >= p2:
                p2_new = p1 - new_d
            else:
                p2_new = p1 + new_d

            pixels[r, c + 1] = np.clip(p2_new, 0, 255)
            idx += n

        if idx >= len(message_bits):
            break

    stego_img = Image.fromarray(pixels.astype(np.uint8))
    stego_img.save(output_path)

def extract_message_pvd(stego_image_path):
    img = Image.open(stego_image_path).convert("L")
    pixels = np.array(img)
    height, width = pixels.shape

    bits = ""
    delimiter = "1111111111111110"

    for r in range(height):
        for c in range(0, width - 1, 2):
            p1 = int(pixels[r, c])
            p2 = int(pixels[r, c + 1])
            d = abs(p2 - p1)
            low, _, n_bits = get_range_info(d)
            b = d - low
            bits += bin(b)[2:].zfill(n_bits)

            if delimiter in bits:
                return bits_to_text(bits.split(delimiter)[0])

    return "Pesan tidak ditemukan."
