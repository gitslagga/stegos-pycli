#!/usr/bin/env python3

import asyncio
import json
import stegos
import setting

from prometheus_client import start_http_server

def load_nodes(path):
    f = open(path, "r")
    encoded = f.read()
    return json.loads(encoded)


async def client_from_node():
    client = stegos.StegosClient(node_id=setting.NODE_ID,
                                 uri=setting.URI,
                                 accounts=setting.ACCOUNTS,
                                 master_key=setting.MASTER_KEY,
                                 api_key=setting.API_KEY)

    await client.connect()
    return client


async def loop_payment(client, source, target, start_amount):
    amount = start_amount
    while True:
        await client.payment_with_confirmation(source, target, amount)
        amount = amount + 1


async def my_app():
    client = await client_from_node()

    print("Waiting for sync!")
    await client.wait_sync()

    balance = await client.get_balance(setting.ACCOUNT_ID)
    assert balance > 0

    asyncio.ensure_future(loop_payment(client, setting.ACCOUNT_ID, setting.TO_ACCOUNT, setting.TO_AMOUNT))


if __name__ == '__main__':
    start_http_server(8890)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(my_app())
    loop.run_forever()
