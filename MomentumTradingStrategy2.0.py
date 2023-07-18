# Libraries

import pandas as pd
import numpy
import wikipedia as wp
import yfinance as yf
import matplotlib.pyplot as plt
import datetime as dt
from datetime import timedelta
import week_Number 

# Downloading tickers from Wikipedia

# Accessing wikipedia web page

html = wp.page("List_of_S%26P_500_companies").html().encode("UTF-8")

# Gathering data from the wikipedia page

sp500_tickers = (pd.read_html(html)[0])['Symbol'].drop_duplicates()

# Selecting date to start gathering data

start_date = "2021-01-01"

# Creating an empty dataframe to fill with data of each ticker

df = pd.DataFrame()

data_download = False

# Iterating t in the list of tickers to append single stock performance 

if data_download == True:
    for t in sp500_tickers:
        try: 
            df[t] = yf.download(t, start=start_date, progress=False)['Adj Close']
            print(df[t])
        except: pass
else: df = pd.read_excel('Prova.xlsx')

# Downloading price history of S&P500

sp500_price_history = (yf.download('^GSPC', start=start_date, progress=False)['Adj Close']).reset_index()

# Converting "Date" Column into a more familiar datatype for both dataframes

df['Date'] = list(map(lambda i: dt.datetime.strptime(str(i)[0:10], "%Y-%m-%d"), df['Date']))
sp500_price_history['Date'] = list(map(lambda i: dt.datetime.strptime(str(i)[0:10], "%Y-%m-%d"), sp500_price_history['Date']))

# Counting the number of weeks that have passed since the start of the dataset will help us later

df['Week Number'] = list(map(lambda i: i.strftime("%U"), df['Date']))
sp500_price_history['Week Number'] = list(map(lambda i: i.strftime("%U"), sp500_price_history['Date']))

#il numero settimana è solo dell'anno, deve essere dalla partenza dello script 

df = week_Number.week_number_total_n(df)

print(df)