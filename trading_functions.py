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