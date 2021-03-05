# !/usr/bin/env python
# coding: utf-8
import asyncio
import logging
import threading
from decimal import Decimal as D
from gate_api import ApiClient, Configuration, Order, SpotApi
from six.moves.urllib.parse import urlparse
import yaml
import os
from GateWS import GateWs
import random
import json
import time


# logger = logging.getLogger(__name__)


class GateioConfig():
    # _instance_lock = threading.Lock()
    configLoaded = False
    config_dict = {}

    @property
    def getConfig(self):
        if not GateioConfig.configLoaded:
            # with GateioConfig._instance_lock:
            self.loadConfig()
        return GateioConfig.config_dict

    def loadConfig(self):
        filename = os.path.join(os.path.dirname(__file__), 'config.yaml').replace("\\", "/")
        f = open(filename)

        gateio_config = yaml.load(f)
        GateioConfig.config_dict = {'api_key': gateio_config['api_key'],
                                    'api_secret': gateio_config['api_secret'],
                                    'host_used': gateio_config['host_used']}
        GateioConfig.configLoaded = True


class GateWSClient():
    gate_ws_client = None

    # _instance_lock = threading.Lock()

    def getGateWsClient(self):
        if GateWSClient.gate_ws_client is None:
            gateio_config = GateioConfig()

            api_key = gateio_config.getConfig['api_key']
            api_secret = gateio_config.getConfig['api_secret']
            host_used = gateio_config.getConfig['host_used']

            GateWSClient.gate_ws_client = GateWs("wss://ws.gate.io/v4/", api_key, api_secret)
        return GateWSClient.gate_ws_client

    def getBalance(self, coin):
        ws_client = self.getGateWsClient()
        coin = coin.upper()
        return ws_client.gateRequest(random.randint(0, 99999), 'balance.query', [coin])

    def getBalanceSimple(self, coin):
        balance = None
        coin = coin.upper()
        res = self.getBalance(coin)
        if 'result' in res:
            balance = res['result'][coin]['available']
        return balance

    def getTicker(self, pair):
        pair = pair.upper()
        ws_client = self.getGateWsClient()
        return ws_client.gateRequest(random.randint(0, 99999), 'ticker.query', [pair, 86400])

    # {'error': None, 'result': {'limit': 10, 'offset': 0, 'total': 1, 'records': [
    #     {'id': 33989855664, 'market': 'ETH_USDT', 'tif': 1, 'user': 3209033, 'ctime': 1614758938.861532,
    #      'mtime': 1614758938.861532, 'price': '1568.25', 'amount': '0.01', 'iceberg': '0', 'left': '0.01',
    #      'deal_fee_rebate': '0', 'deal_point_fee': '0', 'gt_discount': '2', 'gt_taker_fee': '0', 'gt_maker_fee': '0',
    #      'deal_gt_fee': '0', 'orderType': 1, 'type': 2, 'dealFee': '0', 'filledAmount': '0', 'filledTotal': '0'}]},
    #  'id': 75791}

    # {'error': None, 'result': {'limit': 10, 'offset': 0, 'total': 0, 'records': []}, 'id': 49457}

    def getUnexecutedOrder(self, pair):
        pair = pair.upper()
        ws_client = self.getGateWsClient()
        return ws_client.gateRequest(random.randint(0, 99999), 'order.query', [pair, 0, 10])

    # return 0 if there is no open order, otherwise return order id
    def hasUnexecutedOrder(self, pair):
        pair = pair.upper()
        res = self.getUnexecutedOrder(pair)
        records = res['result']['records']
        if len(records) == 0:
            return 0
        else:
            order = records[0]
            print(f'price: {order["price"]} amount: {order["amount"]}')
            return order['id']

    def getOrderBook(self, pair):
        pair = pair.upper()
        ws_client = self.getGateWsClient()
        return ws_client.gateRequest(random.randint(0, 99999), 'spot.book_ticker', [pair, 0, 10])

    def getDepth(self, pair):
        pair = pair.upper()
        ws_client = self.getGateWsClient()
        return ws_client.gateRequest(random.randint(0, 99999), 'depth.query', [pair, 10, "0.00000000001"])

    def getHighestBuyPrice(self, pair):
        pair = pair.upper()
        res = self.getDepth(pair)
        return res['result']['bids'][0][0]

    def getLowestSellPrice(self, pair):
        pair = pair.upper()
        res = self.getDepth(pair)
        return res['result']['asks'][0][0]


class GateAPIClient():
    gate_api_client = None

    def getAPIClient(self):
        if GateAPIClient.gate_api_client is None:
            gateio_obj = GateioConfig()

            api_key = gateio_obj.getConfig['api_key']
            api_secret = gateio_obj.getConfig['api_secret']
            host_used = gateio_obj.getConfig['host_used']

            # Initialize API client
            # Setting host is optional. It defaults to https://api.gateio.ws/api/v4
            config = Configuration(key=api_key, secret=api_secret, host=host_used)
            GateAPIClient.gate_api_client = SpotApi(ApiClient(config))
        return GateAPIClient.gate_api_client

    def buy(self, pair, order_amount, last_price):
        return self.trade(pair, order_amount, last_price, 'buy')

    # buy using the lowest ask price
    def buyFast(self, pair, order_amount):
        pair = pair.upper()
        ws = GateWSClient()
        price = ws.getLowestSellPrice(pair)
        return self.buy(pair, order_amount, price)

    def sell(self, pair, order_amount, last_price):
        return self.trade(pair, order_amount, last_price, 'sell')

    # sell to the highest bid price
    def sellFast(self, pair, order_amount):
        pair = pair.upper()
        ws = GateWSClient()
        price = ws.getHighestBuyPrice(pair)
        return self.sell(pair, order_amount, price)

    def trade(self, pair, order_amount, last_price, side):

        spot_api = self.getAPIClient()

        order = Order(amount=str(order_amount), price=last_price, side=side, currency_pair=pair)
        print(f'place a spot {order.side} order in {order.currency_pair} with amount {order.amount} and price {order.price}')
        created = None
        # created = spot_api.create_order(order)
        # print(f'order created with id {created.id}, status {created.status}')
        return created


#api_client = GateAPIClient()
# ws_client = GateWSClient()
#api_client.buyFast('skm_usdt', '0.001')
# while True:
#     if not ws_client.hasUnexecutedOrder('eth_usdt'):
#         break
#     time.sleep(0.01)
#
# api_client.sellFast('eth_usdt', '0.001')
# while True:
#     if not ws_client.hasUnexecutedOrder('eth_usdt'):
#         break
#     time.sleep(0.01)
# client.trade('BTC_USDT')

# ws_client = GateWSClient()
# #
# print(ws_client.getDepth('zks_usdt'))
# for i in range(1, 60):
#     time.sleep(i)
#     print(ws_client.getDepth('zks_usdt'))
# print(ws_client.getLowestSellPrice('zks_usdt'))
# print(ws_client.getHighestBuyPrice('zks_usdt'))
# print(ws_client.getUnexecutedOrder('eth_usdt'))
# print(ws_client.hasUnexecutedOrder('eth_usdt'))
