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


def get_db_connection(db_path, new_db=False):
    '''
    Returns the db connection for a given filepath after first checking that the
    database exists to avoid sqlite unintentionally creating empty databases.

    db_path: file path of the database
    new_db: flag for creating a new db, skips filepath check
    '''

    if not new_db:
        try:
            assert os.path.exists(db_path)
        except AssertionError:
            raise FileNotFoundError('Database not found.')

    return sqlite3.connect(db_path)


def create_db(filename, table_name, columns):

    if filename[-3:] != '.db':
        filename += '.db'

    assert isinstance(columns, tuple)

    con = get_db_connection(f'data\\{filename}', new_db=True)
    cur = con.cursor()  # init db cursor to execute statements and fetch results
    # create database
    cur.execute(f"CREATE TABLE {table_name}{columns}")

    return
    # create_db('historical_trends', 'current_snapshot', tuple(df.columns))
    # create_db('historical_trends', 'prices_volumes', tuple(df_trends.columns))


def get_all_tablenames(con):
    # show all tables in db
    cur = con.cursor()
    return cur.execute("SELECT name FROM sqlite_master").fetchall()


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

    db_path = "./data/recent_sales.db"
    con = get_db_connection(db_path)

    if check_last_updated:
        if not new_data_avail(df, con):
            print('No new data to append. Operation aborted.')
            return
    # else: [new data available or force written]
    df.to_sql('recent_sales', con, if_exists='append', index=False)
    print(f'Data successfully written to {db_path}')

    return


# def write_snapshot_to_db(df):
#     '''
#     Writes measures scraped from json payload
#     '''
#     db_path = "./data/historical_trends.db"
#     con = get_db_connection(db_path)
#     df.to_sql('current_snapshot', con, if_exists='append', index=False)
#     print(f'Data successfully written to {db_path}')


def write_trends_to_db(df, table):
    db_path = "./data/historical_trends.db"
    con = get_db_connection(db_path)
    df.to_sql(table, con, if_exists='append', index=False)
    print(f'Data successfully written to {db_path}')


def read_recent_sales():
    con = get_db_connection("./data/recent_sales.db")
    return pd.read_sql_query('select * from recent_sales', con)


def read_historical_prices():
    con = get_db_connection("./data/historicalprices.db")
    return pd.read_sql_query('select * from prices_counts', con)


def read_historical_trends(table=None):
    '''
    sel_scrape scraper writes data into this db
    '''
    con = get_db_connection("./data/historical_trends.db")

    tables = [i[0] for i in get_all_tablenames(con)]
    if table not in tables:
        raise ValueError(f'Table name must be on of {tables}')
    else:
        return pd.read_sql_query(f'select * from {table}', con)


if __name__ == "__main__":
    pass
    # display(read_historical_prices().head())
    # display(read_recent_sales().head())

    # %% --- check contents for each table in db
    con = get_db_connection("./data/historical_trends.db")
    for t in [i[0] for i in get_all_tablenames(con)]:
        print(t)
        display(pd.read_sql_query(f'select * from {t}', con).head())

    # %% --- delete
    # con = get_db_connection("./data/historical_trends.db")
    # cur = con.cursor()
    # cur.execute("DROP TABLE prices_volumes")

    # # --- delete current query
    # from datetime import datetime
    # con = get_db_connection("./data/historical_trends.db")

    # tables = ('prices_volumes', 'current_snapshot')
    # for t in tables:
    #     qry = f'''
    #         DELETE FROM {t}
    #         WHERE last_queried = '{datetime.today().date().strftime('%Y-%m-%d')}'
    #         '''

    #     cur = con.cursor()
    #     cur.execute(qry)
    #     con.commit()
    # con.close()

    # %% --- new db
    create_db('historical_trends', 'prices_volumes', tuple(df_trends.columns))
