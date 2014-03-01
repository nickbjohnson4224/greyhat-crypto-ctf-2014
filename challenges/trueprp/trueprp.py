import os
import hashlib

class TruePRP(object):

	def __init__(self, key):
		"""
		Generate a permutation table for every input 16-bit word.
		
		This permutation is randomly sampled from all 16-bit permutations,
		so it is a *true* random permutation: there can be no weaknesses! 
		There are log2(16!) = 2^45 such permutations, so 45 bits of key
		entropy should be sufficient.
		"""
		
		self._table = [ i for i in xrange(2**16) ]

		# generate table using Fisher-Yates shuffle
		for i in xrange(2**16):
			

	def encrypt(self, data):
		"""
		Encrypt using CBC mode with the generated table as the block cipher.
		"""

		iv = os.urandom(2)

		return r''.join(chr(self._table[ord(b)]) for b in data)
