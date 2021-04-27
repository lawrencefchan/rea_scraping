# %%
import sqlite3
import pandas as pd

con = sqlite3.connect('historicalprices.db')
cur = con.cursor()

# cur.execute('DROP TABLE prices_counts')

for row in cur.execute('SELECT * FROM prices_counts ORDER BY date'):
    print(row)

con.close()

# %%
con = sqlite3.connect('historicalprices.db')
df = pd.read_sql_query("""SELECT date, unit_price
                          FROM prices_counts
                          WHERE suburb='lavender bay'""", con)

# df[df['suburb'] == 'dawes']
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', drop=True).plot(marker='.')

con.close()
