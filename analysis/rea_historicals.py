'''
TODO:
- plot all suburbs, colour suburbs of interest


'''

# %%
import os
import pandas as pd

import plotly.graph_objects as go

from utils.sqlite_utils import read_historical_trends
from utils.plot_utils import plotly_geoplot
from utils.general_utils import get_suburb_geom


def create_geoplot(ownership='buy', dwelling='house', n_beds=0):
    '''
    Generate a map of median value by suburb

    Parameters:
    -----------
    ownership: str (buy, rent)
        Defines the ownership type to filter on

    dwelling: str (unit, house) 
        Defines the dwelling type to filter on

    n_beds: int
        Defines the number of beds to filter on. Default is `0`, which
        is any number of bedrooms.
    '''
    try:
        assert ownership in ('buy', 'rent')
        assert dwelling in ('house', 'unit')
        assert n_beds in range(5)  # should be 4 bedrooms or less
    except AssertionError as e:
        raise ValueError(f'Check input args for {create_geoplot.__name__}')

    # --- data processing
    df = read_historical_trends('prices_volumes')
    df['yr_ended'] = pd.to_datetime(df['yr_ended'])

    mask = ((df['ownership_type'] == ownership) &
            (df['n_beds'] == 0) &
            (df['dwelling_type'] == 'house'))
    df = df[mask]

    group_cols = ['suburb', 'dwelling_type', 'n_beds']
    # get latest available data
    df = df.loc[df.groupby(group_cols)['yr_ended'].idxmax()]
    drop_cols = [
        'volume',
        'yr_ended',
        'ownership_type',
        'dwelling_type',
        'n_beds',
        'last_queried']

    # --- get coordinates for each suburb to plot with geoplot
    # NOTE: geopandas processing is a bit slow
    suburb_geom = get_suburb_geom().drop(['Postcode', 'Region'], axis=1)
    suburb_geom.columns = [_.lower() for _ in suburb_geom.columns]
    suburb_geom['suburb'] = suburb_geom['suburb'].str.lower() \
        .str.replace(' ', '-')

    # --- join coords with data to plot
    df = suburb_geom.merge(
        df.drop(drop_cols, axis=1),
        how='inner', on='suburb') \
        .set_index('suburb')

    # --- plot
    plotly_geoplot(
        df.drop(['vaucluse', 'bellevue-hill', 'longueville']),
        plot_col='median'
        )

# working bar plot
# df.reset_index().sort_values('median').plot.bar(x='suburb', y='median')


'''
Analysis todos

yield
- does capital gains follow yield? e.g. correlation with lag?
- how can we normalise against market movements? should suburbs be normalised against the mean/median?

demographics: as income in an area grows, 
- independent variables: income by suburb, length of ownership
- correlation to test:
    - income vs property prices/rent
    - income vs "gentrification" (refer to USYD study?)

'''
# %%

df = read_historical_trends('prices_volumes')
# df['ownership_type'].unique()
mask = ((df['ownership_type'] == 'buy') &
        (df['n_beds'] == 0) &
        (df['dwelling_type'] == 'house'))
df_plot = df[mask].pivot_table(index=['suburb', 'yr_ended'], values='median')

# # --- working everything plot
# px.line(df[mask][['suburb', 'volume', 'yr_ended']],
#         x='yr_ended',
#         y='volume',
#         color='suburb')

# # --- resample to yearly
# df_plot.index = df_plot.index.set_levels(pd.to_datetime(df_plot.index.levels[1]), level=1)
# df_plot = df_plot.groupby(level='suburb').resample('Y', level='yr_ended').mean()

# %%



# %%

# --- test plot: change colour(thickness?) on hover
default_lw = 2
hover_lw = 3

fig = go.FigureWidget() # hover text goes here
fig.layout.hovermode = 'closest'
fig.layout.hoverdistance = -1 #ensures no "gaps" for selecting sparse data

for suburb in df_plot.index.levels[0]:
    fig.add_trace(
        go.Scatter(
            x=df_plot.loc[[suburb]].index.levels[1], 
            y=df_plot.loc[[suburb], 'median'].values,
            name=suburb,
            mode='lines',
            # text=elo_all['Round'],
            opacity=0.3,
            line={'width': default_lw, 'color':'grey'}
            )
        )

fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        # tickvals = [0,29,58,87,117,146],
        # ticktext = [2015,2016,2017,2018,2019,2020]
    )
)

# fig.update_yaxes(range=[1350, 1650])

# our custom event handler
def update_trace(trace, points, selector):
    if len(points.point_inds)==1:
        i = points.trace_index
        for x in range(0,len(fig.data)):
            fig.data[x]['line']['color'] = 'grey'
            fig.data[x]['opacity'] = 0.3
            fig.data[x]['line']['width'] = default_lw
        #print('Correct Index: {}',format(i))
        fig.data[i]['line']['color'] = 'red'
        fig.data[i]['opacity'] = 1
        fig.data[i]['line']['width'] = hover_lw


# we need to add the on_click event to each trace separately       
for x in range(0,len(fig.data)):
    fig.data[x].on_hover(update_trace)

# # show the plot
# fig

fig.write_html('test_plot.html', auto_open=True)
