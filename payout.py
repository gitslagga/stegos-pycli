#!/usr/bin/env python3

import asyncio
import json
import stegos
import logging
import setting

async def client_from_node():
    client = stegos.StegosClient(node_id=setting.NODE_ID,
                                 uri=setting.URI,
                                 accounts=setting.ACCOUNTS,
                                 master_key=setting.MASTER_KEY,
                                 api_key=setting.API_KEY)

    await client.connect()
    return client


async def my_app():
    client = await client_from_node()

    print("Waiting for sync!")
    await client.wait_sync()
    balance = await client.get_balance(setting.ACCOUNT_ID)

    print(f"client balance before payments: {balance}")
    print(f"send: {setting.ACCOUNT_ID}")
    print(f"receive: {setting.TO_ACCOUNT}")

    await client.payment_with_confirmation(setting.ACCOUNT_ID, setting.TO_ACCOUNT, setting.TO_AMOUNT, comment="Hi from Stegos")

    balance = await client.get_balance('heap')
    print(f"client balance after payments: {balance}")

if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(my_app())