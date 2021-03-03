'''
Copyright (C) 2017-2021  Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''
from decimal import Decimal

import networkx as nx
from cryptofeed.backends.redis import BookRedis

from cryptofeed.symbols import binance_symbols, gateio_symbols, huobi_symbols, huobi_us_symbols
from cryptofeed import FeedHandler
from cryptofeed.callback import BookCallback, FundingCallback, TickerCallback, TradeCallback, FuturesIndexCallback, \
    OpenInterestCallback
from cryptofeed.defines import BID, ASK, BLOCKCHAIN, COINBASE, FUNDING, GEMINI, L2_BOOK, L3_BOOK, OPEN_INTEREST, TICKER, \
    TRADES, VOLUME, FUTURES_INDEX, BOOK_DELTA
from cryptofeed.exchanges import (FTX, Binance, BinanceFutures, Bitfinex, Bitflyer, Bitmax, Bitmex, Bitstamp, Bittrex,
                                  Coinbase, Gateio,
                                  HitBTC, Huobi, HuobiDM, HuobiSwap, Kraken, OKCoin, OKEx, Poloniex, Bybit)

# Examples of some handlers for different updates. These currently don't do much.
# Handlers should conform to the patterns/signatures in callback.py
# Handlers can be normal methods/functions or async. The feedhandler is paused
# while the callbacks are being handled (unless they in turn await other functions or I/O)
# so they should be as lightweight as possible
from examples.arbitrage import Arbitrage
import time

g_dict = {}
g = nx.DiGraph()
g_dict['GATEIO'] = g
g_huobi = nx.DiGraph()
g_dict['HUOBI'] = g_huobi

async def book(feed, symbol, book, timestamp, receipt_timestamp):
    # print(f'Timestamp: {timestamp} Cryptofeed Receipt: {receipt_timestamp} Feed: {feed} Pair: {symbol} Book Bid is {book[BID]} Ask  is {book[ASK]}')
    # print(f'bid is {next(iter(reversed(book[BID].items())))} ask is {next(iter(book[ASK].items()))}')
    arbitrage = Arbitrage()
    arbitrage.addDataToGraph(feed, g_dict[feed], symbol, book, timestamp, receipt_timestamp)
    arbitrage.potentialArbitrage(g_dict[feed], symbol)

def main():
    config = {'log': {'filename': 'gateio.log', 'level': 'INFO'}}
    # the config will be automatically passed into any exchanges set up by string. Instantiated exchange objects would need to pass the config in manually.
    f = FeedHandler(config=config)

    pairs = list(gateio_symbols().keys())
    f.add_feed(Gateio(symbols=pairs, channels=[L2_BOOK], callbacks={L2_BOOK: BookCallback(book)}))
    # f.add_feed(Gateio(symbols=['BTC-USDT', 'ETH-USDT', 'ETH-BTC', 'ZKS-ETH', 'ZKS-USDT'], channels=[L2_BOOK], callbacks={L2_BOOK: BookCallback(book)}))

    # huobi_pairs = list(huobi_us_symbols().keys())
    # f.add_feed(Huobi(symbols=huobi_pairs, channels=[L2_BOOK], callbacks={L2_BOOK: BookCallback(book)}))

    f.run()


if __name__ == '__main__':
    main()
