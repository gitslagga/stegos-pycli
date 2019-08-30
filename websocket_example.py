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
    websocket = await websockets.connect('ws://localhost:3145', ping_timeout=None)

    req = {
        "type": "balance_info",
        "account_id": '1',
        "id": 1,
    }
    await websocket.send(str(base64.standard_b64encode(encrypt(api_key, json.dumps(req))), "utf-8"))
    print('send request origin ', req)
    print('send request encrypt ', str(base64.standard_b64encode(encrypt(api_key, json.dumps(req))), "utf-8"))

    while True:
        response = await websocket.recv()
        print("receive response encrypt ", response)
        response = decrypt(api_key, base64.b64decode(response))
        response = json.loads(response)

        # if resp['type'] == 'balance_changed' or resp['type'] == 'balance_info':
            # print(f"balance_changed {response}")

        # if resp['type'] == 'sync_changed' and resp['is_synchronized']:
            # print(f"sync_changed or is_synchronized {response}")

        print("receive response origin ", response)
        time.sleep(5)
asyncio.get_event_loop().run_until_complete(hello())








# send request origin  {'type': 'balance_info', 'account_id': '1', 'id': 1}
# send request encrypt  QwVxuiPXH5YTUSRv1aJ+Y2ZpjwT1Q+QXcyP0q2oKrtEGrsabzcJPa+LXrLfKTHwzMV/0CNWC+Ho4yT6ec5D5STkp19s=
# receive response encrypt  kdufVAXA0YH/rRt/eJ17znoBHaU9ahx7vq4CtbY5X0+zlqZgQ08032ACQ0Si3B8q9F1o9DMznxGu4AV8XJqPWlK57jlk7xvIbDmnlav+kqCLHLfk8DLpk07BPBh8aEIQU5XiCOrfRYzPQjWPsRUdyLmd7A==
# receive response origin  {'account_id': '1', 'type': 'balance_info', 'balance': 1782764007, 'available_balance': 1782764007, 'id': 1}
# receive response encrypt  Sr7ulOn//xciIdQuRf5nqpgu7x79CCFVU2JLYzaDcFMRgE1FW3Mun3oJEHCO+32X/HU0tM9IiYNkDk5em/CSZYVG87dnSXzbwyWp6NODXVag3o+/GaWP
# receive response origin  {'type': 'rollback_micro_block', 'epoch': 14020, 'offset': 59, 'statuses': {}}