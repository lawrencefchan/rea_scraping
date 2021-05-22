'''
Misc Visualisations

'''

# %%

from re import sub
from sqlite3.dbapi2 import Error
from typing import final
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from read_db import load_data
from munge import get_suburb_geom, filter_dataset


def pricevscount(df, suburb=None):
    if suburb is None:
        suburb = 'parramatta'

    df = df[suburb]

    df.columns = pd.MultiIndex.from_product(
        [['house', 'unit'], ['count', 'price']],
        names=['dwelling', 'meas'])

    fig, axes = plt.subplots(nrows=2)
    sm = plt.cm.ScalarMappable(cmap='viridis', 
                            norm=plt.Normalize(vmin=df.index.min().year,
                                                vmax=df.index.max().year))
    df['house'].plot.scatter('count', 'price', c=df.index, cmap='viridis', ax=axes[0])
    df['unit'].plot.scatter('count', 'price', c=df.index, cmap='viridis', ax=axes[1])
    fig.colorbar(sm, ax=axes.ravel().tolist())
    axes[0].ticklabel_format(style='plain')
    axes[1].yaxis.set_major_locator(plt.MultipleLocator(50000))

    fig.suptitle(suburb.title())
    axes[1].set_xlabel('Dwellings sold')

    plt.show()


def plot_single(df, suburb=None, dwelling_type=None):
    if suburb is None:
        suburb = 'macquarie park'
    if dwelling_type is None:
        dwelling_type = 'unit'

    idx = pd.IndexSlice[suburb, f'{dwelling_type}_price']
    ax = df.loc[:, idx].plot(legend=False, marker='.')
    # ax.get_xaxis().set_ticks([])

    ax.set_title(f'{suburb.title()} - {dwelling_type} prices')

    plt.show()

def bar_charts(df):
    '''
    plot all standard deviations (WIP)
    NOTE: combine this section with main branch
    '''

    # df.loc[:, pd.IndexSlice[:, 'house_price']].plot(legend=False)

    df0 = df.loc[:, pd.IndexSlice[:, 'house_price']].std(axis=0).sort_values()[-20:-1]
    df0.plot.bar(legend=False)

    # df0.loc[:, pd.IndexSlice[:, 'house_count']].plot(legend=False)


# prepare df
price_data = filter_dataset(load_data(), max_missing_years=2, min_listed_count=10)
burbs = get_suburb_geom(price_data)

price_data = price_data.loc[:, pd.IndexSlice[:, 'house', 'price']]
price_data.columns = price_data.columns.get_level_values(0)

timedelta = (price_data.index - price_data.index[0]).astype('timedelta64[D]')

# %% munge
growthlist = []

for i, suburb in enumerate(burbs['Suburb']):
    '''
    calculate average annual growth

    TODO: work out what stats error is:
        RuntimeWarning: invalid value encountered in double_scalars
        * slope = ssxym / ssxm
        * t = r * np.sqrt(df / ((1.0 - r + TINY)*(1.0 + r + TINY)))
        * slope_stderr = np.sqrt((1 - r**2) * ssym / ssxm / df)
    '''

    try:
        data = price_data.loc[:, suburb.lower()]
        mask =  ~np.isnan(data)
        slope, intercept, r_value, p_value, std_err = stats.linregress(timedelta[mask], data.values[mask])
        growth = slope/intercept * 365

        # display(price_data.loc[:, suburb.lower()].head())
    except Error as e:
        print(suburb, e)
        growth = np.nan
    finally:
        growthlist += [[suburb, growth]]
        continue

    # --- working plot for historical price
    # ax = data.plot(marker='.')
    # plt.ticklabel_format(axis='y', style='plain')
    # ax.set_title(f'{suburb}: {growth:.2}%')
    # plt.show()


# %% munge2
df = burbs.merge(pd.DataFrame(growthlist, columns=['Suburb', 'Growth']), on='Suburb') \
          .drop('Postcode', axis=1).set_index('Suburb')

# # %%# Plot using geopandas
# ''' Working but:
#     * questionable colours/indicated growth rate
#     * very remote regions showing up??
# '''
# from mpl_toolkits.axes_grid1 import make_axes_locatable

# fig, ax = plt.subplots(1,1, figsize=(20,20))
# divider = make_axes_locatable(ax)

# cax = divider.append_axes("right", size="3%", pad=-1)
# df.plot(column='Growth',
#         ax=ax,
#         cax=cax,
#         legend=True, 
#         legend_kwds={'label': "Avg. annual growth rate"})
# df.geometry.boundary.plot(color='#BABABA', ax=ax, linewidth=0.3)
# ax.axis('off')

# plt.show()




# %% Convert the data frame to a GeoJSON, plot with plotly
import plotly.graph_objects as go

df = df.to_crs(epsg=4326) # convert the coordinate reference system to lat/long
lga_json = df.__geo_interface__ #covert to geoJSON

MAPBOX_ACCESSTOKEN = 'pk.eyJ1IjoibGF3cmVuY2VmY2hhbiIsImEiOiJjazdlNnl4c3IwZnV1M2xxc2I4NXRmZ3hiIn0.j6nePQcJV0bckBFgH19ZPg'

zmin = df['Growth'].min()
zmax = df['Growth'].max()

hovertemplate = "<b>%{text}</b><br>%{z:.0%}<br><extra></extra>"
# Set the data for the map
data = go.Choroplethmapbox(
    geojson=lga_json,  # this is your GeoJSON
    locations=df.index,  # the index of this dataframe should align with the 'id' element in your geojson
    z=df.Growth,  # sets the color value
    text=df.Suburb,  # sets text for each shape
    colorbar=dict(thickness=20, ticklen=3, tickformat='%',outlinewidth=0), #adjusts the format of the colorbar
    marker_line_width=1,
    marker_opacity=0.7,
    colorscale="Viridis",  # adjust format of the plot
    zmin=zmin,  # sets min and max of the colorbar
    zmax=zmax,  
    hovertemplate=hovertemplate  # sets the format of the text shown when you hover over each shape
    )

# Set the layout for the map
layout = go.Layout(
    title={'text': f"Avg. Annual Growth Rates - Houses (2012-2021)",
            'font': {'size':24}},  # format the plot title
    mapbox1=dict(
        domain={'x': [0, 1],'y': [0, 1]}, 
        center=dict(lat=-36.5 , lon=145.5),
        accesstoken=MAPBOX_ACCESSTOKEN, 
        zoom=6),                      
    autosize=True,
    height=650,
    margin=dict(l=0, r=0, t=40, b=0))

# Generate the map
fig = go.Figure(data=data, layout=layout)
fig.show()

input('hit enter to end')
