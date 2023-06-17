'''
Sends a request to allhomes for each suburb in suburb_postcodes.csv to find
a list of suburbs/postcodes used by allhomes.

Results are saved in allhome_suburb_list.csv
'''

# %%
import pandas as pd
import requests

df = pd.read_csv('./data/suburb_postcodes.csv')
df.sample(5)

# %%

# list consistent suburbs/postcodes between allhomes and suburb_postcodes.csv
lst = []
locality_lst = []

url_base = 'https://www.allhomes.com.au/svc/locality/searchallbyname?n='
for r in df.itertuples():
    consistent = False
    locality = None

    print(r.Postcode, r.Suburb)

    response = requests.get(f'{url_base}{r.Suburb}')
    for i in response.json()['division']:
        # print(i)
        suburb, state, postcode = i['name'].split(', ')

        if (state == 'NSW') & (suburb == r.Suburb):
            if int(postcode) == r.Postcode:
                consistent = True
                locality = i['value']
                break
            else:
                # suburb exists but allhomes lists a different postcode
                # note: doesn't break, so an exact match may be found
                consistent = int(postcode)
                locality = i['value']

    lst += [consistent]
    locality_lst += [locality]

df['Consistent'] = lst
df['Locality'] = pd.array(locality_lst, dtype="Int64")

df
# %% ensure csv only has single suburb/postcode combination

# suburbs where allhomes and suburb_postcodes.csv postcodes are different
d = df[~df['Consistent'].isin([True, False])]
d = d[d['Suburb'].duplicated(keep=False)].sort_values('Suburb')

for g, data in d.groupby('Suburb'):
    print(g)

    i = df[(df['Suburb'] == g) &
           (df['Postcode'] == int(data['Consistent'].iloc[0]))]

    if i.shape[0] != 1:
        display(data)
        display(df[df['Suburb'] == g])

'''
Every suburb with inconsistent postcodes already exists in
allhomes_suburb_list, except for Four Mile Creek, which has
no streets on allhomes.

Thus they can all be dropped.
'''

# %%
d = df[df['Consistent'] == True].drop('Consistent', axis=1)
d.head()

# %%
d.to_csv('allhomes_suburb_list.csv', index=False)
