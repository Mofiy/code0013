from binance.client import Client
import sqlite3


class BinanceTrader:

    def __init__(self, api_key, api_secret, db_name):
        self.client = Client(api_key, api_secret)
        self.client.API_URL = 'https://fapi.binance.com/fapi'
        # self.client.recv_window = 10000
        self.db_name = db_name
        self._create_tables()

    def _create_tables(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     symbol TEXT,
                     side TEXT,
                     quantity REAL,
                     price REAL,
                     time TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS positions
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     symbol TEXT,
                     quantity REAL,
                     entry_price REAL,
                     entry_time TIMESTAMP,
                     exit_price REAL,
                     exit_time TIMESTAMP,
                     profit REAL)''')
        conn.commit()
        conn.close()

    def place_order(self, symbol, side, quantity, price=None):
        if price is not None:
            order = self.client.futures_create_order(symbol=symbol, side=side, type='LIMIT', quantity=quantity,
                                                     price=price)
        else:
            order = self.client.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=quantity)
        self._log_trade(symbol, side, quantity, order['price'], order['transactTime'])

    def _log_trade(self, symbol, side, quantity, price, time):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''INSERT INTO trades (symbol, side, quantity, price, time)
                     VALUES (?, ?, ?, ?, ?)''', (symbol, side, quantity, price, time))
        conn.commit()
        conn.close()

    def get_open_positions(self):
        positions = []
        for position in self.client.futures_position_information():
            if float(position['positionAmt']) != 0:
                positions.append({'symbol': position['symbol'],
                                  'quantity': float(position['positionAmt']),
                                  'entry_price': float(position['entryPrice']),
                                  'entry_time': position['entryTime']})
        return positions

    def close_position(self, symbol, quantity=None):
        positions = self.client.futures_position_information()
        for position in positions:
            if position['symbol'] == symbol:
                if quantity is None:
                    quantity = abs(float(position['positionAmt']))
                side = 'BUY' if float(position['positionAmt']) < 0 else 'SELL'
                self.place_order(symbol, side, quantity)
                self._update_position(symbol, quantity, position['entryPrice'], position['entryTime'],
                                      position['markPrice'], position['updateTime'])
                break

    def _update_position(self, symbol, quantity, entry_price, entry_time, exit_price, exit_time):
        profit = (exit_price - entry_price) * quantity
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''INSERT INTO positions (symbol, quantity, entry_price, entry_time, exit_price, exit_time, profit)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (symbol, quantity, entry_price, entry_time, exit_price, exit_time, profit))
        conn.commit()
        conn.close()

    def place_order_max_amount(self, symbol, side):
        account = self.client.get_account()
        balance = float(account['balances'][symbol[:-4]]['free'])  # баланс в базовой валюте
        ticker = self.client.get_ticker(symbol=symbol)
        price = float(ticker['lastPrice'])
        amount = round(balance / price, 6)
        self.place_order(symbol, side, amount)
