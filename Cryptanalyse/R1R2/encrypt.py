import random as rd
from flag import FLAG

def ci(z: int, info_1: int, info_2: int) -> int:
    assert info_1.bit_length() <= 511 and info_2.bit_length() <= 511
    return ((z & 1) << 1022) | ((info_1 & ((1 << 511) - 1)) << 511) | (info_2 & ((1 << 511) - 1))


def encrypt_password(password):
    a = b''
    b, c = password[::2], password[1::2]
    b = int.from_bytes(b.encode(), 'big')
    c = int.from_bytes(c.encode(), 'big')
    assert b > c
    d = b+c
    e = b*c
    r = []
    for i in range(3):
        x = rd.randint(0, 2**b.bit_length())
        y = x**2 - d*x + e
        z = y<0
        t = ci(z,abs(y),x)
        r.append(t)
    for i in range(3):
        a += r[i].to_bytes((r[i].bit_length() + 7) // 8, 'big').rjust(128, b'\x00')
    return a

if __name__ == "__main__":
    a = encrypt_password(FLAG)
    print(a.hex())
    

# ENCRYPED FLAG : 40f1b6e577b2bb6aa703387a15d2738ad50c795972342bdbb4b32946bcf7b72fbbdfb41884883df6589bf0e1e73a01f4f0d13a60146ac87c146de846bb98407d80000000000000000000000000000000000000000000000000000000000000000c4df9ca82064c5b97e3e5013732439d6139195456b94e581b7a22f1510f926c4117ca4ed6a10c5d37b5d400dca883d001564774dbbce5c198c5ff83fe7af851fc3820a17947e71689812f6113dd3893250a14320a8f49c46bde754a188efd3000000000000000000000000000000000000000000000000000000000000000000f6336ee243e9a18cd74b182ff23f87f8bbac8912b57cd3ab25faffcaa18ea3940d748f2696de5597ec5df6d12826fc2b37d8e926af7a39afe74cb0950460da1a33112d89029e1a9334ea4c19d36cab027d4b360f240139de4ebd58ebfb05681800000000000000000000000000000000000000000000000000000000000000029e03851f31bd96e478b63347dc9a369a5d0569dc00ffe07cc3ad2d8293a9bf0
