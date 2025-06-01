import tkinter as tk
import importlib.util
import os
import sys

def import_module():
    module_path = os.path.join(sys._MEIPASS, 'modules/encrypt_key.cpython-39.pyc')
    spec = importlib.util.spec_from_file_location("nom_module", module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

module = import_module()

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def validate_password(password):
    if xor(module.encode_password(password.encode("ascii")), module.encrypt_key(0x6d39d56f8a40a6bbe43a82a53b2c762ea780c21a32c6b3ef765d3a54f3432432f3e6d39d56f8a40a6bbe43a82a53b2c762ea780c21a32c6b3ef765d3a54f3432432f3e)) == b'\xe9J\x1aB\xe2\xc5\xf3S\'\xd6>\n$\x94\x1a\x07\'F\xc6\xa1\x07\xb7\xcc\xec\xe1\x84\xec\xac\xe4\xd64\x8f\xc3\x12\x04\x16$n\x15\xec\xe1\xaee5\xc7\xecOX"\x98EO\x1f2\xb4\x15\xc4\xed\xf4\xcd$\xd3\xd3u\xc2\xf8\xc6\xae\x06\x08\xcd\xff\xe0(\xe9\xb0\xe7\xde6\x90\xcc\xfd\x02}%\x1a\x1a\xc9#\x10\xc2\x86\x06\x08\xcd\xfe&\xb8K\x0f)\x9a\xb6\xb9\x02\x17\xa0\xd8\xe4]\x98\xf5*\x154<\x06\x875\xbd\x05@\xe6\x88\xe3&6%\xcc\x18\x06\\%\xa4\x1a7!\xfe\xc3\xae\x06\x08\xcd\xff\xe2\x18\xe2x\xe0\x927x\r\xfa\xa6\xbd\xe67\x97\xf7\xe5)f\x94\xc8\xbdv\r\xef\x12\x1bZ\xe8e\xf3S\'\xd6>\n"8\x1be\x9c\xdf\xe8\x9b\x06\xb7\x0b3V\x1f\xedN\x87\xbbI!C>8z%\xc0\xeaM\xb5\xd1p\xd1\x0f|A\xd7B\x03\xc54\xd5T\xb9\xfd\x88;\xbf\x10\x81L\x90L\x0b\xff\xed\xe1\xe5dQ\xc4\x17\xd5\xafUl\xec':
        label.config(text="Mot de passe correct !")
    else:
        label.config(text="Mot de passe incorrect !")

root = tk.Tk()
root.title("Rêve en Python")
root.geometry("300x200")

label = tk.Label(root, text="Entrez le mot de passe :")
label.pack(pady=10)

entry_password = tk.Entry(root, width=20)
entry_password.pack(pady=5)

validate_button = tk.Button(root, text="Valider", command=lambda: validate_password(entry_password.get()))
validate_button.pack(pady=5)

root.mainloop()

