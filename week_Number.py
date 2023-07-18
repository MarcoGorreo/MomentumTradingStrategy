import pandas as pd
from datetime import timedelta
import datetime

def week_number_total_n(df):
    df['Week Number'] = df['Week Number'].apply(int)
    df['year'] = list(map(lambda i: (i.year-2021)*52, df['Date']))
    df['Week Number'] = df['Week Number'] + df['year']
    df = df.drop(columns='year',axis=1)
    
    return df