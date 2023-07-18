## LIBRARIES

# The library trading_functions is our own coded library which stores useful functions
# to perform calculations in this backtest environment, we will use it later on.

import pandas as pd
import numpy
import wikipedia as wp
import yfinance as yf
import matplotlib.pyplot as plt
import datetime as dt
import trading_functions
from datetime import timedelta

## GATHERING DATA

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

## PROCESSING DATA

# Converting "Date" Column into a more familiar datatype for both dataframes

df['Date'] = list(map(lambda i: dt.datetime.strptime(str(i)[0:10], "%Y-%m-%d"), df['Date']))
sp500_price_history['Date'] = list(map(lambda i: dt.datetime.strptime(str(i)[0:10], "%Y-%m-%d"), sp500_price_history['Date']))

# Counting the number of weeks that have passed since the start of the dataset will help us later

df['Week Number'] = list(map(lambda i: i.strftime("%U"), df['Date']))
sp500_price_history['Week Number'] = list(map(lambda i: i.strftime("%U"), sp500_price_history['Date']))

# Using a library we coded ourselves to keep track of weeks that have passed

df = trading_functions.week_number_total_n(df)
sp500_price_history = trading_functions.week_number_total_n(sp500_price_history)

# Create Simple Moving Average for S&P500

# n variable represents the period for computing the moving average

periods = [12, 30, 90, 100]
moving_average_types = ['MA', 'EMA']

for type_moving_average in moving_average_types:
    for period_MA in periods:
        sp500_price_history = trading_functions.calculate_moving_average(sp500_price_history,type_moving_average,period_MA)

print(sp500_price_history.tail(3))

#sp500_price_history = trading_functions.calculate_moving_average(sp500_price_history,'EMA', periods[1])

# Function to plot the S&P 500 graph

def plot_sp500_graph(sp500_price_history, ema_name):

    plt.figure(figsize=(20, 10))
    plt.plot(sp500_price_history['Date'],sp500_price_history[ema_name], color="Blue", label="Moving Average")
    plt.plot(sp500_price_history['Date'],sp500_price_history['Adj Close'], color='Red', label="S&P500")
    plt.show()