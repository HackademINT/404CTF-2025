import ast
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.number import long_to_bytes
from Crypto.Random import random as rd
import os

flag = os.getenv("flag") or "Flag{This_is_a_fake_flag_for_testing_purposes}"

class Curve:
    def __init__(self, a, b, p, g):
        self.a = a
        self.b = b
        self.p = p
        self.g = g

    def addPoints(self, P, Q):
        a, p = self.a, self.p
        if P == (0, 0):
            return Q

        if Q == (0, 0):
            return P

        x1, y1, x2, y2 = P[0], P[1], Q[0], Q[1]
        if x1 == x2 and y1 == (-y2) % p:
            return 0, 0

        if x1 == x2 and y1 == y2:
            m = (3 * x1 ** 2 + a) * pow(2 * y1, -1, p) % p
        else:
            m = (y2 - y1) * pow(x2 - x1, -1, p) % p

        x3 = (m ** 2 - x1 - x2) % p
        y3 = (m * (x1 - x3) - y1) % p

        return x3, y3

    def pointMultiplication(self, k, P):
        R = (0, 0)
        Q = P
        while k > 0:
            if k % 2 == 1:
                R = self.addPoints(R, Q)

            Q = self.addPoints(Q, Q)
            k = k // 2
            if k > 0: continue

        return R

Curves = {
    "secp112r1": Curve(0xdb7c2abf62e35e668076bead2088, 0x659ef8ba043916eede8911702b22, 0xdb7c2abf62e35e668076bead208b,
                       (0x09487239995a5ee76b55f9c2f098, 0xa89ce5af8724c0a23e0e0ff77500))
    ,"secp160k1": Curve(0x0000000000000000000000000000000000000000, 0x0000000000000000000000000000000000000007,
                         0xfffffffffffffffffffffffffffffffeffffac73,
                         (0x3b4c382ce37aa192a4019e763036f4f5dd4d7ebb, 0x938cf935318fdced6bc28286531733c3f03c4fee))
    ,"secp160r2": Curve(0xfffffffffffffffffffffffffffffffeffffac70, 0xb4e134d3fb59eb8bab57274904664d5af50388ba,
                         0xfffffffffffffffffffffffffffffffeffffac73,
                         (0x52dcb034293a117e1f4ff11b30f7199d3144ce6d, 0xfeaffef2e331f296e071fa0df9982cfea7d43f2e))
}


def translate(curveName: str) -> Curve:
    try:
        return Curves[curveName]
    except KeyError:
        # Since I have to return a curve, I'll create my own !
        return Curve(0xbb0480e1f010abb2e69e7d72df5d75a23a15bc73710df25b6da04121f904e4f5,
                     0xfa2bddcca24c1d80baf26cb1e1f04cf78e995c675543c9692e959f83b470a03,
                     0xf7fda1b2f0c9ea506e8a125766fd9e5046fd5716630c84f526fea8ce10497829,
                     (0x735d07d96821ec8bff37eb23c31081ea526ddc10abe22375518c44e043a39db0,
                      0x97e570cf7c177584ddd036d9181a3f5f83307f60c92b539a2d4f479d9c9ad4bd)
                     )

def createToken(name: str, destination: int) -> str:
    secureCurves = {1: "secp112r1", 2: "secp160k1", 3: "secp160r2"}
    try:
        return "{'curve':'" + secureCurves[destination] + "','name':'" + name + "'}"
    except KeyError:
        return "{}"

def generateKey(token: dict) -> ((int, int), int):
    curve = translate(token['curve'])
    d = rd.randint(2, curve.p - 1)
    return curve.pointMultiplication(d, curve.g), d

def encryptData(d: int, data: str, username: str) -> (bytes, bytes):
    cipher = AES.new(pad(long_to_bytes(d),32)[:32], AES.MODE_CBC, IV=pad(username.encode(), 16)[:16])
    return cipher.encrypt(pad(data.encode(), 16))


def chall():
    name = str(input("Hello there... Uhm, excuse moi mais quel est ton nom déjà Jedi ?\n"))
    print(f"En effet ! Ravi de te revoir {name}.\nMais pas le temps de discuter, tu dois aller à ton X-wing pour ta prochaine mission!")
    destination = int(input("""
    ||=============================================================================||
    ||Selectionner une destination:       oo__          _      _          __oo     ||
    ||                                        \"\"\"--,,,_(_)_--_(_)_,,,--\"\"\"         ||
    ||>1. Mustafar                                    _>_[____]_<_                 ||
    ||>2. Tatooine                            ___--\"\"\" (_)\\__/(_) \"\"\"--___         ||
    ||>3. Jedha                            oo\"\"                            \"\"oo    ||
    ||=============================================================================||
    """))
    token = createToken(name,destination)
    if token == "{}":
        print("Il semblerait que ce fut une embuscade... x.x")
        return

    try:
        token = ast.literal_eval(token)
        publicPoint, d = generateKey(token)
        print(f"Bien joué! Tu as atteri sur ce point: {publicPoint}")
    except Exception:
        print("Un de tes trains d'atterissage a craqué, et ton vaisseau a fait PAF... x.x")
        return

    ciphertext = encryptData(d, flag, token["name"])
    print(f"Après quelques pas, un papier étrangement brillant a attiré ton attention. Qu'est-ce que cela peut bien dire: {ciphertext.hex()}")

if __name__ == "__main__":
    chall()
    