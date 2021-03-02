# -*- coding: utf-8 -*-
# author: か壞尐孩キ
import random

from websocket import create_connection
from websocket import WebSocketTimeoutException
import gzip
import time
import json
import hmac
import base64
import hashlib


def get_sign(secret_key, message):
    #h = (base64.b64encode(hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha512).digest())).decode()
    h = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha512).hexdigest()
    return h


class GateWs:
    ws = None
    server_signed = False

    def __init__(self, url, apiKey, secretKey):
        self.__url = url
        self.__apiKey = apiKey
        self.__secretKey = secretKey

    def gateGet(self, id, method, params):
        if (params == None):
            params = []
        ws = create_connection(self.__url)
        data = {'id': id, 'method': method, 'params': params}
        js = json.dumps(data)
        ws.send(js)
        return ws.recv()

    def gateSign(self):

        if GateWs.ws is None:
            GateWs.ws = create_connection(self.__url)
        nonce = int(time.time() * 1000)
        signature = get_sign(self.__secretKey, str(nonce))
        data = {'id': random.randint(0, 99999), 'method': 'server.sign', 'params': [self.__apiKey, signature, nonce]}
        js = json.dumps(data)
        GateWs.ws.send(js)
        GateWs.server_signed = True
        return print(f'signin {GateWs.ws.recv()}')

    def gateRequest(self, id, method, params):

        if GateWs.ws is None:
            GateWs.ws = create_connection(self.__url)

        if GateWs.server_signed is False:
            self.gateSign()

        if method == "server.sign":
            return
        else:
            try:
                data = {'id': id, 'method': method, 'params': params}
                js = json.dumps(data)
                GateWs.ws.send(js)
            except WebSocketTimeoutException:
                self.gateSign()
                GateWs.ws.send(js)
            finally:
                return GateWs.ws.recv()

####https://www.gateio.io/####