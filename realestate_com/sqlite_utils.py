# %%


import sqlite3
import pandas as pd

def create_db(con):
    cur = con.cursor()  # init db cursor to execute statements and fetch results

    # create database
    cur.execute(f"CREATE TABLE state_profiles{tuple(df.columns)}")

    return


def write_recent_sales_to_db(df, con):
    '''

    con: sqlite connection - sqlite3.connect("recent_sales.db")
    '''
    qry_str = 'select max(updated) from recent_sales'
    last_updated = read_db(qry_str, con).iloc[0, 0]

    if df['updated'][0] > pd.to_datetime(last_updated).date():
        # df data is more recent than table
        df.to_sql('recent_sales', con, if_exists='append', index=False)

    return


def read_db(qry_str, con):
    '''
    Returns a pandas df.

    con: sqlite connection - sqlite3.connect("recent_sales.db")
    '''
    return pd.read_sql_query(qry_str, con)


con = sqlite3.connect("recent_sales.db")
read_db('select * from recent_sales', con)
