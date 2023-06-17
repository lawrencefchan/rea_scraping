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
# from scipy import stats

import matplotlib.pyplot as plt

def load_data():
    # NOTE: load_data() should point to ./data/historicalprices.db
    
    t0 = time.time()

    con = sqlite3.connect('./data/historicalprices.db')
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

load_data()
# %%


def query_test():
    con = sqlite3.connect('./data/historicalprices.db')
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

# df = load_data()
# df0 = filter_dataset(df)


def get_suburb_url(suburb):
    suburb = suburb.title()

    url_base = r'https://www.realestate.com.au/neighbourhoods/'
    # https://www.realestate.com.au/neighbourhoods/north-epping-2121-nsw

    postcodes = pd.read_csv('postcodes-suburbs-regions.csv').query('Suburb == @suburb')

    display(postcodes)

    p = postcodes.iloc[0, 0]
    s = postcodes.iloc[0, 1]

    url = f'{url_base}{s.lower().replace(" ", "-")}-{p}-nsw'

    return url


# get_suburb_url('north epping')

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

# detect_outliers(df)

# %%
# fig, axes = plt.subplots(ncols=2)

# parra = df['parramatta']

# parra.columns = pd.MultiIndex.from_product(
#     [['house', 'unit'], ['count', 'price']],
#     names=['dwelling', 'meas'])


# sm = plt.cm.ScalarMappable(cmap='viridis', 
#                            norm=plt.Normalize(vmin=parra.index.min().year,
#                                               vmax=parra.index.max().year))
# ax = parra['house'].plot.scatter('count', 'price', c=parra.index, cmap='viridis')
# cbar = plt.colorbar(sm)

# parra['unit'].plot.scatter('count', 'price', c=parra.index, cmap='viridis')

# plt.show()

# %%
# ax = df0.loc[:, pd.IndexSlice[:, 'unit_price']].plot(legend=False)
# ax.get_xaxis().set_ticks([])


# %% growth to date

# df.loc[:, pd.IndexSlice[:, 'house_price']].plot(legend=False)

# df0 = df['house_price'].std(axis=0).sort_values()[-10:-1]
# df0.plot.bar(legend=False)

# df['house_price']['st leonards']
# df['house_count'][df0.index]

# df0.loc[:, pd.IndexSlice[:, 'house_count']].plot(legend=False)

# %% growth in past year


def plot_historical_growth():
    drop_cols = ['millers point', 'kemps creek']

    df0 = df.loc[[df.index[-1], df.index[8]], pd.IndexSlice[:, 'house_price']] # growth in past year
    # df0 = df.loc[[df.index[-1], df.index[-2]], pd.IndexSlice[:, 'house_price']] # growth in past month
    df0.columns = df0.columns.get_level_values(0)
    df0 = (df0.iloc[0, :]/df0.iloc[1, :] - 1) \
        .dropna().sort_values().drop(drop_cols)
    df0 = df0[df0 != 0]

    # --- plot
    ax = df0.plot.barh(legend=False, figsize=(7, 90))
    # ax.get_xaxis().set_ticks([])
    # ax.set_title('Suburbs with positive growth (Feb/2021 - Mar/2021)')
    ax.set_title('Suburb % growth (Mar/2020 - Mar/2021)')
    ax.set_xticklabels(['{:,.2%}'.format(x) for x in ax.get_xticks()])

    # for bar in ax.patches:
    #     bar.set_facecolor('#888888')
    highlight = 'kurrajong'
    pos = df0.index.get_loc(highlight)

    ax.get_yticklabels()[pos].set_color("red")
    ax.get_yticklabels()[pos].set_weight("bold")
    ax.patches[pos].set_facecolor('#aa3333')

    plt.show()




# plot_historical_growth()



'''

TODO:
* geographic plotting
https://towardsdatascience.com/how-to-create-maps-in-plotly-with-non-us-locations-ca974c3bc997
https://github.com/KerryHalupka/plotly_choropleth
https://www.earthdatascience.org/courses/scientists-guide-to-plotting-data-in-python/plot-spatial-data/customize-raster-plots/interactive-maps/

* scatter plot - last month % delta vs last year % delta

'''
