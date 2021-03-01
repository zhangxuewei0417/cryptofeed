# !/usr/bin/env python
# coding: utf-8
import logging
import threading
from decimal import Decimal as D
from gate_api import ApiClient, Configuration, Order, SpotApi
from six.moves.urllib.parse import urlparse
import yaml
import os
from GateWS import GateWs
import random
# logger = logging.getLogger(__name__)


class GateioConfig():
    _instance_lock = threading.Lock()
    configLoaded = False
    config_dict = {}

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(GateioConfig, "_instance"):
            with GateioConfig._instance_lock:
                if not hasattr(GateioConfig, "_instance"):
                    GateioConfig._instance = object.__new__(cls)
        return GateioConfig._instance

    @property
    def getConfig(self):
        if not GateioConfig.configLoaded:
            with GateioConfig._instance_lock:
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
    def __init__(self):
        self.gateio_config = GateioConfig()
        self.api_key = self.gateio_config.api_key
        self.api_secret = self.gateio_config.api_secret

    def trade(self):
        gate = GateWs("wss://ws.gate.io/v3/", "your key", "your secret.")
        print(gate.gateRequest(random.randint(0, 99999), 'server.ping', []))


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

client = GateAPIClient()
client.trade('BTC_USDT')
