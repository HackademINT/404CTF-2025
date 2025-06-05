import numpy as np

def modulate(data, carrier, fshift=4.5e3, symb_duration=1/1200, FE_factor=50, scale = 1):
	print(f"min freq: {carrier-fshift}, max freq: {carrier+fshift}")
	print(f"Send {len(data)} bits")
	FE = 4096/symb_duration
	assert FE >= 2 * (carrier + fshift)

	T = np.arange(0, symb_duration, 1/FE, dtype=np.float32)

	print(f"{len(T)} samples per symbol")
	print(f"Ouput size will be {len(T) * len(data)}")
	signal = np.array([ 0 for _ in range(len(T) * len(data))], dtype = np.float32)

	for i, b in enumerate(data):
		print(round(i/len(data)*100, 2), end="\r")
		signal[i*len(T): (i+1) * len(T)] = scale * np.sin(2 * np.pi * (carrier + (0.5-b) * 2 * fshift) * T)
	return FE, signal
