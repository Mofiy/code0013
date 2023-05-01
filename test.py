import BinanceTrader

api_key = 'your_api_key'
api_secret = 'your_api_secret'
db_name = 'trades.db'
trader = BinanceTrader(api_key, api_secret, db_name)

# размещение ордера на покупку 0.01 BTCUSDT по текущей цене
trader.place_order('BTCUSDT', 'BUY', 0.01)

# размещение ордера на продажу 0.01 BTCUSDT по цене 40000
trader.place_order('BTCUSDT', 'SELL', 0.01, 40000)

# получение списка открытых позиций
positions = trader.get_open_positions()
print(positions)

# закрытие позиции для символа BTCUSDT
trader.close_position('BTCUSDT')