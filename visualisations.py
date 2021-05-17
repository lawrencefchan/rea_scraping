'''

Visualisations

geopandas test:
https://towardsdatascience.com/how-to-create-maps-in-plotly-with-non-us-locations-ca974c3bc997

'''

# %%


def load_data():
    # NOTE: Delete function from this file, make read_db importable
    # NOTE: load_data() should point to ./data/historicalprices.db
    
    t0 = time.time()

    con = sqlite3.connect('historicalprices.db')
    df = pd.read_sql_query("SELECT * FROM prices_counts", con)

    con.close()

    df['date'] = pd.to_datetime(df['date'])

    print(time.time() - t0)

    t0 = time.time()
    df = df.pivot_table(values=['house_price', 'house_count','unit_price','unit_count'],
                        index='date',
                        columns='suburb') \
        .astype(int, errors='ignore')

    df = df.swaplevel(axis=1) \
        .sort_index(axis=1, level=0)

    print(time.time() - t0)

    return df


df = load_data()

# %%
import geopandas as gpd
import pandas as pd

lga_gdf = gpd.read_file('./data/1270055003_lga_2020_aust_shp/LGA_2020_AUST.shp')
lga_gdf = lga_gdf[lga_gdf['STE_NAME16']=='New South Wales']
lga_gdf['LGA_CODE20'] = lga_gdf['LGA_CODE20'].astype(int).round(0).astype(str) # we will join on this axis, so both dataframes need this to be the same type

lga_gdf['LGA_CODE20']
# display(lga_gdf.head())



# %% Load unemployment data
emp_df = pd.read_csv('./data/ABS_C16_G43_LGA_08052021160518366.csv')
emp_df = emp_df[['LGA_2016', 'Labour force status', 'Region', 'Value']]

emp_df = emp_df[emp_df['LGA_2016'].notna()]

emp_df['LGA_2016'] = emp_df['LGA_2016'].astype(int).round(0).astype(str)
emp_df = emp_df.pivot_table(index='LGA_2016', columns='Labour force status', values='Value').reset_index().rename_axis(None, axis=1)
emp_df['percent_unemployed'] = emp_df['Total Unemployed']/(emp_df['Total Unemployed']+emp_df['Total Employed'])

emp_df.head()



# %%

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


# Merge dataframes
df_merged = lga_gdf[['LGA_CODE20', 'geometry', 'LGA_NAME20']].merge(emp_df[['LGA_2016', 'percent_unemployed']], left_on='LGA_CODE20', right_on='LGA_2016', how='outer')
df_merged = df_merged.dropna(subset=['percent_unemployed', 'LGA_CODE20', 'geometry'])
df_merged.index = df_merged.LGA_CODE20

# Plot using geopandas
fig, ax = plt.subplots(1,1, figsize=(20,20))
divider = make_axes_locatable(ax)
tmp = df_merged.copy()
tmp['percent_unemployed'] = tmp['percent_unemployed']*100
cax = divider.append_axes("right", size="3%", pad=-1)
tmp.plot(column='percent_unemployed', ax=ax,cax=cax,  legend=True, 
         legend_kwds={'label': "Unemployment rate"})
tmp.geometry.boundary.plot(color='#BABABA', ax=ax, linewidth=0.3)
ax.axis('off')
