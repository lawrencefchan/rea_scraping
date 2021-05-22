'''
Columns: 
    'date',
    'suburb',
    'house_price',
    'house_count',
    'unit_price',
    'unit_count'

NOTE:
* data is given for the 12months prior to the indexed date 


Observations:
* suburbs with missing data had the samne amount of missing data for both _count and _price


EDA - points of interest
* areas of highest growth (range of years)
* areas of lowest growth (range of years)
* areas of highest yield 
* measures of variance: z-score, r^2 against linear fit
* discard series with low count values and lots mising data 


Hypotheses:
* low variance implies stable pricing, possibly low growth
* house and unit prices should be complementary (both in terms of variance and growth). 
    Deviation from this implies data skewed by outliers (e.g. enormous, 1-off land purchases)

'''

# %%
import sqlite3
import pandas as pd
import time

import numpy as np
from scipy import stats

import matplotlib.pyplot as plt

def load_data():
    # NOTE: load_data() should point to ./data/historicalprices.db
    
    t0 = time.time()

    con = sqlite3.connect('historicalprices.db')
    df = pd.read_sql_query("SELECT * FROM prices_counts", con)

    con.close()

    df['date'] = pd.to_datetime(df['date'])

    print(time.time() - t0)

    t0 = time.time()
    df = df.pivot_table(values=['house_price', 'house_count','unit_price','unit_count'],
                        index='date',
                        columns='suburb') \
        .astype(int, errors='ignore')

    df = df.swaplevel(axis=1) \
        .sort_index(axis=1, level=0)

    print(time.time() - t0)

    return df


def query_test():
    con = sqlite3.connect('historicalprices.db')
    cur = con.cursor()

    # --- show column names
    # cur.execute('PRAGMA table_info(prices_counts);')
    # print('column list:', [i[1] for i in cur.fetchall()])

    # --- delete table
    # cur.execute('DROP TABLE prices_counts')

    # --- print data
    # for row in cur.execute('SELECT * FROM prices_counts ORDER BY date'):
    #     print(row)
    #     break

    # --- extract and plot data for a single suburb
    df = pd.read_sql_query("""SELECT date, unit_price
                              FROM prices_counts
                              WHERE suburb='lavender bay'""", con)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', drop=True).plot(marker='.')

    con.close()
