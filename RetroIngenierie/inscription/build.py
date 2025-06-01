#!/usr/bin/env python3

# flag : 404CTF{Fr13nd5H1p-3ndeD-w1TH-L4t3x-N0w-tYP5T-iS-my-B3sT-Fr1End}

import os
import zipfile

os.chdir("plugin")
os.system("cargo build --release --target wasm32-unknown-unknown")
os.system("cp target/wasm32-unknown-unknown/release/plugin.wasm ..")
os.chdir("..")

with open("plugin.wasm", "rb") as f:
    data = f.read()

key = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim aeque doleamus animo, cum corpore dolemus, fieri tamen permagna accessio potest, si aliquod aeternum et infinitum impendere malum nobis opinemur. Quod idem licet transferre in voluptatem, ut."

ndata = bytes([data[i] ^ ord(key[i & len(key) - 1]) for i, b in enumerate(data)])

with open("data.typ", "w") as f:
    f.write("#let data = (")
    f.write(", ".join(map(hex, ndata)))
    f.write(")")

print("Succesfully wrote plugin to data.typ")

with zipfile.ZipFile("chall.zip", "w") as zf:
    zf.mkdir("chall")
    for file in ["chall.typ", "data.typ", "template.typ"]:
        zf.write(file, f"chall/{file}")

print("Succesfully created archive")
