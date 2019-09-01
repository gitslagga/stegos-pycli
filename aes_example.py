# !/usr/bin/env python

# WS client example

import asyncio
import base64
import json
import time

import websockets
import binascii

from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto import Random

key_bytes = 16
api_key = base64.b64decode("3cYdoIdwr3b49eyuH92oPw==")


def encrypt(key, plaintext):
    assert len(key) == key_bytes

    # Choose a random, 16-byte IV.
    iv = Random.new().read(AES.block_size)

    # Convert the IV to a Python integer.
    iv_int = int(binascii.hexlify(iv), 16)

    # Create a new Counter object with IV = iv_int.
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)

    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)

    # Encrypt and return IV and ciphertext.
    ciphertext = aes.encrypt(plaintext)
    return iv + ciphertext


def decrypt(key, ciphertext):
    assert len(key) == key_bytes

    # Convert the IV to a Python integer.
    iv_int = int(binascii.hexlify(ciphertext[:16]), 16)

    # Create a new Counter object with IV = iv_int.
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)

    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)

    # Decrypt and return the plaintext.
    plaintext = aes.decrypt(ciphertext[16:])
    return plaintext


req = {
    "type": "balance_info",
    "account_id": '1',
    "id": 1,
} 
print('send request origin ', req)

encode = str(base64.standard_b64encode(encrypt(api_key, json.dumps(req))), "utf-8")
print('send request encrypt ', encode)

rsp = "QwVxuiPXH5YTUSRv1aJ+Y2ZpjwT1Q+QXcyP0q2oKrtEGrsabzcJPa+LXrLfKTHwzMV/0CNWC+Ho4yT6ec5D5STkp19s="
decode = decrypt(api_key, base64.b64decode(rsp))
print("receive response origin ", rsp)
print("receive response decrypt ", decode)
print("receive response json loads ", json.loads(decode))

