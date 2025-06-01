import numpy as np
import math

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def encrypt_key(key):
    for _ in range(100):
        key <<= 1
        key ^= 0x4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_4404_4044_4044_4044_4044_0440_4404_4044_4044_4404_4044_4044
        key >>= 1
        key &= 0xF327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_3271_ADF3_3271_ADF3_F327_1ADF_3271_ADF3_F327_1ADF_1ADF_F327_1ADF_1ADF_ADF3_F327_1ADF_1ADF_F327_1ADF_1ADF_ADF3_F327
        key -= 0x4351_EAC5_DB5A_0D3F_3151_3511_EAC5_DB5A_0D3F_3521_EAC5_DB5A_0D3F_3151_EAC5_DB5A_0D3F_2143_EAC5_DB5A_EAC5_DB5A_0D3F_3151_EAC5_DB5A_0D3F_3151_4351_EAC5_DB5A_0D3F_3151_3511_EAC5_DB5A_0D3F_3521_EAC5_DB5A_0D3F_3151_EAC5_DB5A_0D3F_2143_EAC5_DB5A_EAC5_DB5A_0D3F_3151_EAC5_DB5A_0D3F_3151_4351_EAC5_DB5A_0D3F_3151_3511_EAC5_DB5A_0D3F_3521_EAC5_DB5A_0D3F_3151_EAC5_DB5A_0D3F_2143_EAC5_DB5A_EAC5_DB5A_0D3F_3151_EAC5_DB5A_0D3F_3151_4351_EAC5_DB5A_0D3F_3151_3511_EAC5_DB5A_0D3F_3521_EAC5_DB5A_0D3F_3151_EAC5_DB5A_0D3F_2143_EAC5_DB5A_EAC5_DB5A_0D3F_3151_EAC5_DB5A_0D3F_3151_3151_0D3F_3151_3151_DB5A_0D3F_3151_3151_0D3F_3151_3151_DB5A_0D3F
        key ^= 0x4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_0440_4404_4044_4044_4404_4044_4044_4044_4044_0440_4404_4044_4044_4404_4044_4044
        key <<=  1
        key += 4324354
        key >>= 1
    key = abs(key)
    encrypted_bytes = key.to_bytes((key.bit_length() + 7) // 8, byteorder='big')
    return encrypted_bytes


def decode_password(encoded):
    decoded = b''
    x_list = [110, -34, -230]
    for i in range(0, len(encoded), 6):
        r = []
        for j in range(3):
            high = encoded[i + 2 * j]
            low = encoded[i + 2 * j + 1]
            value = (high << 8) + low
            r.append(value)
        A = []
        B = []
        for i in range(3):
            A.append([x_list[i]**2, x_list[i], 1])
            B.append(r[i])
        A = np.array(A)
        B = np.array(B)
        
        # Résoudre pour [a, b, c]
        coeffs = np.linalg.solve(A, B)
        a, b, c = coeffs
        
        print(f"Polynôme trouvé : P(x) = {a}x² + {b}x + {c}")
        
        # Résoudre ax² + bx + c = 0
        delta = b**2 - 4*a*c
        
        if delta > 0:
            root1 = round((-b + math.sqrt(delta)) / (2*a))
            root2 = round((-b - math.sqrt(delta)) / (2*a))
            print(f"Deux racines réelles : {root1} et {root2}")
        # Retrouver les valeurs originales de b et c
        b = max(int(root1), int(root2))
        c = min(int(root1), int(root2))
        
        # Calculer le byte original
        original_byte = (b-11) * 11 + c
        decoded += bytes([original_byte])
    return decoded

if __name__ == "__main__":
    key_encoded = encrypt_key(0x6d39d56f8a40a6bbe43a82a53b2c762ea780c21a32c6b3ef765d3a54f3432432f3e6d39d56f8a40a6bbe43a82a53b2c762ea780c21a32c6b3ef765d3a54f3432432f3e)
    res_encoded = b'\xe9J\x1aB\xe2\xc5\xf3S\'\xd6>\n$\x94\x1a\x07\'F\xc6\xa1\x07\xb7\xcc\xec\xe1\x84\xec\xac\xe4\xd64\x8f\xc3\x12\x04\x16$n\x15\xec\xe1\xaee5\xc7\xecOX"\x98EO\x1f2\xb4\x15\xc4\xed\xf4\xcd$\xd3\xd3u\xc2\xf8\xc6\xae\x06\x08\xcd\xff\xe0(\xe9\xb0\xe7\xde6\x90\xcc\xfd\x02}%\x1a\x1a\xc9#\x10\xc2\x86\x06\x08\xcd\xfe&\xb8K\x0f)\x9a\xb6\xb9\x02\x17\xa0\xd8\xe4]\x98\xf5*\x154<\x06\x875\xbd\x05@\xe6\x88\xe3&6%\xcc\x18\x06\\%\xa4\x1a7!\xfe\xc3\xae\x06\x08\xcd\xff\xe2\x18\xe2x\xe0\x927x\r\xfa\xa6\xbd\xe67\x97\xf7\xe5)f\x94\xc8\xbdv\r\xef\x12\x1bZ\xe8e\xf3S\'\xd6>\n"8\x1be\x9c\xdf\xe8\x9b\x06\xb7\x0b3V\x1f\xedN\x87\xbbI!C>8z%\xc0\xeaM\xb5\xd1p\xd1\x0f|A\xd7B\x03\xc54\xd5T\xb9\xfd\x88;\xbf\x10\x81L\x90L\x0b\xff\xed\xe1\xe5dQ\xc4\x17\xd5\xafUl\xec'
    password_encoded = xor(res_encoded, key_encoded)
    password = decode_password(password_encoded)
    print(password)