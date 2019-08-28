#!/usr/bin/env python3

import asyncio
import json
import stegos
import logging


async def client_from_node(node):
    client = stegos.StegosClient(node_id=node['node_id'],
                                 uri=node['uri'],
                                 accounts=node['accounts'],
                                 master_key=node['master_key'],
                                 api_key=node['api_key'])

    await client.connect()
    return client


async def my_app(heap_node, toAddress):
    node01 = await client_from_node(heap_node)

    my_account = list(heap_node['accounts'].keys())[0]
    print("Waiting for sync!")
    await node01.wait_sync()
    balance = await node01.get_balance(my_account)

    print(f"Node01 balance before payments: {balance}")
    print(f"send: {heap_node['accounts'][my_account]}")
    print(f"receive: {toAddress}")

    await node01.payment_with_confirmation(my_account, toAddress, 1_000, comment="Hi from Stegos")

    balance = await node01.get_balance('heap')
    print(f"Node01 balance after payments: {balance}")

if __name__ == '__main__':
    heap = {
        "node_id": "heap",
        "accounts": {
            "1": "7f9nY9R4LYwmTuc3oEVhDETx6pq5uMpxYzS7nX4F5jNVn6MTcF1"
        },
        "master_key": "123456",
        "api_key": "3cYdoIdwr3b49eyuH92oPw==",
        "uri": "ws://127.0.0.1:3145",
    }
    
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        my_app(heap, "7fd3kYCiBWSGg5bn7dC5EMWHLS8Ndsw8C2VFsHnzDcKmWmQ8jj6"))