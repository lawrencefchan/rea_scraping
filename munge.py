# %%
from read_db import load_data, filter_dataset
import geopandas as gpd
import pandas as pd

import numpy as np

# df = load_data()
# df0 = filter_dataset(df)
# df.loc[:, 'allawah']

# # %% plots (OLD, broken by new multiindex)
# df['house_price'].plot(legend=False)
# df['unit_price'].plot(legend=False)

# # %% outlier detection (OLD, broken by new multiindex)
# df0 = df['house_price']

# def z_score(df):
#     return (df-df.mean())/df.std(ddof=0)

# df0 = df0[df0.apply(z_score) < 3]

# %% get geometry for each suburb


def get_suburb_geom(df) -> pd.DataFrame:
    '''
    df from read_db.load_data()

    TODO:
    * do something about suburbs appearing multiple times
    '''
    suburb_list = df.columns.get_level_values(0)

    # https://data.gov.au/dataset/ds-dga-91e70237-d9d1-4719-a82f-e71b811154c6/details
    df_geom = gpd.read_file("./test_data/NSW_LOC_POLYGON_shp/NSW_LOC_POLYGON_shp.shp")
    # df_geom = pd.concat([df_geom['NSW_LOCA_2'].apply(str.title),
    #                     df_geom['geometry']], axis=1)
    df_geom = df_geom[['NSW_LOCA_2', 'geometry']]
    df_geom['NSW_LOCA_2'] = df_geom['NSW_LOCA_2'].apply(str.title)
    df_geom.columns = ['Suburb', 'geometry']

    burbs = pd.read_csv('suburb_postcodes.csv')

    burbs = df_geom.merge(burbs,
                        how='right',
                        on='Suburb')

    # set index to slice by index
    burbs['Suburb'] = burbs['Suburb'].apply(lambda x: x.replace('-', ' '))
    burbs = burbs.set_index('Suburb')
    burbs = burbs.loc[[i.title() for i in suburb_list.unique()], :]

    return burbs.reset_index()


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

