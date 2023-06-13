# %%
from utils.general_utils import get_suburb_geom

import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


def plot_recent_sales(df):
    '''
    df: data from recent_sales.db
    '''

    df['updated'] = pd.to_datetime(df['updated'])

    plot_var = 'clearance_rate'
    # plot_var = 'private_sales'

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
    from utils.sqlite_utils import read_recent_sales

    plot_df = read_recent_sales()
    plot_recent_sales(plot_df)

    # %% spatial plot
    import numpy as np
    suburb_geom = get_suburb_geom()
    suburb_geom['data'] = np.random.randint(1, 100, len(suburb_geom))

    gpd_geoplot(suburb_geom)
