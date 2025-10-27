from airflow import DAG
from airflow.models import Variable 
from airflow.decorators import task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import timedelta
from datetime import datetime
import snowflake.connector
import requests

def return_snowflake_conn():
    '''Establishes and returns a Snowflake connection using Airflow's SnowflakeHook.'''
    try:
        # Initialize SnowflakeHook
        hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
        
        # Execute the query to fetch results
        conn = hook.get_conn()
        return conn.cursor()
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        raise

# Task to create and load tables in Snowflake
@task
def create_tables_load_snowflake(cursor):
    try:
        cursor.execute("BEGIN;")
                       
        # Creating tables in snowflake

        cursor.execute("""CREATE TABLE IF NOT EXISTS raw.user_session_channel (
    userId int not NULL,
    sessionId varchar(32) primary key,
    channel varchar(32) default 'direct'  
); """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS raw.session_timestamp (
    sessionId varchar(32) primary key,
    ts timestamp  
); """)
        
        # Creating staging tables in snowflake
        cursor.execute("""CREATE OR REPLACE STAGE raw.blob_stage
url = 's3://s3-geospatial/readonly/'
file_format = (type = csv, skip_header = 1, field_optionally_enclosed_by = '"');""")
        

        # Loading data using copy into command

        cursor.execute("""COPY INTO raw.user_session_channel
FROM @raw.blob_stage/user_session_channel.csv;""")
        
        cursor.execute("""COPY INTO raw.session_timestamp
FROM @raw.blob_stage/session_timestamp.csv; """)
        
        cursor.execute("COMMIT;")
        
        print("Data loaded successfully into Snowflake tables.")
    except Exception as e:
        cursor.execute("ROLLBACK;")
        print("Error at function - creat_tables_load_snowflake ",e)
        raise


# Defining the DAG
with DAG(
    dag_id = "etl_session_data_to_snowflake",
    start_date = datetime(2025, 10, 27),
    catchup = False,
    tags = ['ETL'],
    schedule = '*/15 * * * *' # schedule to run every 15 mins
)as dag:
    cursor = return_snowflake_conn()
    create_tables_load_snowflake(cursor)
