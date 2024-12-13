import base64
import uuid
import pandas as pd
import time
import psutil
from dotenv import load_dotenv
import os
import psycopg2 as pg
from questdb.ingress import Sender

# Load environment variables
load_dotenv()

# Database connection details for QuestDB
USER = os.getenv("USER_QUEST", "admin")  # Default user
PASSWORD = os.getenv("PASS_QUEST", "quest")  # Default password
HOST = os.getenv("HOST_QUEST", "127.0.0.1")

# Function to generate a UUID - URL safe, Base64
def get_a_uuid():
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return r_uuid.decode('utf-8').replace('=', '')

# Function to insert the DataFrame into a QuestDB table
def insert_df_to_questdb(df, table_name):
    try:
        conf = f'http::addr={HOST}:9000;username={USER};password={PASSWORD};'
 
        # Enviando o DataFrame para o QuestDB
        with Sender.from_conf(conf) as sender:
            sender.dataframe(df, table_name=table_name, at='timestamp')  # Use timestamp as the designated time column

        print(f"Data inserted successfully into {table_name} table.")
        
    except Exception as e:
        print(f"Error inserting data into QuestDB: {e}")

# Function to process the CSV, add the protocol column, and insert into QuestDB
def extract_data(df):
    try:
        # Measure the start time
        start_time = time.time()

        # Measure memory before insert
        process = psutil.Process()
        mem_before = process.memory_info().rss

        # Convert 'timestamp' to datetime64[ns] format
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # Assuming the timestamp is in milliseconds

        # Convert numeric columns
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 
                           'quote_asset_volume', 'number_of_trades', 
                           'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']
        
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col].replace('-', None), errors='coerce')

        # Drop rows where all columns, except 'timestamp', are NaN
        df = df.dropna(subset=numeric_columns, how='all')

        table_name = "price_hf"

        # Insert the DataFrame into the QuestDB table
        insert_df_to_questdb(df, table_name)

        # Measure the end time
        end_time = time.time()

        # Measure memory after insert
        mem_after = process.memory_info().rss

        delta_time = end_time - start_time
        memory_used = mem_after - mem_before

        return delta_time, memory_used

    except Exception as e:
        print(f"Error processing data: {e}")
        return None
