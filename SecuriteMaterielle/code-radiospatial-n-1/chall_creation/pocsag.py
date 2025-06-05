from util import *


class CodeWord(object):
	def __init__(self, header_bit: int, data_fields: list[list[int]]):
		"""
		:param header_bit: the header bit 0 for Address CW, 0 for Message CW
		:type header_bit: int
		:param data_fields: the fields that contains data
		:type data_fields: list[list[int]]
		"""
		if not header_bit in [0, 1]:
			raise ValueError("Header bit must be 0 or 1")
		if type(data_fields) != list:
			raise ValueError("The data_fields parameter must be a list")
		if len(data_fields) not in [1, 2]:
			raise ValueError("Fields number in data_fields must be 1 or 2")
		for field in data_fields:
			if type(field) != list:
				raise ValueError("The fields inside the data_fields must be list of int")

			for i in field:
				if i not in [0, 1]:
					ValueError("The fields inside the data_fields must be list of int")

		super().__init__()

		super().__setattr__("hbit", header_bit)
		super().__setattr__("f1", data_fields[0])
		if len(data_fields) == 2:
			super().__setattr__("f2", data_fields[1])
		else:
			super().__setattr__("f2", [])
		self.p = 0
		self.bch = [0 for _ in range(10)]
		# Force update
		self.hbit = header_bit
		

	def get_bits(self, with_check: bool = True):
		"""
		Return the data of the code word as a list of bits, MSB first
		:param with_check: does the output bits contain CRC and parity bit
		:type with_check: bool
		:rtype: list[int]
		"""
		out = [self.hbit] + self.f1 + self.f2

		if with_check:
			out += self.bch + [self.p]

		return out

	def is_empty(self):
		return False

	def __setattr__(self, attr, value):
		if attr != "bch" and attr != "p":
			super().__setattr__(attr, value)
			self.bch = to_bits(
				pocsag_crc(
					from_bits(
						self.get_bits(with_check=False)
					)
				),
				size=10
			)
		elif attr == "bch":
			super().__setattr__(attr, value)
			self.p = sum(self.get_bits()[:-1]) % 2
		else:
			super().__setattr__(attr, value)


class AddrCW(CodeWord):
	def __init__(self, address: list[int], function_bits: list[int]):
		assert len(function_bits) == 2, "Invalid size of function bits, must be 2"
		assert len(address) == 18, "Invalid size of address, must be 18"

		super().__init__(
			header_bit=0,
			data_fields=[address, function_bits]
		)


class MessCW(CodeWord):
	def __init__(self, message: list[int]):
		assert len(message) == 20, "Invalid message size, must be 20"

		super().__init__(
			header_bit=1,
			data_fields=[message]
		)


class FillCW(CodeWord):
	def __init__(self):
		super().__init__(
			header_bit=1,
			data_fields=[[0 for _ in range(20)]])

	def get_bits(self, with_check=False):
		return to_bits(0x7A89C197, 32)

	def is_empty(self):
		return True

class POCSAGFrame(object):
	def __init__(self, word1: CodeWord, word2: CodeWord):
		"""
		Init POCSAG Frame
		:param word1: the first 32 bits word of the frame
		:type word1: CodeWord
		:param word2: the second 32 bits word of the frame
		:type word2: CodeWord
		"""
		super().__init__()

		self.w1 = word1
		self.w2 = word2

	def get_bits(self):
		return self.w1.get_bits() + self.w2.get_bits()


class POCSAGBatch(object):
	
	FSC = 0x7CD215D8

	def __init__(self, frames: list[POCSAGFrame]):
		"""
		Init POCSAG Batch
		:param frames: the eight frames in the POCSAG Batch
		:type frames: list[POCSAGFrame]
		"""

		if len(frames) != 8:
			raise ValueError("Invalid number of frames, must be exactly 8")
		super().__init__()

		self.frames = frames

	def get_bits(self):
		out = to_bits(self.FSC, 32)

		for frame in self.frames:
			out += frame.get_bits()

		return out


class POCSAGPacket(object):
	
	SYNC = [ (i + 1) % 2 for i in range(576) ]

	def __init__(self, batches: list[POCSAGBatch]):
		"""
		Init a POCSAG Packet
		:param batches: the POCSAG batches of the packet
		:type data: list[POCSAGBatch]
		"""
		super().__init__()

		assert len(batches) > 0

		self.batches = batches

	def get_bits(self):
		out = self.SYNC

		for batch in self.batches:
			out += batch.get_bits()

		return out

