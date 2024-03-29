'''
Run with `python -m utils.plot_utils`
'''

# %%
from utils  import general_utils
from utils import sqlite_utils

import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


def plot_recent_sales(df, plot_var='private_sales'):
    '''
    df: data from recent_sales.db
    plot_var: ['sold_at_auction', 'sold_prior_to_auction',
       'sold_after_auction', 'withdrawn', 'passed_in', 'private_sales',
       'clearance_rate']
    '''

    def plot_data(plot_var):
        '''
        plotting helper function
        '''
        d = df.pivot_table(
                index='updated',
                columns='state',
                values=plot_var) \
                    .drop(['wa', 'tas', 'nt'], axis=1)

        d = d.set_index(pd.to_datetime(d.index))

        # plot lines (need uniform timeseries for nice xticklabels)
        ax = d.resample('1D').mean().interpolate().plot()

        h, l = ax.get_legend_handles_labels()  # get legend for lines
        clrs = [l.get_color() for l in ax.lines]  # get colors for lines

        # plot dots
        d.plot(ax=ax, ls='', marker='.', ms=8, legend=False)
        ax.legend(h, l)  # drop legend for dots
        for i, l in enumerate(ax.get_lines()):  # set color for dots
            l.set_color(clrs[i%len(clrs)])

        ax.set_title(plot_var)
        # ax.grid()

        plt.show()

    df['updated'] = pd.to_datetime(df['updated'])

    if plot_var == 'all':
        col = ['sold_at_auction', 'sold_prior_to_auction',
       'sold_after_auction', 'withdrawn', 'passed_in', 'private_sales',
       'clearance_rate']
        for c in col:
            plot_data(c)
    else:
        plot_data(plot_var)


def plotly_geoplot(df, plot_col):
    '''
    Interactive plot using plotly (working)

    df: gpd dataframe
        must contain 'geometry', index must be suburb
    '''
    fig = px.choropleth_mapbox(
        # convert coord reference system  (needed for plotly, .shp only)
        df.to_crs("WGS84"),
        geojson=df['geometry'],  # must be df series for some reason
        locations=df.index,
        color=plot_col,
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        center=dict(lat=-33.85, lon=151.07),
        )

    fig.show("browser")


def gpd_geoplot(df):
    '''
    Static plot using geopandas (working)

    df: gpd dataframe (must contain 'geometry')
    '''
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    fig, ax = plt.subplots(1,1, figsize=(20,20))
    divider = make_axes_locatable(ax)

    cax = divider.append_axes("right", size="3%", pad=-1)
    df.plot(column='data',
            ax=ax,
            cax=cax,
            legend=True, 
            legend_kwds={'label': "Avg. annual growth rate"})
    df.geometry.boundary.plot(color='#BABABA', ax=ax, linewidth=0.3)
    ax.axis('off')

    plt.show()


if __name__ == "__main__":

    plot_df = sqlite_utils.read_recent_sales()
    plot_recent_sales(plot_df, plot_var='all')

    # display(plot_df.head())

    # # %% spatial plot (working but long compute)
    # import numpy as np
    # suburb_geom = general_utils.get_suburb_geom()
    # suburb_geom['data'] = np.random.randint(1, 100, len(suburb_geom))

    # gpd_geoplot(suburb_geom)

# %%
