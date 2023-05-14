'''
Todos:
* sort out multiple tables in recent_sales.db:
>>> con = get_db_connection("./data/recent_sales.db")
>>> get_all_tablenames(con)
[('state_profiles',), ('recent_sales',)]

* move historicalprices.db to data file
'''

# %%
import os
import sqlite3
import pandas as pd


# def create_db(con):
#     cur = con.cursor()  # init db cursor to execute statements and fetch results
#     # create database
#     cur.execute(f"CREATE TABLE state_profiles{tuple(df.columns)}")

#     return


def write_recent_sales_to_db(df, check_last_updated=True):
    '''
    Appends new data from a pandas df to database.

    df: data to append
    check_last_updated: Checks whether new data has been published before
        appended it to the db. If false, data is indiscriminately appended.
    '''

    def new_data_avail(df, con):
        '''
        Checks whether new data has been published.
        Returns true if df contains newer data than db
        '''
        qry_str = 'select max(updated) from recent_sales'
        last_updated = pd.read_sql_query(qry_str, con).iloc[0, 0]

        if df['updated'][0] > pd.to_datetime(last_updated).date():
            # queried data is more recent than existing data
            return True
        else:
            return False

    db_pth = "./data/recent_sales.db"
    con = get_db_connection(db_pth)

    if check_last_updated:
        if not new_data_avail(df, con):
            print('No new data to append. Operation aborted.')
            return

    df.to_sql('recent_sales', con, if_exists='append', index=False)
    print(f'Data successfully written to {db_pth}')

    return


def get_all_tablenames(con):
    # show all tables in db
    cur = con.cursor()
    return cur.execute("SELECT name FROM sqlite_master").fetchall()


def get_db_connection(db_pth):
    '''
    Returns the db connection for a given filepath after first checking that the
    database exists to avoid sqlite unintentionally creating empty databases.

    db_pth: file path of the database
    '''

    try:
        assert os.path.exists(db_pth)
    except AssertionError:
        raise FileNotFoundError('Database not found.')

    return sqlite3.connect(db_pth)


def read_recent_sales():
    con = get_db_connection("./data/recent_sales.db")
    return pd.read_sql_query('select * from recent_sales', con)


def read_historical_prices():
    con = get_db_connection("./historicalprices.db")
    return pd.read_sql_query('select * from prices_counts', con)


if __name__ == "__main__":
    df = read_historical_prices()
    display(df.head())
