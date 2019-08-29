from flask import Flask, abort, request, jsonify
from flask.json import JSONEncoder as BaseJSONEncoder
from gevent.pywsgi import WSGIServer
from logging.handlers import RotatingFileHandler

import logging
import json
import threading
import datetime
import decimal
import uuid
import requests
import asyncio
import stegos
import setting

app = Flask(__name__)

###################################### stegos connection ################################################
async def client_from_node():
    client = stegos.StegosClient(
        node_id=setting.NODE_ID,
        uri=setting.URI,
        accounts=setting.ACCOUNTS,
        master_key=setting.MASTER_KEY,
        api_key=setting.API_KEY
    )

    await client.connect()
    return client

loop = asyncio.get_event_loop()
websocket_client = loop.run_until_complete(client_from_node())
loop.run_until_complete(websocket_client.wait_sync())

###################################### rustful api ################################################
@app.route('/getinfo', methods=['POST'])
def getinfo():
    wallet_info = loop.run_until_complete(websocket_client.get_balance("1"))
    return jsonify({'code': 0, 'data': wallet_info})

@app.route('/getblockcount', methods=['POST'])
def getblockcount():
    block_count = websocket_client.getblockcount()
    return jsonify({'code': 0, 'data': block_count})

@app.route('/getnewaddress', methods=['POST'])
def getnewaddress():
    address = websocket_client.getnewaddress()
    privateKey = websocket_client.dumpprivkey(address)

    return jsonify({'code': 0, 'data': {
        "address": address,
        "privateKey": privateKey
    }})

@app.route('/getbalance', methods=['POST'])
def getbalance():
    balance = websocket_client.getbalance()
    return jsonify({'code': 0, 'data': balance})

@app.route('/sendtoaddress', methods=['POST'])
def sendtoaddress():
    app.logger.warning('request params: {}'.format(request.json))

    if not request.json or 'address' not in request.json or 'amount' not in request.json:
        abort(400)
    else:
        try:
            hash = websocket_client.sendtoaddress(request.json['address'], request.json['amount'])
        except Exception as ex:
            app.logger.warning('Sendtoaddress exception: {}'.format(ex))
            sendDingDing('Sendtoaddress exception: {}, request json: {}'.format(ex, request.json))
            return jsonify({'code': 500})
        return jsonify({'code': 0, 'data': hash})

@app.route('/listtransactions', methods=['POST'])
def listtransactions():
    start = 0
    num = 100

    if request.json and 'start' in request.json:
        start = request.json['start']
    if request.json and 'num' in request.json:
        num = request.json['num']

    try:
        list_transactions = websocket_client.listtransactions('*', num, start)
    except Exception as ex:
        app.logger.warning('listtransactions exception: {}'.format(ex))
        return jsonify({'code': 500})
    return jsonify({'code': 0, 'data': list_transactions})

@app.route('/listaddressgroupings', methods=['POST'])
def listaddressgroupings():
    address_groupings = websocket_client.listaddressgroupings()
    return jsonify({'code': 0, 'data': address_groupings})

@app.route('/getblock', methods=['POST'])
def getblock():
    app.logger.warning('request params: {}'.format(request.json))

    if not request.json or 'hashorheight' not in request.json:
        abort(400)
    else:
        try:
            block = websocket_client.getblock(request.json['hashorheight'])
        except Exception as ex:
            app.logger.warning('getblock exception: {}'.format(ex))
            return jsonify({'code': 500})
        return jsonify({'code': 0, 'data': block})

@app.route('/gettransaction', methods=['POST'])
def gettransaction():
    app.logger.warning('request params: {}'.format(request.json))

    if not request.json or 'txid' not in request.json:
        abort(400)
    else:
        try:
            transaction = websocket_client.gettransaction(request.json['txid'])
        except Exception as ex:
            app.logger.warning('gettransaction exception: {}'.format(ex))
            return jsonify({'code': 500})
        return jsonify({'code': 0, 'data': transaction})

###################################### send ding ding ################################################
def sendDingDing(content):
    headers = {
        'Content-Type': 'application/json',
        'Charset': 'utf-8'
    }
    request_data = {
        'msgtype': 'text',
        'text': {
            'content': content
        },
        'at': {
            'atMobiles': [],
            'isAtAll': True
        }
    }

    try:
        sendData = json.dumps(request_data)
        response = requests.post(url= setting.DINGDING_URL, headers= headers, data= sendData)
        content = response.content.decode()
        logging.warning('Dingding send message info: {}'.format(content))
    except Exception as ex:
        logging.warning('Dingding send message error: {}'.format(ex))

###################################### fix json format type ################################################
class JSONEncoder(BaseJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        if isinstance(o, decimal.Decimal):
            return str(o)
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, bytes):
            return o.decode("utf-8")
        return super(JSONEncoder, self).default(o)

app.json_encoder = JSONEncoder

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    handler = RotatingFileHandler('flask.log', maxBytes=100*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)
    logging.getLogger('websockets').addHandler(logging.NullHandler())
    logging.getLogger('websockets').setLevel(logging.CRITICAL)
    # app.run(debug=True)

    ###################################### production run ################################################
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
    