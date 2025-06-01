from pwn import *
from sage.all import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import long_to_bytes

# Data from the code
p = 0xf7fda1b2f0c9ea506e8a125766fd9e5046fd5716630c84f526fea8ce10497829
a, b = 0xbb0480e1f010abb2e69e7d72df5d75a23a15bc73710df25b6da04121f904e4f5, 0xfa2bddcca24c1d80baf26cb1e1f04cf78e995c675543c9692e959f83b470a03
G = (0x735d07d96821ec8bff37eb23c31081ea526ddc10abe22375518c44e043a39db0, 0x97e570cf7c177584ddd036d9181a3f5f83307f60c92b539a2d4f479d9c9ad4bd)
host = 'host'
port = 0000
# host and port should be set to the actual values for the challenge


def findPrivateKey(E:EllipticCurve, G, P):
    G = E(G)
    P = E(P)

    def lift(P, E, p):
        # lift point P from old curve to a new curve
        Px, Py = map(ZZ, P.xy())
        for point in E.lift_x(Px, all=True):
             # take the matching one of the 2 points corresponding to this x on the p-adic curve
            _, y = map(ZZ, point.xy())
            if y % p == Py:
                return point


    assert E.order() == p

    # Lift the points to some new curve over p-adic numbers
    E_adic = EllipticCurve(Qp(p), [a+p*13, b+p*37])
    G = p * lift(G, E_adic, p)
    P = p * lift(P, E_adic, p)

    # Calculate discrete log
    Gx, Gy = G.xy()
    Px, Py = P.xy()
    found_key = int(GF(p)((Px / Py) / (Gx / Gy)))
    print(f"La clef privée est {found_key}")
    return found_key

def decryptData(ciphertext: str, d: int,username: str) -> (str, str):
    cipher = AES.new(pad(long_to_bytes(d),32)[:32], AES.MODE_CBC, IV = pad(username.encode(), 16)[:16])
    return unpad(cipher.decrypt(bytes.fromhex(ciphertext)),16)

def solve(r):
    # Data from the challenge
    r.sendlineafter(b"Jedi ?\n",b"attacker','curve':'custom")
    sleep(3)
    r.sendline(b"2")
    r.recvuntil(b"ce point: ")
    P = eval(r.recvuntil(b")"))
    r.recvuntil(b"dire:")
    ciphertext = r.recvuntil(b"\n").decode()

    # Solve
    E = EllipticCurve(GF(p), [a, b])
    found_key = findPrivateKey(E, G, P)
    name = 'attacker'
    print(f'Flag trouvé: {decryptData(ciphertext, found_key, name)}')

if __name__ == "__main__":
    r = remote(host, port)
    solve(r)