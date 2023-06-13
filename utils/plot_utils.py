# %%
import pandas as pd


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


if __name__ == "__main__":
    from utils.sqlite_utils import read_recent_sales

    plot_df = read_recent_sales()
    plot_recent_sales(plot_df)

# %%
def plotly_geoplot():
    '''
    NOTE:
    - reading the .shp file is slow
    - need geopandas to read .shp
    - .shp needs to be converted to geojson to be plotted with plotly

    TODO:
    - handle missing suburbs
    - check if geojson is any faster/easier to use
    '''
    import numpy as np
    import geopandas as gpd
    # Get df of suburb names and their respective boundaries

    # NSW Localities SHP GDA20(ZIP):
    # https://data.gov.au/dataset/ds-dga-91e70237-d9d1-4719-a82f-e71b811154c6/details
    df_geom = gpd.read_file("./test_data/GDA2020/nsw_localities.shp")

    postcodes = pd.read_csv('postcodes-suburbs-regions.csv')

    # len(set(postcodes['Suburb']) - set(df_geom['LOC_NAME']))

    suburb_geom = df_geom[['LOC_NAME', 'geometry']] \
        .rename({'LOC_NAME': 'Suburb'}, axis=1) \
        .merge(postcodes, how='inner', on='Suburb')
    
    suburb_geom['data'] = np.random.randint(1, 100, len(suburb_geom))

    # simplify geometry accuracy
    accuracy = 50  # meters
    suburb_geom['geometry'] = suburb_geom.to_crs(suburb_geom.estimate_utm_crs()) \
        .simplify(accuracy).to_crs(suburb_geom.crs)

    # --- interactive plot using plotly
    import plotly.express as px
    fig = px.choropleth_mapbox(
        # convert coord reference system  (needed for plotly, .shp only)
        suburb_geom.to_crs("WGS84").set_index('Suburb'),
        geojson=suburb_geom['geometry'],  # needs to be a df series for some reason
        locations=suburb_geom.index,
        color='data',
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        center=dict(lat=-33.85 , lon=151.07),
        )

    fig.show()

    # # --- static plot using geopandas (working)
    # import matplotlib.pyplot as plt
    # from mpl_toolkits.axes_grid1 import make_axes_locatable

    # fig, ax = plt.subplots(1,1, figsize=(20,20))
    # divider = make_axes_locatable(ax)

    # cax = divider.append_axes("right", size="3%", pad=-1)
    # suburb_geom.plot(column='data',
    #         ax=ax,
    #         cax=cax,
    #         legend=True, 
    #         legend_kwds={'label': "Avg. annual growth rate"})
    # suburb_geom.geometry.boundary.plot(color='#BABABA', ax=ax, linewidth=0.3)
    # ax.axis('off')

    # plt.show()


plotly_geoplot()

# %%

# def generate_geomap(dwelling_type):

#     print('munging (1/2)')
#     price_data = filter_dataset(load_data(), max_missing_years=2, min_listed_count=10)
#     burbs = get_suburb_geom(price_data)

#     price_data = price_data.loc[:, pd.IndexSlice[:, dwelling_type, 'price']]
#     price_data.columns = price_data.columns.get_level_values(0)

#     timedelta = (price_data.index - price_data.index[0]).astype('timedelta64[D]')

#     # munge (calculate growth)
#     growthlist = []

#     for i, suburb in enumerate(burbs['Suburb']):
#         '''
#         calculate average annual growth

#         NOTE:
#             * incorrect growth calc because monthly data is weighted too high

#         TODO: work out what stats error is:
#             RuntimeWarning: invalid value encountered in double_scalars
#             * slope = ssxym / ssxm
#             * t = r * np.sqrt(df / ((1.0 - r + TINY)*(1.0 + r + TINY)))
#             * slope_stderr = np.sqrt((1 - r**2) * ssym / ssxm / df)
#         '''

#         try:
#             data = price_data.loc[:, suburb.lower()]
#             mask =  ~np.isnan(data)
#             slope, intercept, r_value, p_value, std_err = stats.linregress(timedelta[mask], data.values[mask])
#             growth = slope/intercept * 365

