'''
TODO:
- plot all suburbs, colour suburbs of interest


'''

# %%
import os
import pandas as pd


from utils.sqlite_utils import read_historical_trends


try:
    df
except NameError:
    df = read_historical_trends('prices_volumes')

burbs = ['vaucluse', 'clovelly', 'randwick', 'kingsford',
       'kensington', 'coogee', 'south-coogee', 'maroubra']
d = df[df['suburb'].isin(burbs)]
# df['suburb'].unique()

d = d.pivot_table(
    index=['suburb', 'dwelling_type', 'yr_ended'],
    columns='ownership_type', values='median')
d['yield'] = d['rent'] * 52 / d['buy']

d['yield_mv_avg'] = d['yield'].rolling(window=12).mean()

# %%
# for dwelling in d.index.levels[1]:
#     print(dwelling)
#     break
# idx = pd.IndexSlice
# d.loc[idx[:, dwelling], :].drop(['buy', 'rent'], axis=1).plot()
import plotly.express as px

fig = px.line(
    d.drop(['buy', 'rent'], axis=1).stack().rename('value').reset_index(),
    x='yr_ended',
    y='value',
    color='suburb',
    facet_row='ownership_type',
    facet_col='dwelling_type',
)
fig.for_each_annotation(lambda x: x.update(text=x.text.split('=')[-1]))
fig.show()
