import asyncio
import websockets
import pandas as pd
import pandasql as psql
import json

# Load the CSV file into a pandas DataFrame
df_full = pd.read_csv('../data.csv')
df = df_full.__deepcopy__()

dates = df_full["Date"].drop_duplicates().sort_values().values
df = df_full[df_full["Date"] == dates[0]]
i = 1

async def handle_query(websocket, path):
    global df
    global i
    async for message in websocket:
        try:
            # Parse the incoming message as a SQL query
            query = message

            # Ensure the DataFrame is in the local scope
            local_df = df

            # Execute the query using pandasql
            result = psql.sqldf(query, {"df": local_df})

            # Execute the query using pandasql
            # result = psql.sqldf(query, locals())
            # Convert the result to JSON and send back to the client
            result_json = result.to_json(orient="split")

            # Update the DataFrame with the next batch of data
            if i < len(dates):
                df = pd.concat([df, df_full[df_full["Date"] == dates[i]]], axis=0)
                i += 1

            await websocket.send(result_json)
        except Exception as e:
            error_message = json.dumps({"error": str(e)})
            await websocket.send(error_message)

        await asyncio.sleep(5)

async def main():
    async with websockets.serve(handle_query, "localhost", 8765):
        await asyncio.Future()  # Run forever

# Run the server
asyncio.run(main())
