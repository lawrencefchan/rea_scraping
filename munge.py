'''multiindex slicing:
df.loc[
    rows,
    columns
]

Example:
idx = pd.IndexSlice
df.loc[
    idx[level_0_slice, level_1_slice, ["C1", "C3"]],
    idx[:, "foo"]
]


'''






# %%
from pandas.io.formats.format import return_docstring
from read_db import load_data
import geopandas as gpd
import pandas as pd

import numpy as np


# df = load_data()
# df.loc[:, 'allawah']

# # %% plots (OLD, broken by new multiindex)
# df['house_price'].plot(legend=False)
# df['unit_price'].plot(legend=False)


def filter_dataset(df=None, max_missing_years=2, min_listed_count=10) -> pd.DataFrame:
    '''
    Default criteria:
    * >=10 sales per year
    * at least 7/9 years of data
    '''

    # TODO: list dropped suburbs for sanity check
    if df is None:
        df = load_data()

    # add another level to multiindex
    df.columns = pd.MultiIndex.from_tuples([(i, j, k) for i, (j, k) in zip(
        df.columns.get_level_values(0),
        df.columns.get_level_values(1).str.split('_', 1))
    ])

    # only run conditional on data reported annually
    # calculating mean on df (not df0) weights recent sales activity more highly (desirable?)
    df0 = df.loc[[d for d in df.index if d.month == 12], :]

    num_missing_years = df0.isna().sum(axis=0)
    drop_list = num_missing_years[num_missing_years > max_missing_years].index \
        # .droplevel(2)  # only want (suburb, dwelling type)
    df0 = df0.drop(drop_list, axis=1)

    avg_annual_sales = df0.loc[:, pd.IndexSlice[:, :, 'count']].mean(axis=0)
    drop_list = avg_annual_sales[avg_annual_sales < min_listed_count].index \
        .droplevel(2)
    df0 = df0.drop(drop_list, axis=1)

    return df.loc[:, df0.columns]

    ''' TODO: Return drop_list:
    * simplify list to [(suburb, dwelling type), ...]
    '''

    return df0 # , dropped_list


# get geometry for each suburb
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


# --- outlier detection / standard deviation / (WIP)
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

def z_score(df):
    return (df-df.mean())/df.std(ddof=0)

if __name__ == '__main__':
    df = filter_dataset()
    # df = df['house_price']


    # df = df[df.apply(z_score) < 3

    # df_std = df.loc[:, pd.IndexSlice[:, 'unit_price']].std(axis=0).sort_values()[:-5]
    # ax = df_std.plot.bar(legend=False, figsize=(10,5))
    # ax.set_title('House Price Variance (2012-2021)')
    # ax.get_xaxis().set_ticks([])

    # %% 
    #  check correlation between house and unit price changes

    price_data = df.loc[:, pd.IndexSlice[:, :, 'price']]

    suburbs = price_data.columns.get_level_values(0)  # suburbs with both house and unit data

    price_data = price_data[suburbs[suburbs.duplicated()]]
    price_data.columns = price_data.columns.droplevel(2)

    # price_data.corr()

    import seaborn as sns

    Var_Corr = df.corr()
    # plot the heatmap and annotation on it
    sns.heatmap(Var_Corr, xticklabels=Var_Corr.columns, yticklabels=Var_Corr.columns, annot=True)
