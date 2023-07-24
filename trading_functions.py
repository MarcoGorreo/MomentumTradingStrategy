import pandas as pd
from datetime import timedelta
import datetime

def week_number_total_n(df):

    df['Week Number'] = df['Week Number'].apply(int)

    df['year'] = list(map(lambda i: (i.year-2021)*52, df['Date']))
    
    df['Week Number'] = df['Week Number'] + df['year']
    df['Week Number'] = df['Week Number'].apply(int)

    df = df.drop(columns='year',axis=1)
    
    return df

def calculate_moving_average(df,moving_average_type,period):

    # Creating an empty array to store moving average data
    
    moving_average_array = []
    
    name = moving_average_type + "_" + str(period)

    # Calculating moving average 

    if moving_average_type == 'MA':

        # Calculating simple moving average 
    
        for i in range(len(df)):
        
            if i >= period:
                moving_average = df['Adj Close'][i-period:i].sum() / period
                moving_average_array.append(moving_average)

            # It's impossible to compute moving average 
            # with period n for a number of observation inferior to n, 
            # so we are skipping the first n days

            else: moving_average_array.append(None)

    elif moving_average_type == 'EMA':

        # Calculating exponential moving average 

            # a represents smoothing factor, used to compute EMA. 

            a = 0.75

            # ema_shifted represents ema calculated the day before
                
            ema_shifted = 0

            for i in range(len(df)):
                
                if i == period:
                    moving_average = df['Adj Close'][i-period:i].sum() / period
                    moving_average_array.append(moving_average)
                    ema_shifted = moving_average

                elif i > period:
                    CN = df['Adj Close'][i-1]
                    ema = ((a * CN) + (1 - a) * ema_shifted)
                    moving_average_array.append(ema)
                    ema_shifted = ema

            # It's impossible to compute moving average 
            # with period n for a number of observation inferior to n, 
            # so we are skipping the first n days

                else: moving_average_array.append(None)

    # Adding moving average to our S&P 500 dataframe

    df[name] = moving_average_array

    return df

def determinate_momentum(sp_500_data, ema):

    momentum = []

    for i in range(len(sp_500_data)):
        if sp_500_data['Adj Close'][i] >= sp_500_data[ema][i]:
            momentum.append("Long")
        elif sp_500_data['Adj Close'][i] <= sp_500_data[ema][i]:
            momentum.append("Short")
        else: momentum.append('Error')

    sp_500_data['Momentum'] = momentum
    
    sp_500_data = sp_500_data[["Date", "Adj Close", ema,"Momentum", "Week Number"]]

    return sp_500_data


def create_portfolio(top_performer, worst_performer, weights, n_assets):

    stocks, operations, positions_weights = [], [], []

    for k in range(len(top_performer)):

        stocks.append(top_performer['index'][k])
        operations.append('Long')
        positions_weights.append(weights[0] / n_assets)

    for k in range(len(worst_performer)):

        stocks.append(worst_performer['index'][k])
        operations.append("Short")
        positions_weights.append(weights[1] / n_assets)

    positions = pd.DataFrame(list(zip(stocks,operations,positions_weights)), columns=['Stock', 'Position Type', 'Position Weight'])

    return positions

def backtest_strategy(sp500_price_history, stocks_df, weights_if_long, weights_if_short, n_assets):

    strategy_returns = []
    weeks = []

    for i in range(max(sp500_price_history['Week Number'])):

        # Gathering the data we need from all dataframes

        temporary_data_sp500 = sp500_price_history[sp500_price_history['Week Number'] == i].reset_index(drop=True)

        # For each week, gathering data of top performer and worst performer

        if len(temporary_data_sp500) == 4 or len(temporary_data_sp500) == 5:

            week = temporary_data_sp500['Week Number'][0]
            weeks.append(week)

            # This is the price history data for the stocks during the previous week, we will use this data to determinate our positions

            stocks_df_n_week = stocks_df[stocks_df['Week Number'] == week-1].reset_index(drop=True)
            
            # This is the price history data for the stocks during the current trading week, we will use this data to calculate result of our strategy

            stocks_df_n_plus1_week = stocks_df[stocks_df['Week Number'] == week].reset_index(drop=True)

            # Selecting from the data only the first and last day of the week for each stock

            loc_1,loc_2 = stocks_df_n_week.iloc[0],stocks_df_n_week.iloc[len(stocks_df_n_week)-1]
            stocks_df_n_week_first_and_last_day = pd.concat([loc_1,loc_2], axis=1).transpose().reset_index(drop=True)

            # Doing the same once again but for the current week stock data

            loc_1,loc_2 = stocks_df_n_plus1_week.iloc[0],stocks_df_n_plus1_week.iloc[len(stocks_df_n_plus1_week)-1]
            stocks_df_current_week_first_and_last_day = pd.concat([loc_1,loc_2], axis=1).transpose().reset_index(drop=True)
            stocks_df_current_week_pct_change = stocks_df_current_week_first_and_last_day.drop(['Date', 'Week Number'], axis=1).pct_change().drop(0,axis=0).reset_index(drop=True)
            stocks_df_current_week_pct_change = stocks_df_current_week_pct_change.transpose().rename(columns={0:"Performance"}).reset_index(drop=False).rename(columns={'index':'Stock'})

            # Calculating the percentage change between the first and last day of the week 

            stocks_df_n_week_pct_change = stocks_df_n_week_first_and_last_day.drop(['Date', 'Week Number'], axis=1).pct_change().drop(0,axis=0).reset_index(drop=True)

            # Rearraging the data and sorting it to get the best and worst performing stocks

            stocks_df_n_week_pct_change = stocks_df_n_week_pct_change.transpose().rename(columns={0:"Performance"}).sort_values("Performance", ascending=False)

            top_performer = stocks_df_n_week_pct_change.head(n_assets).reset_index()
            worst_performer = stocks_df_n_week_pct_change.tail(n_assets).reset_index()

            momentum = temporary_data_sp500['Momentum'][0]

            # Basing on S&P500 momentum, we are creating a portfolio of stocks with the weights we already decided

            if momentum == "Long":

                portfolio = create_portfolio(top_performer, worst_performer, weights_if_long, n_assets)

            elif momentum == "Short":

                portfolio = create_portfolio(top_performer, worst_performer, weights_if_short, n_assets)

            else: print("Error: cannot determinate momentum")

            # Filtering the entire stocks dataframe for the current week with only the stocks we currently hold in un portfolio
        
            stocks_df_current_week_pct_change = stocks_df_current_week_pct_change[stocks_df_current_week_pct_change['Stock'].isin(portfolio['Stock'])].reset_index(drop=True)

            # Merging our operations' performance to our portfolio dataframe

            portfolio = portfolio.merge(stocks_df_current_week_pct_change, on="Stock")

            # Calculating returns for each position

            returns = []

            for k in range(len(portfolio)):
                if portfolio['Position Type'][k] == "Long":
                    returns.append(portfolio['Position Weight'][k] * portfolio['Performance'][k])
                if portfolio['Position Type'][k] == "Short":
                    returns.append(portfolio['Position Weight'][k] * portfolio['Performance'][k] * -1)

            portfolio['P/L %'] = returns

            # With the sum of the P/L % column we obtain the current week P/L %

            strategy_returns.append(portfolio['P/L %'].sum()) 

    return pd.DataFrame(list(zip(weeks,strategy_returns)), columns=['Week', 'Return'])