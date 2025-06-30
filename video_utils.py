import cv2
import numpy as np

def text_to_bits(text):
    bits = bin(int.from_bytes(text.encode('utf-8'), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def bits_to_text(bits):
    try:
        n = int(bits, 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('utf-8', errors='ignore')
    except:
        return "[Gagal decode pesan]"

def get_range_info(diff):
    ranges = [(7, 2), (15, 3), (31, 4), (63, 5), (127, 6), (255, 7)]
    for upper, bits_to_embed in ranges:
        if diff <= upper:
            lower = 0
            if ranges.index((upper, bits_to_embed)) > 0:
                lower = ranges[ranges.index((upper, bits_to_embed)) - 1][0] + 1
            return lower, upper, bits_to_embed
    return 0, 255, 8

def embed_message_in_video(video_path, message, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "Gagal membuka video."

    width = int(cap.get(3))
    height = int(cap.get(4))
    fps = cap.get(5)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=False)

    message_bits = text_to_bits(message) + "1111111111111110"
    idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for r in range(gray.shape[0]):
            for c in range(0, gray.shape[1] - 1, 2):
                if idx >= len(message_bits):
                    break

                p1 = int(gray[r, c])
                p2 = int(gray[r, c+1])
                d = abs(p2 - p1)
                low, _, n_bits = get_range_info(d)

                available = len(message_bits) - idx
                n = min(n_bits, available)

                b = int(message_bits[idx:idx + n], 2)
                new_d = low + b

                if p1 >= p2:
                    p2_new = p1 - new_d
                else:
                    p2_new = p1 + new_d

                gray[r, c+1] = np.clip(p2_new, 0, 255)
                idx += n

            if idx >= len(message_bits):
                break

        out.write(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))

        if idx >= len(message_bits):
            break

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        out.write(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))

    cap.release()
    out.release()

def extract_message_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "Gagal membuka video."

    bits = ""
    delimiter = "1111111111111110"

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for r in range(gray.shape[0]):
            for c in range(0, gray.shape[1] - 1, 2):
                p1 = int(gray[r, c])
                p2 = int(gray[r, c + 1])
                d = abs(p2 - p1)
                low, _, n_bits = get_range_info(d)
                b = d - low
                bits += bin(b)[2:].zfill(n_bits)

                if delimiter in bits:
                    cap.release()
                    return bits_to_text(bits.split(delimiter)[0])

    cap.release()
    return "Pesan tidak ditemukan."
