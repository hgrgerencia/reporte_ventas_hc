import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

nombre_hoja_calculo = st.secrets["NOMBRE_DEL_DOCUMENTO"]

def leer_hoja_google(nombre_pestana=None):
    # 1. Configuración de Credenciales
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        # Asegúrate de que 'credentials.json' esté en la misma carpeta que este script
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # 2. Abrir el documento
        # Puedes abrirlo por su nombre exacto
        spreadsheet = client.open(nombre_hoja_calculo)
        
        # 3. Seleccionar la pestaña (por nombre o por índice)
        if nombre_pestana:
            worksheet = spreadsheet.worksheet(nombre_pestana)
        else:
            worksheet = spreadsheet.get_worksheet(0) # Abre la primera por defecto
            
        # 4. Obtener todos los valores
        # get_all_records() asume que la primera fila son los encabezados
        datos = worksheet.get_all_records()
        
        # Convertir a DataFrame de Pandas para manejarlo fácilmente
        df = pd.DataFrame(datos)
        #print(df.head())
        return df

    except gspread.exceptions.SpreadsheetNotFound:
        print("Error: No se encontró el archivo. Revisa que el nombre sea exacto.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    return None



