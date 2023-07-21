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

stocks_df = pd.DataFrame()

data_download = False

# Iterating t in the list of tickers to append single stock performance 

if data_download == True:
    for t in sp500_tickers:
        try: 
            stocks_df[t] = yf.download(t, start=start_date, progress=False)['Adj Close']
            print(stocks_df[t])
        except: pass
else: stocks_df = pd.read_excel('Prova.xlsx')

# Downloading price history of S&P500

sp500_price_history = (yf.download('^GSPC', start=start_date, progress=False)['Adj Close']).reset_index()

## PROCESSING DATA

# Converting "Date" Column into a more familiar datatype for both dataframes

stocks_df['Date'] = list(map(lambda i: dt.datetime.strptime(str(i)[0:10], "%Y-%m-%d"), stocks_df['Date']))
sp500_price_history['Date'] = list(map(lambda i: dt.datetime.strptime(str(i)[0:10], "%Y-%m-%d"), sp500_price_history['Date']))

# Counting the number of weeks that have passed since the start of the dataset, this will help us later

stocks_df['Week Number'] = list(map(lambda i: i.strftime("%U"), stocks_df['Date']))
sp500_price_history['Week Number'] = list(map(lambda i: i.strftime("%U"), sp500_price_history['Date']))

# Using a function from a library we coded ourselves to keep track of weeks that have passed

stocks_df = trading_functions.week_number_total_n(stocks_df)
sp500_price_history = trading_functions.week_number_total_n(sp500_price_history)

# Create Simple Moving Average for S&P500
# n variable represents the period for computing the moving average

periods = [12, 30, 90, 100]
moving_average_types = ['MA', 'EMA']
distinct_moving_average_setting = []

for type_moving_average in moving_average_types:
    for period_MA in periods:

        sp500_price_history = trading_functions.calculate_moving_average(sp500_price_history,type_moving_average,period_MA)

        # Filling an array with all different kind of moving averages 

        distinct_moving_average_setting += [f"{type_moving_average}_{period_MA}"]

#sp500_price_history = trading_functions.calculate_moving_average(sp500_price_history,'EMA', periods[1])

# Function to plot the S&P 500 graph

def plot_sp500_graph(sp500_price_history, ema_name):

    plt.figure(figsize=(20, 10))
    plt.plot(sp500_price_history['Date'],sp500_price_history[ema_name], color="Blue", label="Moving Average")
    plt.plot(sp500_price_history['Date'],sp500_price_history['Adj Close'], color='Red', label="S&P500")
    plt.show()

# We are recalling a function from our personal libary to determinate if the actual momentum of S&P500 is currently long
# It will check for each data point if the actual price is long 

sp500_price_history = trading_functions.determinate_momentum(sp500_price_history, "MA_30")

# It will give an error while checking the data with moving averages with different periods:
# MA with 90 days period will require more days to compute than a 30 days period moving average 

sp500_price_history = sp500_price_history[sp500_price_history['Momentum'] != "Error"]
sp500_price_history = sp500_price_history.reset_index(drop=True)

## CREATING BACKTEST ENVIRONMENT

# Defining variables to perform the strategy

weights_if_long = [0.80,0.20]
weights_if_short = [0.20,0.80]
n_assets = 2

def backtest(sp500_price_history, stocks_df, weights_if_long, weights_if_short, n_assets):

    for i in range(max(sp500_price_history['Week Number'])):

        # Gathering the data we need from all dataframes

        temporary_data_sp500 = sp500_price_history[sp500_price_history['Week Number'] == i].reset_index(drop=True)

        # For each week, gathering data of top performer and worst performer

        if len(temporary_data_sp500) == 4 or len(temporary_data_sp500) == 5:

            week = temporary_data_sp500['Week Number'][0]
            stocks_df_n_week = stocks_df[stocks_df['Week Number'] == week-1].reset_index(drop=True)
            loc_1,loc_2 = stocks_df_n_week.iloc[0],stocks_df_n_week.iloc[len(stocks_df_n_week)-1]
            stocks_df_n_week = pd.concat([loc_1,loc_2], axis=1).transpose().reset_index(drop=True)
            stocks_df_n_week_pct_change = stocks_df_n_week.drop(['Date', 'Week Number'], axis=1).pct_change().drop(0,axis=0).reset_index(drop=True)
            stocks_df_n_week_pct_change = stocks_df_n_week_pct_change.transpose().rename(columns={0:"Performance"}).sort_values("Performance", ascending=False)

            top_performer = stocks_df_n_week_pct_change.head(n_assets).reset_index()
            worst_performer = stocks_df_n_week_pct_change.tail(n_assets).reset_index()

            print(top_performer)
            print(worst_performer)

        else: print("Data for this trading week is incomplete, skipping to the next week...")

backtest(sp500_price_history, stocks_df, weights_if_long, weights_if_short, n_assets)