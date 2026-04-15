import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import date, datetime
from configuracion.leer_data_gs import leer_hoja_google

def vista_dashboard():
    # --- ESTILOS PERSONALIZADOS ---
    st.markdown("""
        <style>
        .main { background-color: #f8fafc; }
        .metric-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            text-align: center;
        }
        .block-container { padding-top: 3rem; }
        </style>
    """, unsafe_allow_html=True)

    # --- CARGA Y CRUCE DE DATOS ---
    @st.cache_data
    def load_coordinator_data():
        try:
            # Carga de archivos originales
            df_ventas_helados = leer_hoja_google("ventas_helados")
            df_ventas_chocolates = leer_hoja_google("venta_chocolates")
            df_info = leer_hoja_google("coordinadores_distribuidoras")
            # st.write(df_info)
            # st.write(df_ventas )
            
            # Limpieza de columnas
            df_ventas_helados.columns = df_ventas_helados.columns.astype(str).str.strip()
            df_ventas_chocolates.columns = df_ventas_chocolates.columns.astype(str).str.strip()
            df_info.columns = df_info.columns.astype(str).str.strip()
            
            # Formato de fecha
            df_ventas_helados['FECHA'] = pd.to_datetime(df_ventas_helados['FECHA'], format='mixed', dayfirst=True)
            df_ventas_helados['FECHA'] = pd.to_datetime(df_ventas_helados['FECHA'])
            df_ventas_chocolates['FECHA'] = pd.to_datetime(df_ventas_chocolates['FECHA'], format='mixed', dayfirst=True)
            df_ventas_chocolates['FECHA'] = pd.to_datetime(df_ventas_chocolates['FECHA'])
            
            # --- LIMPIEZA DE DATOS NUMÉRICOS (Manejo de comas) ---
            # Si el punto no existe y la coma es el decimal, convertimos a formato Python
            if 'VENTA' in df_ventas_helados.columns:
                df_ventas_helados['VENTA'] = pd.to_numeric(df_ventas_helados['VENTA'], errors='coerce').fillna(0)
            if 'VENTA' in df_ventas_chocolates.columns:
                df_ventas_chocolates['VENTA'] = pd.to_numeric(df_ventas_chocolates['VENTA'], errors='coerce').fillna(0)
                
            if 'TICKET PROMEDIO' in df_ventas_helados.columns:
                df_ventas_helados['TICKET PROMEDIO'] = pd.to_numeric(df_ventas_helados['TICKET PROMEDIO'], errors='coerce').fillna(0)
            if 'TICKET PROMEDIO' in df_ventas_chocolates.columns:
                df_ventas_chocolates['TICKET PROMEDIO'] = pd.to_numeric(df_ventas_chocolates['TICKET PROMEDIO'], errors='coerce').fillna(0)
                
            if 'CLIENTES' in df_ventas_helados.columns:
                df_ventas_helados['CLIENTES'] = pd.to_numeric(df_ventas_helados['CLIENTES'], errors='coerce').fillna(0)
            if 'CLIENTES' in df_ventas_chocolates.columns:
                df_ventas_chocolates['CLIENTES'] = pd.to_numeric(df_ventas_chocolates['CLIENTES'], errors='coerce').fillna(0)
                
            # --- MERGE DE DATOS ---
            # Merge para asignar Coordinador a cada registro de venta
            df_merged_helados = pd.merge(df_ventas_helados, df_info, on="DISTRIBUIDORA", how="left")
            df_merged_chocolates = pd.merge(df_ventas_chocolates, df_info, on="DISTRIBUIDORA", how="left")
    
            
            # Rellenar coordinadores desconocidos para evitar errores en agrupaciones
            df_merged_helados['COORDINADOR'] = df_merged_helados['COORDINADOR'].fillna("SIN ASIGNAR")
            df_merged_chocolates['COORDINADOR'] = df_merged_chocolates['COORDINADOR'].fillna("SIN ASIGNAR")
            
            return [df_merged_helados, df_merged_chocolates]
        except Exception as e:
            st.error(f"Error al procesar datos: {e}")
            return pd.DataFrame()

    df_helados, df_chocolates = load_coordinator_data()

    # --- CUERPO PRINCIPAL ---
    st.markdown("<h2 style='text-align: center; color: #1F2937;'>Resumen de ventas 2026</h2>", unsafe_allow_html=True)
    
    # TOTAL VENTAS DE HELADOS VS TOTAL VENTAS DE CHOCOLATE
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='text-align: center; color: #1F2937;'>Total Ventas Helados</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: #1F2937;'>${df_helados['VENTA'].sum():,.2f}</h4>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h3 style='text-align: center; color: #1F2937;'>Total Ventas Chocolates</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: #1F2937;'>${df_chocolates['VENTA'].sum():,.2f}</h4>", unsafe_allow_html=True)
    
    # TOTAL CLIENTES DE HELADOS VS TOTAL CLIENTES DE CHOCOLATE
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='text-align: center; color: #1F2937;'>Total Clientes Helados</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: #1F2937;'>{df_helados['CLIENTES'].sum():,.2f}</h4>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h3 style='text-align: center; color: #1F2937;'>Total Clientes Chocolates</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: #1F2937;'>{df_chocolates['CLIENTES'].sum():,.2f}</h4>", unsafe_allow_html=True)
        
    # TOTAL VENTAS MES ACTUAL
    # FILTRAR POR MES ACTUAL
    current_month = datetime.now().month
    current_year = datetime.now().year
    df_helados_MES_ACTUAL = df_helados[df_helados['FECHA'] == current_month]
    df_chocolates_MES_ACTUAL = df_chocolates[df_chocolates['FECHA'] == current_month]
    # MES HELADO VS MES CHOCOLATE
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<h3 style='text-align: center; color: #1F2937;'>Total Ventas Mes Actual {current_month} Helados</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: #1F2937;'>${df_helados_MES_ACTUAL['VENTA'].sum():,.2f}</h4>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h3 style='text-align: center; color: #1F2937;'>Total Ventas Mes Actual Chocolates</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: #1F2937;'>${df_chocolates_MES_ACTUAL['VENTA'].sum():,.2f}</h4>", unsafe_allow_html=True)
        
    # TOTAL CLIENTES MES ACTUAL
    # MES HELADO VS MES CHOCOLATE
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='text-align: center; color: #1F2937;'>Total Clientes Mes Actual Helados</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: #1F2937;'>{df_helados_MES_ACTUAL['CLIENTES'].sum():,.2f}</h4>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h3 style='text-align: center; color: #1F2937;'>Total Clientes Mes Actual Chocolates</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: #1F2937;'>{df_chocolates_MES_ACTUAL['CLIENTES'].sum():,.2f}</h4>", unsafe_allow_html=True)
    


    