#             # display(price_data.loc[:, suburb.lower()].head())
#         except Exception as e:
#             # print(suburb, e)
#             growth = np.nan
#         finally:
#             growthlist += [[suburb, growth]]
#             continue

#         # --- working plot for historical price
#         # ax = data.plot(marker='.')
#         # plt.ticklabel_format(axis='y', style='plain')
#         # ax.set_title(f'{suburb}: {growth:.2}%')
#         # plt.show()


#     # munge2
#     print('munging (2/2)')
#     df = burbs.merge(pd.DataFrame(growthlist, columns=['Suburb', 'Growth']), on='Suburb') \
#             .drop('Postcode', axis=1)  # .set_index('Suburb')

#     # --- (working) Plot using geopandas
#     # from mpl_toolkits.axes_grid1 import make_axes_locatable

#     # fig, ax = plt.subplots(1,1, figsize=(20,20))
#     # divider = make_axes_locatable(ax)

#     # cax = divider.append_axes("right", size="3%", pad=-1)
#     # df.plot(column='Growth',
#     #         ax=ax,
#     #         cax=cax,
#     #         legend=True, 
#     #         legend_kwds={'label': "Avg. annual growth rate"})
#     # df.geometry.boundary.plot(color='#BABABA', ax=ax, linewidth=0.3)
#     # ax.axis('off')

#     # plt.show()

#     # Convert the data frame to a GeoJSON, plot with plotly
#     import plotly.graph_objects as go
#     import plotly.offline  # to save

#     print('converting data to geojson')
#     df = df.to_crs(epsg=4326) # convert the coordinate reference system to lat/long
#     lga_json = df.__geo_interface__ #covert to geoJSON

#     MAPBOX_ACCESSTOKEN = 'pk.eyJ1IjoibGF3cmVuY2VmY2hhbiIsImEiOiJjazdlNnl4c3IwZnV1M2xxc2I4NXRmZ3hiIn0.j6nePQcJV0bckBFgH19ZPg'

#     zmin = df['Growth'].min()
#     zmax = df['Growth'].max()

#     hovertemplate = """<b>%{text}</b><br>%{z:.0%}<br><extra></extra>"""

#     # Set the data for the map
#     data = go.Choroplethmapbox(
#         geojson=lga_json,  # this is your GeoJSON
#         locations=df.index,  # the index of this dataframe should align with the 'id' element in your geojson
#         z=df.Growth,  # sets the color value
#         text=df.Suburb,  # sets text for each shape
#         colorbar=dict(thickness=20, ticklen=3, tickformat='%',outlinewidth=0), #adjusts the format of the colorbar
#         marker_line_width=1,
#         marker_opacity=0.7,
#         colorscale=[[0, "red"], [zmin/(zmin-zmax), "white"], [1, "green"]],  # adjust format of the plot
#         zmin=zmin,  # sets min and max of the colorbar
#         zmax=zmax,
#         hovertemplate=hovertemplate,  # sets the format of the text shown when you hover over each shape
#         hoverlabel_align='right'
#         )

#     # Set the layout for the map
#     layout = go.Layout(
#         title={'text': f"Avg. Annual Growth Rates - {dwelling_type.title()}s (2012-2021)",
#                 'font': {'size':24}},
#         mapbox1=dict(
#             domain={'x': [0, 1],'y': [0, 1]}, 
#             center=dict(lat=-33.85 , lon=151.07),
#             accesstoken=MAPBOX_ACCESSTOKEN, 
#             zoom=9),                      
#         autosize=True,
#         height=650,
#         margin=dict(l=0, r=0, t=40, b=0)
#         )

#     # Generate the map
#     print('generating map')
#     fig = go.Figure(data=data, layout=layout)

#     # --- without offline 
#     # fig.show()
#     # input('hit enter to end')

#     # save map
#     plotly.offline.plot(fig, filename=f'{dwelling_type}.html')

