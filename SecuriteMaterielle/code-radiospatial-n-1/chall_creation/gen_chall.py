from pocsag import *
from transmission import modulate
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import numpy as np 
from scipy.signal import hilbert

# Format : IQ float32 real, float32 ima, FE = 4.9152MHz, 1200 bauds, 

FLAG = "404CTF{fb31e1acc2e6eae8be01182d3029ffcb958e3368ca991ceb53895b8c97f2f275}"

packet=send_to("Voici le flag : " + FLAG, 0b111001001101000010000)

bits = packet.get_bits()
FE, signal = modulate(bits, 136e3, symb_duration=1/1200)
print(f"Working at FE={FE/1e6}Mhz")

signal.astype(np.float32).tofile("signal.raw")

signal_iq = hilbert(signal)

signal_iq.astype(np.complex64).tofile("chall.iq")