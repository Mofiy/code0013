from BinanceTrader import BinanceTrader

if __name__ == "__main__":

    f = open("binance_api.cfg", 'r')
    api_key, api_secret = f.read().split('\n')
    db_name = 'trades.db'
    trader = BinanceTrader(api_key, api_secret, db_name)

    # размещение ордера на покупку максимально доступной суммы BTCUSDT
    trader.place_order_max_amount('BTCUSDT', 'BUY')

    # размещение ордера на продажу максимально доступной суммы BTCUSDT
    trader.place_order_max_amount('BTCUSDT', 'SELL')

    # получение списка открытых позиций
    positions = trader.get_open_positions()
    print(positions)

    # # закрытие позиции для символа BTCUSDT
    trader.close_position('BTCUSDT')