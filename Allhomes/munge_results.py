# %%
import json


def reset_status(results):
    # set complete flag to false
    for suburb in results.keys():
        for street in results[suburb].keys():
            if street == 'complete':
                # print(suburb, results[suburb]['complete'])
                results[suburb]['complete'] = False
            else:
                # print(street, results[suburb][street]['complete'])
                results[suburb][street]['complete'] = False


def read_results(filename, munge=True):
    '''
    Parameters
    ----------
    munge: If True, applies processing to results including removing `None`
    values and 'complete' keys.
    '''
    # load results
    with open(filename) as f:
        results = json.load(f)

    def munge_dict(d):
        # recursively removes all None values, 'complete' keys from dict
        if isinstance(d, dict):
            return {k: munge_dict(v) for k, v in d.items()
                    if v is not None  # remove None
                    and k != 'complete'  # remove 'complete' keys
                    and bool(munge_dict(v))}  # remove empty dicts
        else:
            return d

    if munge:
        results = munge_dict(results)

    return results


read_results('haymarket.json')['Haymarket']  # ['Barangaroo'].keys()


# %%  process data
# for r in ('Contract', 'Transfer', 'Listed'):
#     results[r] = pd.to_datetime(results[r], format='%d/%m/%Y')

# results['Days on market'] = int(results['Days on market'])
# assert results['Days on market'] == (results['Contract'] -
#   results['Listed']).days

# assert set(data.keys()) == set([
#     'Contract',
#     'Transfer',
#     'Listed',
#     'Days on market',
#     'Block size',
#     'Transfer type',
#     'Purpose',
#     'Price'
#     ])
