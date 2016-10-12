# -*- coding: utf-8 -*-
from string import digits as _numbers, letters as _letters, punctuation as _symbols, whitespace as _spaces
from itertools import chain, product
from random import sample
from random import randint
from Crypto.Cipher import AES


class PasserCrypto:
	def __init__(self, secret):
		BLOCK_SIZE = 32
		PADDING = 'l'
		secret = secret
		cipher = AES.new(secret)

		pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
		self.encodeAES = lambda s: base64.b64encode(cipher.encrypt(pad(s)))
		self.decodeAES = lambda e: cipher.decrypt(base64.b64decode(e)).rstrip(PADDING)

	def encodeAES(self, data):
		encoded = self.encodedAES(data)
		return encoded

	def decodeAES(self, data):
		decoded = self.decodedAES(data)
		return decoded


def PasserAesDecode(key, data):
	return PasserCrypto(key).decodeAES(data)


def PasserAesEncode(key, data):
	return PasserCrypto(key).encodeAES(data)


def otp_generator():
        return "".join(map(str, [randint(1,9) for r in xrange(16)]))


def generate_password(min_length=8, max_length=12, letters=True, numbers=True, symbols=True, spaces=False):
	choice = ''
	choices += _letters if letters else ''
	choices += _numbers if numbers else ''
	choices += _symbols if symbols else ''
	choices += _spaces if spaces else ''
	choices = ''.join(sample(choices, len(choices)))
	return (
		''.join(candidate) for candidate in
		chain.from_iterable(
			product(
				choices,
				repeat=i,
			) for i in range(min_length, max_length + 1),
		)
	)
