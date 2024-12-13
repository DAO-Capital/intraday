import asyncio
import websockets
import pandas as pd
import pandasql as psql
import json
import logging
from joblib import Parallel, delayed
import multiprocessing

logging.basicConfig(level=logging.INFO)

# Parameters
send_n_rows = 9000
width_multiplier = 1
sleep_time = 5

# Load the CSV file into a pandas DataFrame
df_full = pd.read_csv("../../data/merged_data.csv")
# Ensure timestamp is in datetime format
df_full["timestamp"] = pd.to_datetime(df_full["timestamp"])

# Sort DataFrame by timestamp to ensure correct data order
df_full = df_full.sort_values(by="timestamp")

# Function to prepare the package of data
def prepare_package(start_index):
    # Extract a chunk of data of size `send_n_rows` starting from `start_index`
    chunk = df_full.iloc[start_index:start_index + send_n_rows].copy()

    return chunk

current_package_index = 0

async def handle_query(websocket, path):
    global current_package_index
    logging.info("New client connected")

    try:
        async for message in websocket:
            logging.info(f"Received query: {message}")

            try:
                logging.info(f"Preparing package {current_package_index}")
                
                # Prepare the data package
                current_df = prepare_package(current_package_index)

                # Ensure we have enough rows in the package
                while current_df.shape[0] < send_n_rows:
                    current_df = prepare_package(current_package_index)

                # Process the SQL query on the DataFrame
                result = psql.sqldf(message, {"df": current_df})

                # Convert the result to JSON format
                result_json = result.to_json(orient="split")
                
                logging.info(f"Sending result with {len(result)} rows")
                await websocket.send(result_json)
                
                # Move to the next package
                current_package_index += send_n_rows

            except Exception as e:
                error_message = json.dumps({"error": str(e)})
                logging.error(f"Error processing query: {str(e)}")
                await websocket.send(error_message)

            # Sleep between sending packages
            await asyncio.sleep(sleep_time)

    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected")

async def main():
    server = await websockets.serve(handle_query, "localhost", 8765)
    logging.info("Server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())