# %%
import os
import pandas as pd
import plotly.express as px

from utils.sqlite_utils import read_historical_trends


df = read_historical_trends('prices_volumes')
df.head()


# %%


def plot_historical_yield(df=None):
    '''
    Plots rental yield over time, where yield assumes income over 50 weeks.
    Suburbs are coloured in order of historical average price.

    Parameters:
    -----------
    df:
        Uses `read_historical_trends('prices_volumes')`
    
    TODO:
    *   consider treatment of low volume datapoints
    *   color by average suburb growth?
    * 
    '''

    if df is None:
        df = read_historical_trends('prices_volumes')

    d = df.pivot_table(index=['suburb', 'dwelling_type', 'n_beds', 'yr_ended'],
                columns='ownership_type',
                values='median')
    d['yield'] = d['rent'] * 50 / d['buy']  # assumes income over 50 weeks
    # d['yield_mv_avg'] = d['yield'].rolling(window=12).mean()

    historical_means = d.groupby(level='suburb')['buy'].mean()

    # TODO: drop NA cols
    # d[historical_means.isna()]
    # idx = pd.IndexSlice
    # d.loc[idx['yennora']]

    # -- convert to longform for plotly
    d = d.drop(['buy', 'rent'], axis=1)
    d.columns.name = 'measure'
    d = d.stack().rename('value').reset_index()

    # -- order suburbs by historical mean
    s = historical_means.sort_values() \
        .reset_index().drop('buy', axis=1)
    suburb_order_map = pd.DataFrame(s.index.values, index=s['suburb'].values).to_dict()[0]
    d['order'] = d['suburb'].map(suburb_order_map)

    # -- create colour mapping - apparently not inbuilt in plotly
    n_colors = len(suburb_order_map)
    colors = px.colors.sample_colorscale("viridis", [n/(n_colors-1) for n in range(n_colors)])

    fig = px.line(
        d.sort_values(['order', 'n_beds', 'yr_ended'], ascending=False),
        x='yr_ended',
        y='value',
        color='suburb',
        color_discrete_sequence=colors,
        facet_col='n_beds',
        facet_row='dwelling_type',
    )
    fig.update_traces(opacity=.4)
    # fig.for_each_annotation(lambda x: x.update(text=x.text.split('=')[-1]))

    fig.show('browser')


plot_historical_yield(df)

# %% correlation plot

d = df.pivot_table(index=['suburb', 'dwelling_type', 'n_beds', 'yr_ended'],
            columns='ownership_type',
            values='median')
d['yield'] = d['rent'] * 50 / d['buy']
# d['yield_mv_avg'] = d['yield'].rolling(window=12).mean()

historical_means = d.groupby(level='suburb')['buy'].mean()

d[(d['measure'] == 'yield') &
(d['dwelling_type'] == 'house')] \
    .sort_values(['order', 'n_beds', 'yr_ended'], ascending=False),

