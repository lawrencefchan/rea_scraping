'''NOTE: work in progress. 
The source for sydneyregions.csv is not official. 

Also need to work out the aim of this whole thing.
'''

# %%

import pandas as pd

postcodes = pd.read_csv('postcodes-suburbs-regions.csv')
regions = pd.read_csv('sydneyregions.csv', header=None)

# %% get highest postcode listed
import re

max_pc = 0
for i in regions[1]:
    curr = max([int(j) for j in re.sub('[\xa0 ]', '', i.replace('to', ',')).split(',')])

    if curr > max_pc:
        max_pc = curr

max_pc

# %% explicitly name every single postcode in the region
region_postcodes = []

for i in regions[1]:
    curr = []

    pc_list = re.sub('[\xa0 ]', '', i).split(',')

    for j in pc_list:
        if 'to' in j:
            start_pc = int(j.split('to')[0])
            end_pc = int(j.split('to')[-1])
            curr += [k for k in range(start_pc, end_pc+1)]
        else:
            curr += [int(j)]

    region_postcodes += [curr]

regions[1] = region_postcodes

# %%
import numpy as np

i = 0
region_list = []

while postcodes.Postcode[i] <= max_pc:

    for j in range(len(regions)):
        if postcodes.Postcode[i] in regions[1][j]:
            region_list += [regions[0][j]]

    i += 1

postcodes['SydMetroRegion']
regions_list