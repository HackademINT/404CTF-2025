def pocsag_crc(data: int):
	generator = 0b11101101001
	denom = generator << 20
	crc = data << 10

	for i in range(0, 21):
		b = (crc >> (30 - i)) & 1

		if b:
			crc ^= denom

		denom >>= 1

	return crc & 0x3FF

def to_bits(data: int, size: int):
	"""
	Returns the bits of the int assuming a 'size' bits number
	:param data: The integer to convert
	:type data: int
	:param size: The size of the integer in bits
	:type size: int
	:return: A list of bits, MSB first
	:rtype: list[int]
	"""
	output_bits = [0 for _ in range(size)]
	for i in range(size - 1, -1, -1):
		output_bits[size - i - 1] = (data & (1 << i)) >> i

	return output_bits

def from_bits(data: list[int]):
	"""
	Return the int represented by the bits, MSB first
	:param data: the bits to convert
	:type data: list[int]
	"""
	n = len(data) - 1
	return sum([ b * 2 ** (n - i) for i, b in enumerate(data)])
