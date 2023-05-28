# %%
import pandas as pd


def plot_recent_sales(df):
    '''
    df: data from recent_sales.db
    '''

    df['updated'] = pd.to_datetime(df['updated'])

    plot_var = 'clearance_rate'
    # plot_var = 'private_sales'
    ax = df.pivot_table(
        index='updated',
        columns='state',
        values=plot_var) \
            .drop(['wa', 'tas', 'nt'], axis=1) \
            .plot(marker='.')
    ax.set_title(plot_var)
    ax.grid()


if __name__ == "__main__":
    from utils.sqlite_utils import read_recent_sales

    df = read_recent_sales()
    plot_recent_sales(df)
