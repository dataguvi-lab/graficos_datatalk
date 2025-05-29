import os
import appconfig as cfg
import pandas as pd
import logging
import json
from dotenv import load_dotenv
from conn_pstg import start_connection_datalake
import pytz
from datetime import datetime


load_dotenv()

class DataWrapper:

    @staticmethod
    def get_reports_notifications():
        conn = start_connection_datalake()           
        df = pd.read_sql_query(cfg.QUERY_GRAFICOS_ZEROUM, conn)
        df = pd.DataFrame(df)
        conn.close()
        return df