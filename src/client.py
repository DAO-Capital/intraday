import asyncio
import websockets
import json
import pandas as pd
from io import StringIO


async def query_csv():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            # Example SQL query to get the most recent data point
            query = """
                SELECT *
                FROM df
                WHERE Date = (SELECT MAX(Date) FROM df)
            """

            await websocket.send(query)

            # Receive the query result
            result_json = await websocket.recv()
            result = json.loads(result_json)

            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                # Convert the result back to a DataFrame
                result_df = pd.read_json(StringIO(result_json), orient="split")
                print(result_df)

# Run the client
asyncio.run(query_csv())

