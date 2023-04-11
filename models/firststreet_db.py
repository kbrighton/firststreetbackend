import psycopg2
import pandas as pd
from sqlalchemy import create_engine


conn = psycopg2.connect(database="Firststreet",
                        user='postgres', password='L4RPEverywhere!',
                        host='192.168.1.245', port='32775'
                        )
