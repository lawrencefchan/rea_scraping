# %%
from read_db import load_data, filter_dataset

df = load_data()
df0 = filter_dataset(df)




df.loc[:, 'allawah']
# df.head()

# # %% plots (OLD, broken by new multiindex)
# df['house_price'].plot(legend=False)
# df['unit_price'].plot(legend=False)

# # %% outlier detection (OLD, broken by new multiindex)
# df0 = df['house_price']

# def z_score(df):
#     return (df-df.mean())/df.std(ddof=0)

# df0 = df0[df0.apply(z_score) < 3]



# %% standard deviation (WIP)

# df_std = df.loc[:, pd.IndexSlice[:, 'unit_price']].std(axis=0).sort_values()[:-5]
# ax = df_std.plot.bar(legend=False, figsize=(10,5))
# ax.set_title('House Price Variance (2012-2021)')
# ax.get_xaxis().set_ticks([])

def detect_outliers(df):
    '''
    Remove price outliers >3 standard deviations
    * checks suburb and dwelling type

    NOTE: wiki says "Deletion of outlier data is a controversial practice frowned upon"

    TODO:
    * check what degrees of freedom is for std
    '''
    nparray = df.loc[:, pd.IndexSlice[:, 'unit_price']].values
    nparray = nparray[~np.isnan(nparray)]

    return nparray.std(ddof=1), np.mean(nparray)

detect_outliers(df)

# %%
fig, axes = plt.subplots(nrows=2)

parra = df['parramatta']

parra.columns = pd.MultiIndex.from_product(
    [['house', 'unit'], ['count', 'price']],
    names=['dwelling', 'meas'])


sm = plt.cm.ScalarMappable(cmap='viridis', 
                           norm=plt.Normalize(vmin=parra.index.min().year,
                                              vmax=parra.index.max().year))
parra['house'].plot.scatter('count', 'price', c=parra.index, cmap='viridis', ax=axes[0])
parra['unit'].plot.scatter('count', 'price', c=parra.index, cmap='viridis', ax=axes[1])
fig.colorbar(sm, ax=axes.ravel().tolist())
axes[0].ticklabel_format(style='plain')
axes[1].yaxis.set_major_locator(plt.MultipleLocator(50000))

plt.show()

# %%
ax = df0.loc[:, pd.IndexSlice[:, 'unit_price']].plot(legend=False)
# ax.get_xaxis().set_ticks([])


# %% growth to date

df.loc[:, pd.IndexSlice[:, 'house_price']].plot(legend=False)

# df0 = df['house_price'].std(axis=0).sort_values()[-10:-1]
# df0.plot.bar(legend=False)

# df['house_price']['st leonards']
# df['house_count'][df0.index]

# df0.loc[:, pd.IndexSlice[:, 'house_count']].plot(legend=False)
