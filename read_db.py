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
* r^2 against linear fit (another measure of variance?)
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


def filter_dataset(df=None, max_missing_years=2, min_listed_count=10):
    '''
    Criteria:
    * >=10 sales per year
    * at least 7/9 years of data

    TODO: list filtered suburbs
    '''
    if df is None:
        df = load_data()

    # --- count missing years of data
    # max_missing_years = 2
    df0 = df.loc[[d for d in df.index if d.month == 12], :].isna().sum(axis=0)
    drop_index = df0[df0 > max_missing_years].index

    # ax = df0.plot.bar(legend=False)
    # ax.get_xaxis().set_ticks([])

    # # Q: do _price and _count have the same number of nans? (A: yes)
    # df0 = df0.unstack()
    # df0[~(df0.max(axis=1) == df0.min(axis=1))]

    # --- count mean number of sales per year
    # min_listed_count = 10
    # df0 = df.loc[:, pd.IndexSlice[:, 'house_count']].mean()
    # drop_index = drop_index.append(df0[df0 < min_listed_count].index)

    df0 = df.drop(drop_index, axis=1)

    '''
    Check dropped data:
    * x_price and x_count are both dropped (result of having the same number of nans)
    * simplify list to [(suburb, dwelling type), ...]
    '''

    assert len(drop_index) % 2 ==0

    dropped_list = []
    for i in range(int(len(drop_index)/2)):
        dwelling = drop_index[2*i][1].split('_')[0]
        
        if dwelling == drop_index[2*i+1][1].split('_')[0]:
            dropped_list += [(drop_index[2*i][0], dwelling)]

    return df0 # , dropped_list

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

df = load_data()
df0 = filter_dataset(df)




# df.loc[:, 'allawah']
# df.head()

# # %% plots (OLD, broken by new multiindex)
# df['house_price'].plot(legend=False)
# df['unit_price'].plot(legend=False)

# # %% outlier detection (OLD, broken by new multiindex)
# df0 = df['house_price']

# def z_score(df):
#     return (df-df.mean())/df.std(ddof=0)

# df0 = df0[df0.apply(z_score) < 3]



# %% standard deviation (WIP)

# df_std = df.loc[:, pd.IndexSlice[:, 'unit_price']].std(axis=0).sort_values()[:-5]
# ax = df_std.plot.bar(legend=False, figsize=(10,5))
# ax.set_title('House Price Variance (2012-2021)')
# ax.get_xaxis().set_ticks([])

def detect_outliers(df):
    '''
    Remove price outliers >3 standard deviations
    * checks suburb and dwelling type

    NOTE: wiki says "Deletion of outlier data is a controversial practice frowned upon"

    TODO:
    * check what degrees of freedom is for std
    '''
    nparray = df.loc[:, pd.IndexSlice[:, 'unit_price']].values
    nparray = nparray[~np.isnan(nparray)]

    return nparray.std(ddof=1), np.mean(nparray)

detect_outliers(df)

# %%
fig, axes = plt.subplots(nrows=2)

parra = df['parramatta']

parra.columns = pd.MultiIndex.from_product(
    [['house', 'unit'], ['count', 'price']],
    names=['dwelling', 'meas'])


sm = plt.cm.ScalarMappable(cmap='viridis', 
                           norm=plt.Normalize(vmin=parra.index.min().year,
                                              vmax=parra.index.max().year))
parra['house'].plot.scatter('count', 'price', c=parra.index, cmap='viridis', ax=axes[0])
parra['unit'].plot.scatter('count', 'price', c=parra.index, cmap='viridis', ax=axes[1])
fig.colorbar(sm, ax=axes.ravel().tolist())
axes[0].ticklabel_format(style='plain')
axes[1].yaxis.set_major_locator(plt.MultipleLocator(50000))

plt.show()

# %%
ax = df0.loc[:, pd.IndexSlice[:, 'unit_price']].plot(legend=False)
# ax.get_xaxis().set_ticks([])


# %% growth to date

df.loc[:, pd.IndexSlice[:, 'house_price']].plot(legend=False)

# df0 = df['house_price'].std(axis=0).sort_values()[-10:-1]
# df0.plot.bar(legend=False)

# df['house_price']['st leonards']
# df['house_count'][df0.index]

# df0.loc[:, pd.IndexSlice[:, 'house_count']].plot(legend=False)
