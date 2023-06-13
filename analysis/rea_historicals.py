'''
TODO:
- plot all suburbs, colour suburbs of interest


'''

# %%
import os
import pandas as pd

import plotly.express as px

from utils.sqlite_utils import read_historical_trends


def plot_historical_yield(df=None):
    # plots yield and 12month moving average

    if df is None:
        df = read_historical_trends('prices_volumes')

    df = df.pivot_table(
        index=['suburb', 'dwelling_type', 'yr_ended'],
        columns='ownership_type', values='median')
    df['yield'] = df['rent'] * 52 / df['buy']
    df['yield_mv_avg'] = df['yield'].rolling(window=12).mean()

    fig = px.line(
        df.drop(['buy', 'rent'], axis=1).stack().rename('value').reset_index(),
        x='yr_ended',
        y='value',
        color='suburb',
        facet_row='ownership_type',
        facet_col='dwelling_type',
    )
    fig.for_each_annotation(lambda x: x.update(text=x.text.split('=')[-1]))
    fig.show("browser")


