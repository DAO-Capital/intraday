import asyncio
import websockets
import pandas as pd
import pandasql as psql
import json
import logging

logging.basicConfig(level=logging.INFO)

# Parameters
sleep_time = 5  # Time between each package

# Load the CSV file into a pandas DataFrame
df_full = pd.read_csv("../../data/merged_data.csv")
df_full["timestamp"] = pd.to_datetime(df_full["timestamp"])  # Ensure timestamp is datetime

# Sort DataFrame by timestamp to ensure correct data order
df_full = df_full.sort_values(by="timestamp")

# Get the minimum timestamp (starting point)
start_timestamp = df_full["timestamp"].min()

# Function to prepare a package of data for the current minute
def prepare_package_for_minute(current_timestamp):
    # Extract data for the current timestamp + 1 minute
    end_timestamp = current_timestamp + pd.Timedelta(minutes=1)
    chunk = df_full[(df_full["timestamp"] >= current_timestamp) & (df_full["timestamp"] < end_timestamp)].copy()
    return chunk

# Initialize the current timestamp to the start
current_timestamp = start_timestamp

async def handle_query(websocket, path):
    global current_timestamp
    logging.info("New client connected")

    try:
        async for message in websocket:
            logging.info(f"Received query: {message}")

            try:
                logging.info(f"Preparing data for timestamp: {current_timestamp}")

                # Prepare the data package for the current minute
                current_df = prepare_package_for_minute(current_timestamp)

                # Check if there is data for the current time window
                while current_df.empty:
                    current_timestamp += pd.Timedelta(minutes=1)
                    current_df = prepare_package_for_minute(current_timestamp)

                # Process the SQL query on the DataFrame
                result = psql.sqldf(message, {"df": current_df})

                # Convert the result to JSON format
                result_json = result.to_json(orient="split")

                logging.info(f"Sending result with {len(result)} rows")
                await websocket.send(result_json)

                # Move to the next minute
                current_timestamp += pd.Timedelta(minutes=1)

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
