import wave
import numpy as np

def text_to_bits(text):
    bits = bin(int.from_bytes(text.encode('utf-8'), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def bits_to_text(bits):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('utf-8', errors='ignore')

def get_range_info(diff):
    ranges = [(7, 2), (15, 3), (31, 4), (63, 5), (127, 6), (255, 7), (511, 8), (1023, 9)]
    for upper, bits_to_embed in ranges:
        if diff <= upper:
            lower = 0
            if ranges.index((upper, bits_to_embed)) > 0:
                lower = ranges[ranges.index((upper, bits_to_embed)) - 1][0] + 1
            return lower, upper, bits_to_embed
    return 0, 2047, 11

def embed_message_in_audio(audio_path, message, output_path):
    with wave.open(audio_path, 'rb') as wav:
        params = wav.getparams()
        frames = wav.readframes(params.nframes)
        samples = np.frombuffer(frames, dtype=np.int16).copy()

    bits = text_to_bits(message) + "1111111111111110"
    idx = 0

    for i in range(0, len(samples) - 1, 2):
        if idx >= len(bits):
            break
        s1, s2 = int(samples[i]), int(samples[i + 1])
        d = abs(s2 - s1)
        low, high, n_bits = get_range_info(d)

        available = len(bits) - idx
        n = min(n_bits, available)

        b = int(bits[idx:idx + n], 2)
        new_d = low + b

        if s1 >= s2:
            s2_new = s1 - new_d
        else:
            s2_new = s1 + new_d

        samples[i + 1] = np.clip(s2_new, -32768, 32767)
        idx += n

    new_frames = samples.astype(np.int16).tobytes()
    with wave.open(output_path, 'wb') as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(new_frames)

def extract_message_from_audio(audio_path):
    with wave.open(audio_path, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        samples = np.frombuffer(frames, dtype=np.int16)

    bits = ""
    delimiter = "1111111111111110"

    for i in range(0, len(samples) - 1, 2):
        s1, s2 = int(samples[i]), int(samples[i + 1])
        d = abs(s2 - s1)
        low, _, n_bits = get_range_info(d)
        b = d - low
        bits += bin(b)[2:].zfill(n_bits)

        if delimiter in bits:
            return bits_to_text(bits.split(delimiter)[0])

    return "Pesan tidak ditemukan."
