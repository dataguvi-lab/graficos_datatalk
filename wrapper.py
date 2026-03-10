import os
import appconfig as cfg
import pandas as pd
import logging
import json
from dotenv import load_dotenv
from conn_pstg import start_connection_datalake, start_connection_zeroum
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
    
    @staticmethod
    def get_boletim_inpasa():
        conn = start_connection_datalake()           
        df = pd.read_sql_query(cfg.QUERY_GRAFICO_INPASA, conn)
        df = pd.DataFrame(df)
        conn.close()
        return df
    
    @staticmethod
    def get_projecao_deposito():
        conn = start_connection_zeroum()           
        df = pd.read_sql_query(cfg.QUERY_PROJECAO_ZEROUM, conn)
        df = pd.DataFrame(df)
        df.rename(columns={'atualdepositohoje': 'AtualDepositoHoje', 'maiordepositomesanterior': 'MaiorDepositoMesAnterior'}, inplace=True)
        conn.close()
        return df
    
    @staticmethod
    def get_projecao_deposito_energia():
        conn = start_connection_zeroum()           
        df = pd.read_sql_query(cfg.QUERY_PROJECAO_ENERGIA, conn)
        df = pd.DataFrame(df)
        df.rename(columns={'atualdepositohoje': 'AtualDepositoHoje', 'maiordepositomesanterior': 'MaiorDepositoMesAnterior'}, inplace=True)
        conn.close()
        return df