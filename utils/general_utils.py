# %%

import os
import pandas as pd
import geopandas as gpd


def get_suburb_geom():
    '''
    Get df of suburb names and their respective boundaries
    
    NOTE:
    - reading the .shp file is slow
    - need geopandas to read .shp
    - .shp needs to be converted to geojson to be plotted with plotly

    TODO:
    - handle missing suburbs
    - check if geojson is any faster/easier to use
    '''

    # NSW Localities SHP GDA20(ZIP):
    # https://data.gov.au/dataset/ds-dga-91e70237-d9d1-4719-a82f-e71b811154c6/details
    df_geom = gpd.read_file("./data/GDA2020/nsw_localities.shp")

    postcodes = pd.read_csv('postcodes-suburbs-regions.csv')

    # len(set(postcodes['Suburb']) - set(df_geom['LOC_NAME']))

    suburb_geom = df_geom[['LOC_NAME', 'geometry']] \
        .rename({'LOC_NAME': 'Suburb'}, axis=1) \
        .merge(postcodes, how='inner', on='Suburb')

    # simplify geometry accuracy
    accuracy = 50  # meters - 50m seems to be a good tradeoff
    suburb_geom['geometry'] = suburb_geom.to_crs(suburb_geom.estimate_utm_crs()) \
        .simplify(accuracy).to_crs(suburb_geom.crs)

    return suburb_geom
