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

        all_ma_sp500_price_history = trading_functions.calculate_moving_average(sp500_price_history,type_moving_average,period_MA)

        # Filling an array with all different kind of moving averages 

        distinct_moving_average_setting += [f"{type_moving_average}_{period_MA}"]

# Function to plot the S&P 500 graph

def plot_sp500_graph(all_ma_sp500_price_history, ema_name):

    plt.figure(figsize=(20, 10))
    plt.plot(all_ma_sp500_price_history['Date'],all_ma_sp500_price_history[ema_name], color="Blue", label="Moving Average")
    plt.plot(all_ma_sp500_price_history['Date'],all_ma_sp500_price_history['Adj Close'], color='Red', label="S&P500")
    plt.show()


## CREATING BACKTESTING ENVIRONMENT

# Defining variables to perform the strategy

possible_allocation_combinations_long = list(zip([round((i*0.10),2) for i in range(1,10)],[round((1 - i*0.10),2) for i in range(1,10)]))
possible_allocation_combinations_short = list(zip([round((i*0.10),2) for i in range(10,1,-1)],[round((1 - i*0.10),2) for i in range(10,1,-1)]))

strategy_returns = []
settings = []

# This for loop will iterate all strategy dinamic variables: 
# allocation combinations for long and short, all moving averages and number of assets to long and short

for i in range(len(possible_allocation_combinations_long)):

    ma = 'MA_30'

    # We are defining a dinamic name for the current strategy we are backtesting,
    # otherwise we won't be able to keep track of what parameters are being tested.
        
    test_settings = f"{ma} {str(possible_allocation_combinations_long[i])} {str(possible_allocation_combinations_short[i])} {str(1)}"
    settings.append(test_settings)
    
    print("Performing test for: ", test_settings)
    
    # We are recalling a function from our personal libary to determinate if the actual momentum of S&P500 is currently long
    # It will check for each data point if the actual price is long 
    
    sp500_price_history = trading_functions.determinate_momentum(all_ma_sp500_price_history, ma)
    
    # It will give an error while checking the data with moving averages with different periods:
    # for example MA with 90 days period will require more days to compute than a 30 days period moving average 
    
    sp500_price_history = sp500_price_history[sp500_price_history['Momentum'] != "Error"]
    sp500_price_history = sp500_price_history.reset_index(drop=True)
                
    results = trading_functions.backtest_strategy(sp500_price_history, stocks_df, possible_allocation_combinations_long[i], possible_allocation_combinations_short[i], 1)
    
    strategy_returns.append(results)     
    print("Strategy Backtested")

df = pd.DataFrame(list(zip(settings,strategy_returns)), columns=['Strategy', 'Strategy Returns'])

strategies = []
trading_weeks = []
strategies_balances = []

for i in range(len(df)):

    strategies.append(df['Strategy'][i])
    balance = 100
    balance_history = []
    trading_weeks_n = []

    for k in range(len(df['Strategy Returns'][i])):
        strategy_n_return = df['Strategy Returns'][i]
        trading_weeks_n.append(strategy_n_return['Week'][k])
        balance = balance + (balance * strategy_n_return['Return'][k])
        balance_history.append(balance)
    
    strategies_balances.append(balance_history)
    trading_weeks.append(trading_weeks_n)

final_df = pd.DataFrame(list(zip(strategies,trading_weeks,strategies_balances)), columns=['Strategy', 'Trading Weeks','Strategy Balance'])  