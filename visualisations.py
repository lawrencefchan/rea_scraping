'''

Visualisations

geopandas test:
https://towardsdatascience.com/how-to-create-maps-in-plotly-with-non-us-locations-ca974c3bc997

'''

# %%
import geopandas


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

lga_gdf = geopandas.read_file('./data/1270055003_lga_2020_aust_shp/LGA_2020_AUST.shp')
# lga_gdf = lga_gdf[lga_gdf['STE_NAME16']=='Victoria'] #Select the data for the state of Victoria
# lga_gdf['LGA_CODE20'] = lga_gdf['LGA_CODE20'].astype('str') # we will join on this axis, so both dataframes need this to be the same type
lga_gdf.head()

