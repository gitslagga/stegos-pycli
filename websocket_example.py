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


async def hello():
    async with websockets.connect('ws://localhost:3145') as websocket:

        name = input("What's your name? ")

        await websocket.send(str(base64.standard_b64encode(encrypt(api_key, json.dumps(name))), "utf-8"))
        print(f"send {name}")

        while True:
            resp = await websocket.recv()
            resp = decrypt(api_key, base64.b64decode(resp))
            resp = json.loads(resp)

            if resp['type'] == 'balance_changed' or resp['type'] == 'balance_info':
                print(f"receive {resp}")

            if resp['type'] == 'sync_changed' and resp['is_synchronized']:
                print("node is synchronized!")
                break

asyncio.get_event_loop().run_until_complete(hello())
