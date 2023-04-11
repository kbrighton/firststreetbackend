import psycopg2
import pandas as pd
from sqlalchemy import create_engine


conn = psycopg2.connect(database="Firststreet",
                        user='postgres', password='L4RPEverywhere!',
                        host='192.168.1.245', port='32775'
                        )

cursor = conn.cursor()

engine=create_engine("postgresql+psycopg2://postgres:L4RPEverywhere!@192.168.1.245:32775/Firststreet")


df = pd.read_csv("../importCSV/files/Orders.txt", low_memory=False, encoding="cp1252")
print(df.head())

try:
    df.to_sql("Orders", engine, if_exists='append', index=False)

except Exception as e:
    print(e)
finally:
    engine.dispose()