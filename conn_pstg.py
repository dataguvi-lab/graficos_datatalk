import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração da conexão DATA-LAKE
def start_connection_datalake(): 
    
    conn = psycopg2.connect(host=os.getenv("DT_HOST"), 
                            database=os.getenv("DT_DATABASE"), 
                            port=os.getenv("DT_PORT"), 
                            user=os.getenv("DT_USER"),
                            password=os.getenv("DT_PASSWORD"), 
                            sslmode="require")
    #print("Conexão bem-sucedida. O banco de dados está ativo.")
    return conn