#!/usr/bin/env python

import asyncio
import json
import stegos
import setting

BOT_ACCOUNTS = 5

async def client_from_node():
    client = stegos.StegosClient(node_id=setting.NODE_ID,
                                 uri=setting.URI,
                                 master_key=setting.MASTER_KEY,
                                 api_key=setting.API_KEY)

    await client.connect()
    return client

async def get_address():
    node = await client_from_node()
    print("Waiting for sync!")
    await node.wait_sync()

    ids = await node.list_accounts()
    for id in ids:
        address = await node.get_address(id)
        print(f"get_address: {id} = {address}")

async def create_account():
    node = await client_from_node()
    print("Waiting for sync!")
    await node.wait_sync()

    ids = await node.list_accounts()
    print(f"Node0 has accounts: {ids}")
    if len(ids.keys()) < BOT_ACCOUNTS:
        for n in range(0, BOT_ACCOUNTS - len(ids.keys())):
            account_info = await node.create_account()
            print(f"create_account: {n} = {account_info}")
    else:
        for id in ids:
            address = await node.get_address(id)
            print(f"get_address: {id} = {address}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_address())
