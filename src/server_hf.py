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
send_n_rows = 1000000
width_multiplier = 1
sleep_time = 5

# Load the CSV file into a pandas DataFrame
df_full = pd.read_csv("./HighFreq-Cryptocurrency EGLD Data.csv")
df_full["Date"] = pd.to_datetime(df_full["timestamp"], unit="ms")
df_full = df_full.drop(columns="timestamp")

dates = df_full["Date"].drop_duplicates().sort_values().values

def merge_chunk(chunk, merge_df, start_col, end_col):
    for x in range(start_col, end_col):
        chunk = chunk.merge(merge_df, on="Date", how="outer", suffixes=["", str(x + 1)])
    return chunk

def prepare_package(start_index):
    chunk = df_full.set_index("Date").loc[dates[start_index]: dates[start_index] + pd.Timedelta(seconds=send_n_rows - 1)].reset_index()
    merge_df = chunk.__deepcopy__()
    
    num_cores = multiprocessing.cpu_count()
    chunk_size = width_multiplier // num_cores
    
    results = Parallel(n_jobs=num_cores)(
        delayed(merge_chunk)(chunk, merge_df, i * chunk_size, (i + 1) * chunk_size)
        for i in range(num_cores)
    )
    
    final_df = pd.concat(results, axis=1)
    final_df = final_df.loc[:, ~final_df.columns.duplicated()]
    
    return final_df

current_package_index = 0

async def handle_query(websocket, path):
    global current_package_index
    logging.info("New client connected")

    try:
        async for message in websocket:
            logging.info(f"Received query: {message}")

            try:
                logging.info(f"Preparing package {current_package_index}")
                current_df = prepare_package(current_package_index)
                
                result = psql.sqldf(message, {"df": current_df})
                result_json = result.to_json(orient="split")
                
                logging.info(f"Sending result with {len(result)} rows")
                await websocket.send(result_json)
                
                current_package_index = (current_package_index + send_n_rows) % len(dates)

            except Exception as e:
                error_message = json.dumps({"error": str(e)})
                logging.error(f"Error processing query: {str(e)}")
                await websocket.send(error_message)

            if width_multiplier * send_n_rows < 500000:
                await asyncio.sleep(sleep_time)

    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected")

async def main():
    server = await websockets.serve(handle_query, "localhost", 8765)
    logging.info("Server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())