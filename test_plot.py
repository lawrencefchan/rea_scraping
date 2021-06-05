'''
Working test code for generating interacitve map.
Code taken from:
https://towardsdatascience.com/how-to-create-maps-in-plotly-with-non-us-locations-ca974c3bc997

data sources:
* "Local Government Areas ASGS Ed 2020 Digital Boundaries in ESRI Shapefile Format"
    * https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/1270.0.55.003June%202020

* "Census 2016, G43 Labour force status by age by sex (LGA)"
    * http://stat.data.abs.gov.au/

'''

# %%

from read_db import load_data
import geopandas as gpd
import pandas as pd

print('start')

df = load_data()

# %%

lga_gdf = gpd.read_file('./test_data/1270055003_lga_2020_aust_shp/LGA_2020_AUST.shp')
lga_gdf = lga_gdf[lga_gdf['STE_NAME16']=='New South Wales']
lga_gdf['LGA_CODE20'] = lga_gdf['LGA_CODE20'].astype(int).round(0).astype(str) # we will join on this axis, so both dataframes need this to be the same type

# display(lga_gdf.head())



# %% Load unemployment data
emp_df = pd.read_csv('./test_data/ABS_C16_G43_LGA_18052021104154762.csv')
emp_df = emp_df[['LGA_2016', 'Labour force status', 'Region', 'Value']]

emp_df = emp_df[emp_df['LGA_2016'].notna()]

emp_df['LGA_2016'] = emp_df['LGA_2016'].astype(int).round(0).astype(str)
emp_df = emp_df.pivot_table(index='LGA_2016', columns='Labour force status', values='Value').reset_index().rename_axis(None, axis=1)
emp_df['percent_unemployed'] = emp_df['Total Unemployed']/(emp_df['Total Unemployed']+emp_df['Total Employed'])

emp_df.head()



# %%

# import matplotlib.pyplot as plt
# from mpl_toolkits.axes_grid1 import make_axes_locatable


# # Merge dataframes
# df_merged = lga_gdf[['LGA_CODE20', 'geometry', 'LGA_NAME20']].merge(emp_df[['LGA_2016', 'percent_unemployed']], left_on='LGA_CODE20', right_on='LGA_2016', how='outer')
# df_merged = df_merged.dropna(subset=['percent_unemployed', 'LGA_CODE20', 'geometry'])
# df_merged.index = df_merged.LGA_CODE20

# # Plot using geopandas
# fig, ax = plt.subplots(1,1, figsize=(20,20))
# divider = make_axes_locatable(ax)
# tmp = df_merged.copy()
# tmp['percent_unemployed'] = tmp['percent_unemployed']*100
# cax = divider.append_axes("right", size="3%", pad=-1)
# tmp.plot(column='percent_unemployed', ax=ax,cax=cax,  legend=True, 
#          legend_kwds={'label': "Unemployment rate"})
# tmp.geometry.boundary.plot(color='#BABABA', ax=ax, linewidth=0.3)
# ax.axis('off')


# %% Convert the data frame to a GeoJSON, plot with plotly
import plotly.graph_objects as go

df_merged = df_merged.to_crs(epsg=4326) # convert the coordinate reference system to lat/long
lga_json = df_merged.__geo_interface__ #covert to geoJSON

MAPBOX_ACCESSTOKEN = 'pk.eyJ1IjoibGF3cmVuY2VmY2hhbiIsImEiOiJjazdlNnl4c3IwZnV1M2xxc2I4NXRmZ3hiIn0.j6nePQcJV0bckBFgH19ZPg'

zmin = df_merged['percent_unemployed'].min()
zmax = df_merged['percent_unemployed'].max()

# Set the data for the map
data = go.Choroplethmapbox(
        geojson = lga_json,             #this is your GeoJSON
        locations = df_merged.index,    #the index of this dataframe should align with the 'id' element in your geojson
        z = df_merged.percent_unemployed, #sets the color value
        text = df_merged.LGA_NAME20,    #sets text for each shape
        colorbar=dict(thickness=20, ticklen=3, tickformat='%',outlinewidth=0), #adjusts the format of the colorbar
        marker_line_width=1, marker_opacity=0.7, colorscale="Viridis", #adjust format of the plot
        zmin=zmin, zmax=zmax,           #sets min and max of the colorbar
        hovertemplate = "<b>%{text}</b><br>" +
                    "%{z:.0%}<br>" +
                    "<extra></extra>")  # sets the format of the text shown when you hover over each shape

# Set the layout for the map
layout = go.Layout(
    title = {'text': f"Population of Victoria, Australia",
            'font': {'size':24}},       #format the plot title
    mapbox1 = dict(
        domain = {'x': [0, 1],'y': [0, 1]}, 
        center = dict(lat=-36.5 , lon=145.5),
        accesstoken = MAPBOX_ACCESSTOKEN, 
        zoom = 6),                      
    autosize=True,
    height=650,
    margin=dict(l=0, r=0, t=40, b=0))

# Generate the map
fig=go.Figure(data=data, layout=layout)
fig.show()

input('hit enter to end')