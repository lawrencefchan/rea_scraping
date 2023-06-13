# %%
import pandas as pd


def plot_recent_sales(df):
    '''
    df: data from recent_sales.db
    '''

    df['updated'] = pd.to_datetime(df['updated'])

    plot_var = 'clearance_rate'
    # plot_var = 'private_sales'

    d = df.pivot_table(
            index='updated',
            columns='state',
            values=plot_var) \
                .drop(['wa', 'tas', 'nt'], axis=1)

    d = d.set_index(pd.to_datetime(d.index))

    # plot lines (need uniform timeseries for nice xticklabels)
    ax = d.resample('1D').mean().interpolate().plot()

    h, l = ax.get_legend_handles_labels()  # get legend for lines
    clrs = [l.get_color() for l in ax.lines]  # get colors for lines

    # plot dots
    d.plot(ax=ax, ls='', marker='.', ms=8, legend=False)
    ax.legend(h, l)  # drop legend for dots
    for i, l in enumerate(ax.get_lines()):  # set color for dots
        l.set_color(clrs[i%len(clrs)])

    ax.set_title(plot_var)
    # ax.grid()


if __name__ == "__main__":
    from utils.sqlite_utils import read_recent_sales

    plot_df = read_recent_sales()
    plot_recent_sales(plot_df)
