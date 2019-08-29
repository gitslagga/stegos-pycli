#!/usr/bin/env python3

import asyncio
import stegos
import logging
import setting

async def my_app():
    node01 = stegos.StegosClient(node_id=setting.NODE_ID,
                                 uri=setting.URI,
                                 accounts=setting.ACCOUNTS,
                                 master_key=setting.MASTER_KEY,
                                 api_key=setting.API_KEY)

    await node01.connect()

    print("Waiting for sync!")
    await node01.wait_sync()
    balance = await node01.get_balance('1')
    print(f"Node01 balance: {balance}")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(my_app())
