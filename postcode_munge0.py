# %%

import pandas as pd


regions = pd.read_csv('regions.csv', header=None)
postcodes = pd.read_csv('suburb_postcodes.csv')

regions

# %%
region_list = []
postcode_list = list(postcodes.Postcode)
j = 0  # regions

codes = regions.iloc[j, 0].split(' ')
start = codes[0]
if len(codes) == 1:
    end = codes[0]
else:
    end = codes[-1]

for i in postcode_list:
    if i >= int(start) and i <= int(end):
        region_list += [regions.iloc[j, 1]]

    else:
        while i > int(end):
            j += 1

            codes = regions.iloc[j, 0].split(' ')
            start = codes[0]
            if len(codes) == 1:
                end = codes[0]
            else:
                end = codes[-1]

            if i >= int(start) and i <= int(end):
                region_list += [regions.iloc[j, 1]]
            elif i < int(start):
                region_list += ['Missing Region']

# %%

postcodes['Region'] = region_list
postcodes['Region'].unique()

postcodes = postcodes[postcodes['Region'] != 'Missing Region']


# %%
postcodes.to_csv('postcodes-suburbs-regions.csv', index=False)