from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import timedelta
from datetime import datetime
import snowflake.connector
import requests

def return_snowflake_conn():

    # Initialize SnowflakeHook
    hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    
    # Execute the query to fetch results
    conn = hook.get_conn()
    return conn.cursor()

# Task to extract data from Alpha Vantage API
@task
def extract_data():
    try:
        symbol = 'AAPL'
        alpha_vantage_key = Variable.get("vantage_api_key")
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={alpha_vantage_key}'
        r = requests.get(url)
        data = r.json()
        results = [] # empyt list to hold  90 days of stock info (open, high, low, close, volume)
        for d in data["Time Series (Daily)"]: # d is a date: "YYYY-MM-DD"
            stock_info = data["Time Series (Daily)"][d]
            stock_info["date"] = d
            results.append(stock_info)
        print("Extracted data for 90 days from Apha Vantage")
        return results
    except Exception as e:
        print("Error at function - extract_data ",e)
        raise


# helper function to insert data into Snowflake
def insert_data(table, results, cursor):
    try:
        for r in results:
            open = r["1. open"]
            high = r["2. high"]
            low = r["3. low"]
            close = r["4. close"]
            volume = r["5. volume"]
            symbol = "AAPL"
            date = r["date"]
            insert_sql = f"INSERT INTO {table} (symbol, date, open, close, high, low, volume) VALUES ('{symbol}', '{date}', {open}, {close}, {high}, {low}, {volume})"

            cursor.execute(insert_sql) 
    except Exception as e:
        print("Error at function - insert_data ",e)


# Task to execute the ETL pipeline
@task
def execute_pipeline(price_list):
    table_name = "raw.stock_data"
    cursor = return_snowflake_conn()
    try:
        cursor.execute("BEGIN;")
        # creating table
        create_table_sql = """

CREATE TABLE IF NOT EXISTS RAW.stock_data(
  SYMBOL VARCHAR(10) NOT NULL,
  DATE DATE NOT NULL,
  OPEN FLOAT NOT NULL,
  CLOSE FLOAT NOT NULL,
  HIGH FLOAT NOT NULL,
  LOW FLOAT NOT NULL,
  VOLUME FLOAT NOT NULL,
  PRIMARY KEY(SYMBOL, DATE)

)

"""
        cursor.execute(create_table_sql)

        # deleting records from the table
        cursor.execute("DELETE FROM RAW.stock_data")

        # Inserting records into the table
        insert_data(table_name, price_list, cursor)
        cursor.execute("COMMIT;")
        print("Data inserted successfully into Snowflake table")
    except Exception as e:
        print("Error at function execute_pipeline ",e)
        cursor.execute("ROLLBACK;")
        raise

# Defining the DAG
with DAG(
    dag_id = "alpha_vantage_to_snowflake",
    start_date = datetime(2025, 10, 1),
    catchup = False,
    tags = ['ETL'],
    schedule = '*/15 * * * *' # schedule to run every 15 mins
)as dag:
    price_list = extract_data()
    execute_pipeline(price_list)
