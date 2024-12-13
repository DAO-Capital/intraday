import asyncio
import websockets
import json
import pandas as pd
import pandasql as psql
from io import StringIO
import logging
from extract import extract_data
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

METRICS_FILE_PATH = "../../data/etl_QUESTDB_metrics.csv"
url_server = os.getenv("HOST_WEBSOCKET")

async def query_csv():
    uri = f"ws://{url_server}:8765"
    logging.info(f"Connecting to {uri}")

    query_count = 0
    
    while True:
        async with websockets.connect(uri, max_size=None) as websocket:
            logging.info("Connected to server")
        
            # Query ajustada para refletir as colunas que já existem no servidor
            query = "SELECT * FROM df"
            logging.info(f"Sending query: {query}")

            try:
                await websocket.send(query)
                logging.info("Query sent, waiting for response...")

                # Recebe o JSON contendo o DataFrame do servidor
                result_json = await websocket.recv()
                logging.info("Received response")

                result = json.loads(result_json)

                if "error" in result:
                    logging.error(f"Error from server: {result['error']}")
                else:
                    # Converte o JSON para DataFrame
                    result_df = pd.read_json(StringIO(result_json), orient="split")
                    logging.info(f"Received DataFrame with shape: {result_df.shape}")
                    
                    # Processa o DataFrame recebido
                    time_taken, memory_used = extract_data(result_df)

                    # Para tualizar o arquivo de métricas de ETL, descomente a linha abaixo
                    #update_metrics_csv(query, result_df.shape[0], time_taken, memory_used)
                    query_count += 1

            except websockets.exceptions.ConnectionClosed:
                logging.error("WebSocket connection closed unexpectedly. Retrying in 5 seconds...")
                await asyncio.sleep(5)
                continue
                
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
                logging.info("Retrying in 5 seconds...")
                await asyncio.sleep(5)
                continue

            await asyncio.sleep(1)  # Espera antes da próxima query

def update_metrics_csv(query, rows, time_taken, memory_used):
    if os.path.exists(METRICS_FILE_PATH):
        metrics_df = pd.read_csv(METRICS_FILE_PATH)
    else:
        metrics_df = pd.DataFrame(columns=["query", "rows", "time(s)", "memory(MB)"])
        
    new_data = pd.DataFrame({
        "query": [query], 
        "rows": [rows], 
        "time(s)": [time_taken], 
        "memory(MB)": [memory_used]
    })

    if not metrics_df.empty and not metrics_df.isna().all().all():
        updated_metrics_df = pd.concat([metrics_df, new_data], ignore_index=True)
    else:
        updated_metrics_df = new_data

    updated_metrics_df.to_csv(METRICS_FILE_PATH, index=False)
    logging.info(f"Metrics updated: {new_data.to_dict('records')}")

if __name__ == "__main__":
    asyncio.run(query_csv())
