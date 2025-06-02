import math
from sage.all import *

def reverse_concat_infos(value: int) -> tuple:
    # Extract info_2 (last 512 bits)
    info_2 = value & ((1 << 511) - 1)
    value >>= 511

    # Extract info_1 (next 512 bits)
    info_1 = value & ((1 << 511) - 1)
    value >>= 511

    # Extract z (second bit)
    z = value & 1
    value >>= 1

    return z, info_1, info_2

def decode_password(encoded):
    print(encoded)
    decoded = b''
    padded_length = ((len(encoded) * 8 + 511) // 512) * 512
    print(f"Padded bit length: {padded_length}")
    assert padded_length == 3072
    r = []
    for j in range(3):
        # Extract 512 bits for each block
        value = int.from_bytes(encoded[j * 1024 // 8:(j + 1) * 1024 // 8], byteorder='big') & ((1 << 1024) - 1)
        value = reverse_concat_infos(value)
        r.append(value)
    A = []
    B = []
    for i in range(3):
        signe = -1 if r[i][0] == 1 else 1
        A.append([r[i][2]**2, r[i][2], 1])
        B.append(signe * r[i][1])
    print(f"A : {A}")
    print(f"B : {B}")

    # Résoudre pour [a, b, c] avec SageMath
    a, b, c = var('a b c')
    equations = [
        A[0][0] * a + A[0][1] * b + A[0][2] * c == B[0],
        A[1][0] * a + A[1][1] * b + A[1][2] * c == B[1],
        A[2][0] * a + A[2][1] * b + A[2][2] * c == B[2],
    ]
    solution = solve(equations, [a, b, c])
    print(f"Solution : {solution}")
    sol = solution[0]
    a = sol[0].rhs()
    b = sol[1].rhs()
    c = sol[2].rhs()
    
    
    print(f"Polynôme trouvé : P(x) = {a}x² + {b}x + {c}")
    
    # Résoudre ax² + bx + c = 0 avec SageMath
    x = var('x')
    polynomial = a * x**2 + b * x + c
    roots = solve(polynomial == 0, x)
    roots = [root.rhs() if hasattr(root, 'rhs') else root for root in roots]
    
    if len(roots) != 2:
        raise ValueError("Les racines ne sont pas valides.")
    
    root1, root2 = roots
    print(f"Deux racines réelles : {root1} et {root2}")
    
    # Retrouver les valeurs originales de b et c
    b = max(int(root1), int(root2))
    c = min(int(root1), int(root2))
    
    # Convert b and c back to the password
    password_b = b.to_bytes((b.bit_length() + 7) // 8, 'big').decode()
    password_c = c.to_bytes((c.bit_length() + 7) // 8, 'big').decode()

    # Combine b and c to reconstruct the password
    password = ''.join([password_b[i // 2] if i % 2 == 0 else password_c[i // 2] for i in range(len(password_b) + len(password_c))])

    decoded = password.encode()
    return decoded

if __name__ == "__main__":
    encrypted = b'@O\n#c\xe9\xda\x8e[6:#i\xc8\xe7\xbf\xe9\xc8J\xd8\x02+\x8a\xa6\xc5Ln\xdb\xcf\n\xc9\xc6\x8d\xbf\xb3\xe5G>R\xa7\x9d\x11L\xeb\x8f\xab^Z\xbeh\xee\x90\x9e\xa2\x0e\xd5"\xd2\x93:\x80\x1f\xfa\xb0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03m\xf5\'\x95u!\xfav7\xcbg\xc3\x96\xad\xf9BY\xa9e\xde{\xfe\r\x82#\xa7\xc0\xb3@\xeayA\x1f\x04\xc2\x11R\x0c_C\x90a\xcd&\xe3\xcdqCi&sL\x1c\xb2t\xc5#\xca{\x87\xef\xe4\xb3G\xe0\xc5\x0c\x9e{\x97C\xbfA\ra\x99\xefW$\xdc:\x03(\xfb)+\x19\x9c\xd2.{\xe0\xbfl\xe9\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$P\x87\xbe\x0c\x8d:\xc9,\xbf\xad\xd7Q\x9e\x81\xa2\x84@k8\x8f\x11\xf5R\x87\xf1\xb1\xd7o\xe2F6A\x11\xa8o\xc2>\xe8\x1c\xd7\x8e\x0cQ\xf9\x94\xb8\xceT\xcdkV\xe07#T\x19\xc9\xb1\xbd\x1d\x17Q\xef\xa5\x88\x8d1\xee\xb0\x9a[\xa4\xd2g\x9fK[\x86\x9c5\x93\xe5\x94\x8aoa!r\x1ad\xa0\xa8\\\x9e\xc5\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00%\x8e\xfe6\n\x86\x90\x1ah8\xb2\'\xe6\x88\x81\xc6\xa6}p\xc2\xb9nW\xd7e\xc64\xc8`\x11\x11\xba'
    decoded = decode_password(encrypted)
    print(f"Decoded password: {decoded.decode()}")