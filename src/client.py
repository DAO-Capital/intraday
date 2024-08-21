import asyncio
import websockets
import json
import pandas as pd
from io import StringIO
import logging

logging.basicConfig(level=logging.INFO)

async def query_csv():
    uri = "ws://localhost:8765"
    logging.info(f"Connecting to {uri}")
    
    async with websockets.connect(uri, max_size=None) as websocket:
        logging.info("Connected to server")
        
        while True:
            query = "SELECT * FROM df WHERE Date = (SELECT MAX(Date) FROM df) "
            logging.info(f"Sending query: {query}")

            try:
                await websocket.send(query)
                logging.info("Query sent, waiting for response...")

                result_json = await websocket.recv()
                logging.info("Received response")

                result = json.loads(result_json)

                if "error" in result:
                    logging.error(f"Error from server: {result['error']}")
                else:
                    result_df = pd.read_json(StringIO(result_json), orient="split")
                    logging.info(f"Received DataFrame with shape: {result_df.shape}")
                    print(result_df)  # Print first few rows

            except websockets.exceptions.ConnectionClosed:
                logging.error("WebSocket connection closed unexpectedly. Retrying in 5 seconds...")
                await asyncio.sleep(5)
                continue

            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
                logging.info("Retrying in 5 seconds...")
                await asyncio.sleep(5)
                continue

            await asyncio.sleep(1)  # Wait before next query

if __name__ == "__main__":
    asyncio.run(query_csv())