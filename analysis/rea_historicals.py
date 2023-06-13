'''
TODO:
- plot all suburbs, colour suburbs of interest


'''

# %%
import os
import pandas as pd

import plotly.express as px

from utils.sqlite_utils import read_historical_trends
from utils.plot_utils import plotly_geoplot
from utils.general_utils import get_suburb_geom


def plot_historical_yield(df=None):
    # plots yield and 12month moving average

    if df is None:
        df = read_historical_trends('prices_volumes')

    df = df.pivot_table(
        index=['suburb', 'dwelling_type', 'yr_ended'],
        columns='ownership_type', values='median')
    df['yield'] = df['rent'] * 52 / df['buy']
    df['yield_mv_avg'] = df['yield'].rolling(window=12).mean()
    df = df.drop(['buy', 'rent'], axis=1).stack().rename('value') \
        .reset_index()

    fig = px.line(
        df,
        x='yr_ended',
        y='value',
        color='suburb',
        facet_row='ownership_type',
        facet_col='dwelling_type',
    )
    fig.for_each_annotation(lambda x: x.update(text=x.text.split('=')[-1]))
    fig.show("browser")

# --- spatial plot median
try:
    suburb_geom
except NameError:
    suburb_geom = get_suburb_geom().drop(['Postcode', 'Region'], axis=1)
    suburb_geom.columns = [_.lower() for _ in suburb_geom.columns]
    suburb_geom['suburb'] = suburb_geom['suburb'].str.lower() \
        .str.replace(' ', '-')

df = read_historical_trends('prices_volumes')
df['yr_ended'] = pd.to_datetime(df['yr_ended'])

df = df[(df['ownership_type'] == 'buy') &
        (df['n_beds'] == 0) &
        (df['dwelling_type'] == 'house')]
# get latest available data
group_cols = ['suburb', 'dwelling_type', 'n_beds']
df = df.loc[df.groupby(group_cols)['yr_ended'].idxmax()]
drop_cols = [
    'volume',
    'yr_ended',
    'ownership_type',
    'dwelling_type',
    'n_beds',
    'last_queried']
df = suburb_geom.merge(
    df.drop(drop_cols, axis=1),
    how='inner', on='suburb') \
    .set_index('suburb')
# %%
# plotly_geoplot(df.drop(['vaucluse', 'bellevue-hill', 'longueville']), plot_col='median')

# %%

df.reset_index().sort_values('median').plot.bar(x='suburb', y='median')

px.plot()