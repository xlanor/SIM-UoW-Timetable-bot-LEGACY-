#! /usr/bin/env python3
#-*- coding: utf-8 -*-
##
# Cronus encryption mod
# Thanks to stackoverflow 
# Written by xlanor
##
import base64,hashlib
from Cryptodome import Random
from Cryptodome.Cipher import AES

class Encrypt():
	def encrypt(self,password,encryptionkey,encryption_type):
		BS = 16
		pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
		unpad = lambda s : s[0:-s[-1]]
		key = hashlib.sha256(encryptionkey.encode('utf-8')).digest()
		if encryption_type == "encrypt":
			raw = pad(password).encode("utf-8")
			iv = Random.new().read( AES.block_size )
			cipher = AES.new( key, AES.MODE_CBC, iv )
			encrypted = base64.b64encode( iv + cipher.encrypt( raw ) )
			return encrypted
		else:
			enc = base64.b64decode(password)
			iv = enc[:16]
			cipher = AES.new(key, AES.MODE_CBC, iv )
			decrypted = unpad(cipher.decrypt( enc[16:] )).decode("utf-8")
			return decrypted
