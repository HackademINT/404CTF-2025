from pwn import *
from AES_Full_Linear import AES_Full_Linear_Attack

r = remote("host", 0000)  # Replace with actual host and port

def linear_attack(ciphertext:str,b_aes:str)->str:

    BC = BC_Starhunter(os.urandom(16))
    def encrypt_local(message):
        return BC.sendMissile(bytes.fromhex(message)).hex()

    linear_attack = AES_Full_Linear_Attack(encrypt_local=encrypt_local, remote_b_aes=b_aes, encr_flag=ciphertext)
    return linear_attack.attack()

def solve(r:remote):
    # Part 0: Set the security to 277182 to have the identity for the sbox
    r.recvuntil(b'pour commencer le combat: ')
    r.sendline(b'277182')

    # Part 1: Recover an encrypted message to perform the linear attack
    r.recvuntil('arme secrète.'.encode())
    r.sendline(b'1')
    r.sendline(b"0"*32)
    r.recvuntil("ce qu'il a répondu : ".encode())
    b_aes = r.recvline().rstrip().decode()
    print(f"b_aes: {b_aes}")

    # Part 2: Recover the ciphertext
    r.recvuntil('arme secrète.'.encode())
    r.sendline(b'2')
    r.recvuntil(b'>>> ')
    ciphertext = r.recvuntil(b'\n').rstrip().decode()
    print(f"Ciphertext: {bytes.fromhex(ciphertext)}")

    plaintext = linear_attack(ciphertext, bytes.fromhex(b_aes))
    r.recvuntil(b'chef ?')
    r.sendline(plaintext.hex().encode())
    try:
        r.recvuntil(b'prime : ')
        print(r.recvline())
    except Exception as e:
        print(f"An error occured: {e}")


# Remotely the S_box is the identity, so we can use a security level of 1 locally with S_box being the identity 
security = 1

s_box = [0] * 256
for i in range(256):
    s_box[i] = i

inv_s_box = [0x00] * 256
for i in range(256):
    inv_s_box[s_box[i]] = i

#
# Everything that follows is the AES algorithm implementation from the chall.py file
#

def sub_bytes(s):
    # Let's do this more than once to be stronger
    for _ in range(security):
        for i in range(4):
            for j in range(4):
                s[i][j] = s_box[s[i][j]]


def inv_sub_bytes(s):
    # Let's do this more than once to be stronger
    for _ in range(security):
        for i in range(4):
            for j in range(4):
                s[i][j] = inv_s_box[s[i][j]]


def shift_rows(s):
    s[0][1], s[1][1], s[2][1], s[3][1] = s[1][1], s[2][1], s[3][1], s[0][1]
    s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
    s[0][3], s[1][3], s[2][3], s[3][3] = s[3][3], s[0][3], s[1][3], s[2][3]


def inv_shift_rows(s):
    s[0][1], s[1][1], s[2][1], s[3][1] = s[3][1], s[0][1], s[1][1], s[2][1]
    s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
    s[0][3], s[1][3], s[2][3], s[3][3] = s[1][3], s[2][3], s[3][3], s[0][3]


def add_round_key(s, k):
    for i in range(4):
        for j in range(4):
            s[i][j] ^= k[i][j]


xtime = lambda a: (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)


def mix_single_column(a):
    t = a[0] ^ a[1] ^ a[2] ^ a[3]
    u = a[0]
    a[0] ^= t ^ xtime(a[0] ^ a[1])
    a[1] ^= t ^ xtime(a[1] ^ a[2])
    a[2] ^= t ^ xtime(a[2] ^ a[3])
    a[3] ^= t ^ xtime(a[3] ^ u)


def mix_columns(s):
    for i in range(4):
        mix_single_column(s[i])


def inv_mix_columns(s):
    for i in range(4):
        u = xtime(xtime(s[i][0] ^ s[i][2]))
        v = xtime(xtime(s[i][1] ^ s[i][3]))
        s[i][0] ^= u
        s[i][1] ^= v
        s[i][2] ^= u
        s[i][3] ^= v

    mix_columns(s)


