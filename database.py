import pandas as pd
import sqlite3

df = pd.read_csv("clean_customer_data.csv")

conn = sqlite3.connect("customers.db")

df.to_sql("customers", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("Database created")