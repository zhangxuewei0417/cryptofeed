import time
from decimal import Decimal as D
from decimal import getcontext
from cryptofeed.defines import BID, ASK
import gate_api

from examples.spot import GateAPIClient, GateWSClient


class Arbitrage:
    USDT = 'USDT'
    BTC = 'BTC'
    ETH = 'ETH'
    feed = ''
    fee = D('0.02')

    def __init__(self):
        pass

    def addDataToGraph(self, feed, g, symbol, book, timestamp, receipt_timestamp):
        self.feed = feed
        # symbol: BTC-USDT
        coin_a = symbol.split('-')[0]  # BTC
        coin_b = symbol.split('-')[1]  # USDT

        if not g.has_node(coin_a):
            g.add_node(coin_a)
            # print(f'coin {coin_a} is added')

        if not g.has_node(coin_b):
            g.add_node(coin_b)
            # print(f'coin {coin_b} is added')

        # Timestamp: 1614114411.322199 Cryptofeed Receipt: 1614114411.322199 Feed: GATEIO Pair: GAS-USDT Book Bid is
        # SortedDict({D('2.899'): D('1.3745'), D('2.985'): D('1.3745'), D('3.072'): D('1.3745'), D('3.158'): D(
        # '1.3745'), D('3.226'): D('1.8859'), D('3.245'): D('1.3745'), D('3.331'): D('1.3745'), D('3.418'): D(
        # '1.3745'), D('3.5'): D('127.9956'), D('3.504'): D('1.3745'), D('3.591'): D('1.3745'), D('3.677'): D(
        # '11.3745'), D('3.764'): D('1.3745'), D('3.85'): D('1.3745'), D('3.937'): D('1.3745'), D('4'): D('1017'),
        # D('4.023'): D('1.3745'), D('4.11'): D('1.3745'), D('4.88'): D('108.6065'), D('4.989'): D('36.1017'),
        # D('5'): D('1'), D('5.454'): D('20'), D('6.06'): D('15'), D('6.174'): D('100'), D('6.181'): D('20'),
        # D('6.75'): D('7.407'), D('6.754'): D('2.2209'), D('6.755'): D('298.22618598'), D('7.466'): D('62.751'),
        # D('7.7'): D('71.24294')}) Ask  is SortedDict({D('8.134'): D('13.6295'), D('8.135'): D('71.32127'),
        # D('8.299'): D('100'), D('8.899'): D('14.1037'), D('8.9'): D('12.2404'), D('9.09'): D('1.472'), D('9.8'): D(
        # '12.2405'), D('9.878'): D('329.50995'), D('10'): D('410.7678'), D('10.271'): D('7.984'), D('10.298'): D(
        # '100'), D('10.508'): D('190.3433'), D('10.6'): D('7.571965'), D('10.605'): D('0.6145'), D('10.606'): D(
        # '992.122782'), D('10.71'): D('110.251289'), D('11.363'): D('10.5974'), D('11.668'): D('27.82424'),
        # D('11.818'): D('3.41316'), D('12.121'): D('91.567849'), D('12.878'): D('865.469263'), D('13'): D(
        # '49.9175'), D('13.722'): D('82.913'), D('13.8'): D('82.9595'), D('14.008'): D('0.9287'), D('14.5'): D('5'),
        # D('14.6'): D('7.04089'), D('15.5'): D('9.98'), D('15.879'): D('14.5664'), D('15.99'): D('8.5')})

        # print(f'symbol {symbol}: {book}')
        if len(book[BID]) == 0 or len(book[ASK]) == 0:
            return
        first_bid_price = next(iter(reversed(book[BID])))
        first_bid_volume = next(iter(reversed(book[BID].values())))
        first_ask_price = next(iter(book[ASK]))
        first_ask_volume = next(iter(book[ASK].values()))

        # coin_a to coin_b edge uses bid price
        # example: convert 100 ETH to USDT, 100 * bid price
        if g.has_edge(coin_a, coin_b):
            g[coin_a][coin_b]['rate'] = first_bid_price
            g[coin_a][coin_b]['vol_count'] = first_bid_volume
            g[coin_a][coin_b]['book'] = reversed(book[BID])
            g[coin_a][coin_b]['timestamp'] = timestamp
            g[coin_a][coin_b]['receipt_timestamp'] = receipt_timestamp

            # print(f'{coin_a} to {coin_b} edge updated: rate: {first_bid_price}')

        else:
            g.add_edge(coin_a, coin_b, pair=symbol, rate=first_bid_price, vol_count=first_bid_volume,
                       book=book[BID], timestamp=timestamp, receipt_timestamp=receipt_timestamp)
            # print(f'{coin_a} to {coin_b} edge added')

        # coin_b to coin_a edge uses (1 / ask price)
        # example: convert 100 USDT to ETH, 100 / ask price
        if g.has_edge(coin_b, coin_a):
            g[coin_b][coin_a]['rate'] = D(1) / first_ask_price
            g[coin_b][coin_a]['vol_count'] = first_ask_volume
            g[coin_b][coin_a]['book'] = book[ASK]
            g[coin_a][coin_b]['timestamp'] = timestamp
            g[coin_a][coin_b]['receipt_timestamp'] = receipt_timestamp

            # print(f'{coin_b} to {coin_a} edge updated: rate: {D(1) / first_ask_price}')
        else:
            g.add_edge(coin_b, coin_a, pair=symbol, rate=(D(1) / first_ask_price), vol_count=first_ask_volume,
                       book=book[ASK], timestamp=timestamp, receipt_timestamp=receipt_timestamp)

            # print(f'{coin_b} to {coin_a} edge added')

    # example: invest_coin = USDT, coin = ZKS, intermediate_coin = ETH
    def simulateOrdering(self, g, initial_invest_amount, invest_coin, coin, intermediate_coin, invest_increase):
        if g.has_edge(coin, intermediate_coin) and g.has_edge(coin, invest_coin):

            invest2coin_amount = D(g.get_edge_data(invest_coin, coin)['vol_count'])  # 245 SWAP
            invest2coin_rate = D(g.get_edge_data(invest_coin, coin)['rate'])  # 4.09 USDT

            coin2intermediate_amount = D(g.get_edge_data(coin, intermediate_coin)['vol_count'])  # 52 SWAP
            coin2intermediate_rate = D(g.get_edge_data(coin, intermediate_coin)['rate'])  # 0.0026 ETH

            intermediate2invest_amount = D(g.get_edge_data(intermediate_coin, invest_coin)['vol_count'])  # 0.5 ETH
            intermediate2invest_rate = D(g.get_edge_data(intermediate_coin, invest_coin)['rate'])  # 1498 USD

            invest_amount = min(initial_invest_amount,
                                min(invest2coin_amount, coin2intermediate_amount) / invest2coin_rate)

            # repeatedly find the smallest amount can invest
            v1 = invest_amount * invest2coin_rate * D(1 - self.fee)
            v2 = v1 * coin2intermediate_rate * D(1 - self.fee)
            v3 = v2 * intermediate2invest_rate * D(1 - self.fee)
            # print(f'{self.feed} {invest_amount} {invest_coin}->{v1} {coin}->{v2} {intermediate_coin}-> {v3} {
            # invest_coin}')
            if v3 >= invest_amount * D(1 + invest_increase):
                print(
                    f'{self.feed} {invest_amount} {invest_coin}->{v1} {coin}->'
                    f'{v2} {intermediate_coin}-> {v3} {invest_coin}')

                api_client = GateAPIClient()
                ws_client = GateWSClient()
                pair1 = coin + '_' + invest_coin

                api_client.buyFast(pair1, v1)
                while True:
                    if not ws_client.hasUnexecutedOrder(pair1):
                        break
                    time.sleep(0.01)

                pair2 = coin + '_' + intermediate_coin
                api_client.sellFast(pair2, v1)
                while True:
                    if not ws_client.hasUnexecutedOrder(pair2):
                        break
                    time.sleep(0.01)

                pair3 = None
                if intermediate_coin.lower() == 'eth' and invest_coin:
                    pair3 = self.formPair(intermediate_coin, invest_coin)
                balance = ws_client.getBalanceSimple(intermediate_coin)
                api_client.sellFast(pair3, balance)
                while True:
                    if not ws_client.hasUnexecutedOrder(pair3):
                        break
                    time.sleep(0.01)



    def formPair(self, coin1, coin2):
        if coin1.lower() == 'eth':
            return coin1 + '_' + coin2
        elif coin1.lower() == 'btc' and coin2.lower() == 'usdt':
            return coin1 + '_' + coin2
        elif coin1.lower() == 'btc' and coin2.lower() == 'eth':
            return coin2 + '_' + coin1
        elif coin1.lower() == 'usdt' and coin2.lower() == 'btc':
            return coin2 + '_' + coin1
        elif coin1.lower() == 'usdt' and coin2.lower() == 'eth':
            return coin2 + '_' + coin1


    def potentialArbitrage(self, g, symbol):

        invest_usdt = D(100)  # 100 USDT
        invest_eth = D('0.1')  # 0.1 ETH
        invest_btc = D('0.01')  # 0.01 BTC

        # symbol: ETH-USDT
        # coin: ETH
        coin = symbol.split('-')[0]
        # print(f'final potential arbitrage of {coin}')

        if coin not in (Arbitrage.ETH, Arbitrage.USDT, Arbitrage.BTC) \
                and g.has_edge(Arbitrage.ETH, Arbitrage.USDT) \
                and g.has_edge(Arbitrage.ETH, Arbitrage.BTC) \
                and g.has_edge(Arbitrage.BTC, Arbitrage.USDT):
            self.simulateOrdering(g, D('100'), Arbitrage.USDT, coin, Arbitrage.ETH, D(0))
            self.simulateOrdering(g, D('0.1'), Arbitrage.ETH, coin, Arbitrage.USDT, D(0))
            self.simulateOrdering(g, D('0.01'), Arbitrage.BTC, coin, Arbitrage.ETH, D(0))
            self.simulateOrdering(g, D('100'), Arbitrage.USDT, coin, Arbitrage.BTC, D(0))