r_con = (
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
    0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
    0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
    0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
)


def bytes2matrix(text):
    return [list(text[i:i + 4]) for i in range(0, len(text), 4)]


def matrix2bytes(matrix):
    return bytes(sum(matrix, []))


def xor_bytes(a, b)-> list[bytes]:
    return bytes(i ^ j for i, j in zip(a, b))


def inc_bytes(a):
    out = list(a)
    for i in reversed(range(len(out))):
        if out[i] == 0xFF:
            out[i] = 0
        else:
            out[i] += 1
            break
    return bytes(out)


def pad(plaintext):
    padding_len = (16 - (len(plaintext) % 16)) % 16
    padding = bytes([padding_len] * padding_len)
    return plaintext + padding


def unpad(plaintext):
    padding_len = plaintext[-1]
    assert padding_len > 0
    message, padding = plaintext[:-padding_len], plaintext[-padding_len:]
    assert all(p == padding_len for p in padding)
    return message


def split_blocks(message, block_size=16, require_padding=True):
    assert len(message) % block_size == 0 or not require_padding
    return [message[i:i + 16] for i in range(0, len(message), block_size)]


class BC_Starhunter:
    rounds_by_key_size = {16: 10, 24: 12, 32: 14}

    def __init__(self, master_key):
        assert len(master_key) in self.rounds_by_key_size
        self.n_rounds = self.rounds_by_key_size[len(master_key)]
        self._key_matrices = self._expand_key(master_key)

    def _expand_key(self, master_key):
        key_columns = bytes2matrix(master_key)
        iteration_size = len(master_key) // 4

        i = 1
        while len(key_columns) < (self.n_rounds + 1) * 4:
            word = list(key_columns[-1])

            if len(key_columns) % iteration_size == 0:
                word.append(word.pop(0))
                word = [s_box[b] for b in word]
                word[0] ^= r_con[i]
                i += 1
            elif len(master_key) == 32 and len(key_columns) % iteration_size == 4:
                word = [s_box[b] for b in word]

            word = xor_bytes(word, key_columns[-iteration_size])
            key_columns.append(word)

        return [key_columns[4 * i: 4 * (i + 1)] for i in range(len(key_columns) // 4)]

    def encrypt_block(self, plaintext):
        assert len(plaintext) == 16

        plain_state = bytes2matrix(plaintext)

        add_round_key(plain_state, self._key_matrices[0])

        for i in range(1, self.n_rounds):
            sub_bytes(plain_state)
            shift_rows(plain_state)
            mix_columns(plain_state)
            add_round_key(plain_state, self._key_matrices[i])

        sub_bytes(plain_state)
        shift_rows(plain_state)
        add_round_key(plain_state, self._key_matrices[-1])

        return matrix2bytes(plain_state)

    def decrypt_block(self, ciphertext):
        assert len(ciphertext) == 16

        cipher_state = bytes2matrix(ciphertext)

        add_round_key(cipher_state, self._key_matrices[-1])
        inv_shift_rows(cipher_state)
        inv_sub_bytes(cipher_state)

        for i in range(self.n_rounds - 1, 0, -1):
            add_round_key(cipher_state, self._key_matrices[i])
            inv_mix_columns(cipher_state)
            inv_shift_rows(cipher_state)
            inv_sub_bytes(cipher_state)

        add_round_key(cipher_state, self._key_matrices[0])

        return matrix2bytes(cipher_state)

    def sendMissile(self, plaintext):
        plaintext = pad(plaintext)
        print(f"Envoie du missile de force {len(plaintext)}...")
        blocks = split_blocks(plaintext)
        ciphertext = b"".join(self.encrypt_block(block) for block in blocks)
        return ciphertext

    def decrypt(self, ciphertext):
        blocks = split_blocks(ciphertext, require_padding=False)
        plaintext = b"".join(self.decrypt_block(block) for block in blocks)
        return unpad(plaintext)


solve(r)