def create_empty_packet(n_batches):
	"""
	Create a POCSAG packet with a given number of batches, init with empty code word
	:param n_batches: the number of batches in the packet
	:type n_batches: int
	"""
	assert n_batches <= 8

	batches = []

	for _ in range(n_batches):
		batches.append(
			POCSAGBatch(
				[POCSAGFrame(FillCW(), FillCW()) for k in range(8)]
			)
		)

	return POCSAGPacket(batches)


def send_to(data, address):
	"""
	Create POCSAG packets to send to the address
	:param data: the data to transmit
	:type data: str
	:param address: the address to send the data
	:type address: int
	"""
	assert address.bit_length() <= 21

	size = len(data) * 7 // 20 + 1
	address_18 = address >> 3
	pos = address & 0b111
	
	data_bits = []
	for c in data:
		data_bits += to_bits(ord(c), 7)[::-1]

	data_bits += [0] * (20 - (len(data) * 7 % 20))
	print(data_bits)
	bn = (size + pos * 2 + 1) // 16 + 1
	print(f"Need {bn} batches")
	packet = create_empty_packet(bn)

	packet.batches[0].frames[pos].w1 = AddrCW(
		to_bits(address_18, 18),
		[1, 1]
	)
	
	index = (pos + 1) * 20
	for i in range(0, len(data_bits), 20):
		message_word = MessCW(data_bits[i:i+20])
		if index % 40:
			print(f"Add data to batch {index // (8 * 2 * 20)}, frame {index // (2 * 20)} and word w2")
			packet.batches[index // (8 * 2 * 20)].frames[index // (2 * 20) % 8].w2 = message_word
		else:
			print(f"Add data to batch {index // (8 * 2 * 20)}, frame {index // (2 * 20)} and word w1")
			packet.batches[index // (8 * 2 * 20)].frames[index // (2 * 20) % 8].w1 = message_word

		index += 20

	return packet


def insert(packet, address, codewords):
	"""
	Try to insert code words inside a POCSAG packet
	"""
	address_18 = address >> 3
	pos = address & 0b111
	start = 0

	enough_length = False
	address_cw = 0
	for bn, batch in enumerate(packet.batches):
		address_cw = pos * 2 + bn * 16
		start = pos * 2
		if batch.frames[pos].w1.is_empty():
			start += 1
		elif batch.frames[pos].w2.is_empty():
			address_cw += 1
			start += 2
		else:
			continue

		print(f"Found free place at batch {bn} frame {pos}")
		enough_length = True
		for i in range(start, len(codewords) + start):
			print(f"Test batch {(bn*16 + i)//16}, frame {(bn*16+i)//2 % 8}, cw {1 + i%2}")
			if len(packet.batches) <= (bn + i//16)\
				or (i % 2 and not packet.batches[(bn * 16+ i)//16].frames[(bn * 16 + i//2) % 8].w2.is_empty())\
				or (not (i % 2) and not packet.batches[(bn*16 + i)//16].frames[(bn*16 + i//2) % 8].w1.is_empty()):
				enough_length = False
				break
			else:
				if i % 2:
					assert packet.batches[bn + i//16].frames[((bn * 16) + i)//2 % 8].w2.is_empty()
				else:
					assert packet.batches[bn + i//16].frames[(bn*16 + i)//2 % 8].w1.is_empty()
		if enough_length:
			start += bn * 16
			break

	if not enough_length:
		return False

	if address_cw % 2:
		assert packet.batches[address_cw//16].frames[address_cw//2 % 8].w2.is_empty()
		packet.batches[address_cw//16].frames[address_cw//2 % 8].w2 = AddrCW(to_bits(address_18, 18), [0, 0])
	else:
		assert packet.batches[address_cw//16].frames[address_cw//2 % 8].w1.is_empty()
		packet.batches[address_cw//16].frames[address_cw//2 % 8].w1 = AddrCW(to_bits(address_18, 18), [0, 0])
	for i in range(start, len(codewords) + start):
		print(f"Insert {''.join(list(map(str, codewords[i-start].get_bits()[1:21])))} at batch {i//16}, frame {i//2 % 8}, cw {1 + i%2}")
		if i % 2:
			assert packet.batches[i//16].frames[i//2 % 8].w2.is_empty()
			packet.batches[i//16].frames[i//2 % 8].w2 = codewords[i-start]
		else:
			assert packet.batches[i//16].frames[i//2 % 8].w1.is_empty()
			packet.batches[i//16].frames[i//2 % 8].w1 = codewords[i-start]

	return True


def ascii2cw(data):
	size = len(data) * 7 // 20 + 1
	data_bits = []
	for c in data:
		data_bits += to_bits(ord(c), 7)

	if len(data) * 7 % 20 != 0:
		data_bits += [0] * (20 - (len(data) * 7 % 20))

	cw = []
	for i in range(0, len(data_bits), 20):
		cw.append(MessCW(data_bits[i:i+20]))

	return cw