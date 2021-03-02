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

    def trade(self):
        gate = GateWs("wss://ws.gate.io/v4/", self.api_key, self.api_secret)
        ##Check server connectivity.
        # print(gate.gateRequest(random.randint(0,99999),'server.ping',[]))

        ##Acquire server time.
        # print(gate.gateRequest(random.randint(0,99999),'server.time',[]))

        ##Query ticker of specified market, including price, deal volume etc in certain period.
        # print(gate.gateRequest(random.randint(0,99999),'ticker.query',["EOS_USDT",86400]))

        ##Subscribe market ticker.
        # print(gate.gateRequest(random.randint(0,99999),'ticker.subscribe',["BOT_USDT"]))

        ##Unsubscribe market ticker.
        # print(gate.gateRequest(random.randint(0,99999),'ticker.unsubscribe',[]))

        ##Query latest trades information, including time, price, amount, type and so on.
        # print(gate.gateRequest(random.randint(0,99999),'trade.query',["EOS_USDT",2,7177813]))

        ##Subscribe trades update notification.
        # print(gate.gateRequest(random.randint(0,99999),'trades.subscribe',["ETH_USDT","BTC_USDT"]))

        ##Unsubscribe trades update notification.
        # print(gate.gateRequest(random.randint(0,99999),'trades.unsubscribe',[]))

        ##Query specified market depth.
        # print(gate.gateRequest(random.randint(0,99999),'depth.query',["EOS_USDT",5,"0.0001"]))

        ##Subscribe depth.
        # print(gate.gateRequest(random.randint(0,99999),'depth.subscribe',["ETH_USDT",5,"0.0001"]))

        ##Unsbscribe specified market depth.
        # print(gate.gateRequest(random.randint(0,99999),'depth.unsubscribe',[]))

        ##Query specified market kline information
        # print(gate.gateRequest(random.randint(0,99999),'kline.query',["BTC_USDT",1,1516951219,1800]))

        ##Subscribe specified market kline information.
        # print(gate.gateRequest(random.randint(0,99999),'kline.subscribe',["BTC_USDT",1800]))

        ##Unsubsribe specified market kline information.
        # print(gate.gateRequest(random.randint(0,99999),'kline.unsubscribe',[]))

        ##Notify kline information of subscribed market.
        # print(gate.gateRequest(random.randint(0,99999),'kline.update',[1492358400,"7000.00","8000.0","8100.00","6800.00","1000.00","123456.00","BTC_USDT"]))

        ##Signature based authorization.
        # print(gate.gateSign(random.randint(0,99999),'server.sign',[]))

        ##Query user unexecuted orders
        # print(gate.gateRequest(random.randint(0,99999),'order.query',["BTC_USDT",0,10]))

        ##Subscribe user orders update
        # print(gate.gateRequest(random.randint(0,99999),'order.subscribe',["BTC_USDT"]))

        ##Notify user orders information when an order is put, updated or finished.
        # print(gate.gateRequest(random.randint(0,99999),'order.update',[2,"12345654654"]))

        ##Unubscribe user orders update notification, for all markets.
        # print(gate.gateRequest(random.randint(0,99999),'order.unsubscribe',[]))

        ##Acquire user balance information of specified asset or assets.
        print(gate.gateRequest(random.randint(0, 99999), 'balance.query', ["BTC"]))
        print(gate.gateRequest(random.randint(0, 99999), 'balance.query', ["USDT"]))
        print(gate.gateRequest(random.randint(0, 99999), 'balance.query', ["ETH"]))

        ##Subscribe for user balance update.
        # print(gate.gateRequest(random.randint(0,99999),'balance.subscribe',["BTC"]))

        ##Notify user balance update.
        # print(gate.gateRequest(random.randint(0,99999),'balance.update',[{'EOS':{'available':'96.765323611874','freeze':'11'}}]))

        ##Unsubscribe user balance update.
        ##print(gate.gateRequest(random.randint(0,99999),'balance.unsubscribe',[]))

class GateAPIClient():
    def __init__(self):
        gateio_obj = GateioConfig()

        self.api_key = gateio_obj.getConfig['api_key']
        self.api_secret = gateio_obj.getConfig['api_secret']
        self.host_used = gateio_obj.getConfig['host_used']

    def trade(self, currency_pair):
        # type: (RunConfig) -> None
        # currency_pair = "BTC_USDT"
        currency = currency_pair.split("_")[1]

        # Initialize API client
        # Setting host is optional. It defaults to https://api.gateio.ws/api/v4
        config = Configuration(key=self.api_key, secret=self.api_secret, host=self.host_used)
        spot_api = SpotApi(ApiClient(config))
        pair = spot_api.get_currency_pair(currency_pair)
        # logger.info("testing against currency pair: " + currency_pair)
        min_amount = pair.min_quote_amount

        # get last price
        tickers = spot_api.list_tickers(currency_pair=currency_pair)
        assert len(tickers) == 1
        last_price = tickers[0].last

        # make sure balance is enough
        order_amount = D(min_amount) * 2
        accounts = spot_api.list_spot_accounts(currency=currency)
        assert len(accounts) == 1
        available = D(accounts[0].available)
        # logger.info("Account available: %s %s", str(available), currency)
        print(f'Account available: {str(available)} {currency}')
        if available < order_amount:
            #logger.error("Account balance not enough")
            print(f'Account balance not enough')
            return
    """
        order = Order(amount=str(order_amount), price=last_price, side='buy', currency_pair=currency_pair)
        logger.info("place a spot %s order in %s with amount %s and price %s", order.side, order.currency_pair,
                    order.amount, order.price)
        created = spot_api.create_order(order)
        logger.info("order created with id %s, status %s", created.id, created.status)
        if created.status == 'open':
            order_result = spot_api.get_order(created.id, currency_pair)
            logger.info("order %s filled %s, left: %s", order_result.id, order_result.filled_total, order_result.left)
            result = spot_api.cancel_order(order_result.id, currency_pair)
            if result.status == 'cancelled':
                logger.info("order %s cancelled", result.id)
        else:
            trades = spot_api.list_my_trades(currency_pair, order_id=created.id)
            assert len(trades) > 0
            for t in trades:
                logger.info("order %s filled %s with price %s", t.order_id, t.amount, t.price)"""

# client = GateAPIClient()
# client.trade('BTC_USDT')

ws_client = GateWSClient()
res = ws_client.getBalance('usdt')
print(res)
res = ws_client.getBalance('link')
print(res)
res = ws_client.getBalance('fil')
print(res)
res = ws_client.getBalance('dot')
print(res['result'])


