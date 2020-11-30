import numpy as np
import requests
import pytz
from datetime import datetime, timedelta
import time
import pandas as pd

# Oanda API Configuration
access_token = 'e1983f1ae981140c9a29ba3928c65b4d-3ab3bed1919b2920adc330b7fca32d7d'
account_id = '101-011-13259108-001'

end_point = "/v3/accounts/{account_id}/instruments/{symbol}/candles"
url = 'https://api-fxpractice.oanda.com' + end_point

headers = {'Authorization': 'Bearer ' + access_token}

# Time Zone
timezone_instrument = pytz.timezone("America/New_York")
server_timezone = pytz.timezone("America/Bogota")
utc_timezone = pytz.timezone('UTC')

# Read Trades CSV
df_instruments = pd.read_csv("input/symbols.csv", sep=";")

year = int(input("Ingresar año: "))

for index, row in df_instruments.iterrows():
    symbol = row['Symbol']
    resolution = 'M1'

    if year == 2018:
        from_date = server_timezone.localize(datetime(2017, 12, 10))
    else:
        from_date = server_timezone.localize(datetime(year, 1, 1))

    to_date = server_timezone.localize(datetime(year, 12, 31))

    current_date = from_date

    ohlc_file = open("ohlc_data/{}/{}.csv".format(year, symbol), 'w')
    ohlc_file.write("date;open;high;low;close;volume\n")

    while current_date < to_date:
        future_date = current_date + timedelta(days=3)
        print("{} ******* Symbol: {} ***** From: {} **** To: {}".format(index, symbol, current_date, future_date))
        
        if future_date > to_date:
            future_date = to_date

        from_with_timezone = int(current_date.timestamp())
        to_with_timezone = int(future_date.timestamp())

        params = {'price': 'M', 'granularity': resolution, 'from': from_with_timezone, 'to': to_with_timezone}

        response = requests.get(url.format(account_id=account_id, symbol=symbol), headers=headers, params=params)

        json_response = response.json()

        if response.status_code == 200:
            for elem in json_response['candles']:
                candle = elem['mid']

                ohlc_file.write("{};{};{};{};{}\n".format(elem['time'], candle['o'], candle['h'], candle['l'], candle['c'], elem['volume']))
        else:
            print(response.status_code)

        current_date = current_date + timedelta(days=3)
