import pandas as pd
import numpy as np
from datetime import datetime
import pytz


tick_size_dict = {
    "EUR_JPY": 0.001,
    "AUD_JPY": 0.001,
    "CAD_JPY": 0.001,
    "CHF_JPY": 0.001,
    "GBP_JPY": 0.001,
    "USD_JPY": 0.001,
    "NZD_JPY": 0.001
}


# Time Zone
timezone_instrument = pytz.timezone("America/New_York")
server_timezone = pytz.timezone("America/Bogota")
utc_timezone = pytz.timezone('UTC')

# Read trades
df_trades = pd.read_csv("input/trades.csv", sep=";")
df_trades['Date Entry'] = pd.to_datetime(df_trades['Date Entry'])
df_trades['Date Exit'] = pd.to_datetime(df_trades['Date Exit'])

ranges = pd.date_range(start="2017/12/10", end="2020/1/1", freq="T").tz_localize(tz='UTC')

df_balance = pd.DataFrame({"date": ranges})
df_balance = df_balance.set_index("date")

print(df_trades.dtypes)

for index, trade in df_trades.iterrows():
    symbol = trade['Symbol']
    side = trade['Side']
    price_entry = trade['Price Entry']
    price_stop = trade['Stoploss']
    tick_size = tick_size_dict.get(symbol, 0.00001)

    stoploss_pips = abs(price_entry - price_stop) / tick_size / 10
    pip_value = trade['Risk[USD]'] / stoploss_pips

    #print(trade['Date Entry'].tz_localize(tz=server_timezone), price_entry)
    print("Entry: ", trade['Date Entry'], " ** Price Exit: ", trade['Date Exit'])

    #from_date = server_timezone.localize(datetime.strptime(trade['Date Entry'], "%d/%m/%Y %H:%M"))
    #to_date = server_timezone.localize(datetime.strptime(trade['Date Exit'], "%d/%m/%Y %H:%M"))
    from_date = trade['Date Entry'].tz_localize(tz=server_timezone)
    to_date = trade['Date Exit'].tz_localize(tz=server_timezone)
    #price_entry = trade['']

    year = from_date.year

    if year == 2017:
        year = 2018

    # Open file with candlestick data
    df_instrument = pd.read_csv("ohlc_data/{}/{}.csv".format(year, symbol), sep=";")
    df_instrument['date'] = pd.to_datetime(df_instrument['date'])
    df_instrument = df_instrument.set_index('date')

    df_instrument.index = df_instrument.index.tz_localize(None).tz_localize(tz='UTC')

    mask = (df_instrument.index > from_date) & (df_instrument.index <= to_date)

    df_candles = df_instrument.loc[mask]
    #df_candles = df_candles.set_index('date')

    df_bal = df_balance.loc[mask]

    df_balance[index] = np.nan

    last_close = price_entry

    for i, c in df_bal.iterrows():
        if i in df_candles.index:
            last_close = df_candles.loc[i, 'close']

        if side == 'Long':
            gain = (last_close - price_entry) / tick_size / 10 * pip_value
        elif side == 'Short':
            gain = (price_entry - last_close) / tick_size / 10 * pip_value

        print(gain, last_close, price_entry, tick_size, pip_value)

        df_balance.loc[i, index] = gain

    df_balance[index] = df_balance[index].ffill()

    df_balance.to_csv("output/backtesting.csv")

    print(df_balance.tail(10))

    break












