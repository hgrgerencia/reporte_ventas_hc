import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from configuracion.leer_data_gs import leer_hoja_google

def format_latino(val):
    """Formatea números al estilo: 1.234,56 (Sin símbolo de moneda)"""
    try:
        return f"{val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "0,00"

def vista_sell_in():
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
            df_maras_helados = leer_hoja_google("maras_helados")
            df_maras_chocolates = leer_hoja_google("maras_chocolates")
            df_info = leer_hoja_google("coordinadores_distribuidoras")
            
            # Limpieza de columnas
            df_maras_helados.columns = df_maras_helados.columns.astype(str).str.strip()
            df_maras_chocolates.columns = df_maras_chocolates.columns.astype(str).str.strip()
            df_info.columns = df_info.columns.astype(str).str.strip()
            
            # Formato de fecha
            df_maras_helados['FECHA'] = pd.to_datetime(df_maras_helados['FECHA'], format='mixed', dayfirst=True, errors='coerce')
            df_maras_chocolates['FECHA'] = pd.to_datetime(df_maras_chocolates['FECHA'], format='mixed', dayfirst=True, errors='coerce')
            
            # Eliminar filas con fechas nulas para evitar errores en MES_AÑO
            df_maras_helados = df_maras_helados.dropna(subset=['FECHA']).copy()
            df_maras_chocolates = df_maras_chocolates.dropna(subset=['FECHA']).copy()

            # --- LIMPIEZA DE DATOS NUMÉRICOS ---
            def to_num(df, col):
                if col in df.columns:
                    # Si viene con comas de Google Sheets, las cambiamos por puntos
                    df[col] = df[col].astype(str).str.replace(',', '.', regex=False).str.strip()
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                return df

            df_maras_helados = to_num(df_maras_helados, 'MARAS')
            df_maras_helados = to_num(df_maras_helados, 'LITROS')
            df_maras_chocolates = to_num(df_maras_chocolates, 'MARAS')
            df_maras_chocolates = to_num(df_maras_chocolates, 'KG')
            
            # Creación de columna MES_AÑO
            df_maras_helados['MES_AÑO'] = df_maras_helados['FECHA'].dt.to_period('M').astype(str)
            df_maras_chocolates['MES_AÑO'] = df_maras_chocolates['FECHA'].dt.to_period('M').astype(str)
            
            # Merge para asignar Coordinador
            df_h = pd.merge(df_maras_helados, df_info, on="DISTRIBUIDORA", how="left")
            df_c = pd.merge(df_maras_chocolates, df_info, on="DISTRIBUIDORA", how="left")
            
            df_h['COORDINADOR'] = df_h['COORDINADOR'].fillna("SIN ASIGNAR")
            df_c['COORDINADOR'] = df_c['COORDINADOR'].fillna("SIN ASIGNAR")
            
            return df_h, df_c
        except Exception as e:
            st.error(f"Error al procesar datos: {e}")
            return pd.DataFrame(), pd.DataFrame()

    df_h, df_c = load_coordinator_data()
    
    if df_h.empty and df_c.empty:
        st.warning("No se encontraron datos de Sell In.")
        return


    # --- SECCIÓN DE FILTROS ---
    with st.container(border=True):
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            todos_coords = sorted(list(set(df_h['COORDINADOR'].unique()) | set(df_c['COORDINADOR'].unique())))
            coords_sel = st.multiselect("Líderes de Zona", todos_coords, default=todos_coords)
        with col_f2:
            min_date = min(df_h['FECHA'].min(), df_c['FECHA'].min()).date()
            max_date = max(df_h['FECHA'].max(), df_c['FECHA'].max()).date()
            rango = st.date_input("Periodo de Análisis", [min_date, max_date])

    def filtrar_sellin(df):
        df_coord = df[df['COORDINADOR'].isin(coords_sel)]
        if len(rango) == 2:
            mask = (df_coord['FECHA'].dt.date >= rango[0]) & (df_coord['FECHA'].dt.date <= rango[1])
            return df_coord, df_coord.loc[mask]
        return df_coord, df_coord

    h_acum, h_range = filtrar_sellin(df_h)
    c_acum, c_range = filtrar_sellin(df_c)

    # --- PESTAÑAS ---
    t1, t2, t3 = st.tabs(["🍦 Helados (Litros)", "🍫 Chocolates (KG)", "📈 Consolidado Maras"])

    def render_sellin_tab(df_a, df_r, col_vol, unit, color):
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-card"><p>Acumulado Maras</p><h3>{format_latino(df_a["MARAS"].sum())}</h3></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><p>Maras en Periodo</p><h3>{format_latino(df_r["MARAS"].sum())}</h3></div>', unsafe_allow_html=True)
        with m3:
            vol_total = df_r[col_vol].sum()
            st.markdown(f'<div class="metric-card"><p>Total {unit}</p><h3>{vol_total:,.1f}</h3></div>', unsafe_allow_html=True)

        st.write("---")
        
        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader(f"Maras por Coordinador ({unit})")
            res_c = df_r.groupby('COORDINADOR')['MARAS'].sum().reset_index().sort_values('MARAS')
            st.plotly_chart(px.bar(res_c, y='COORDINADOR', x='MARAS', orientation='h', color='MARAS', color_continuous_scale=color), use_container_width=True)
        
        with c_right:
            st.subheader("Evolución de Maras por Mes")
            res_m = df_r.groupby('MES_AÑO')['MARAS'].sum().reset_index()
            st.plotly_chart(px.line(res_m, x='MES_AÑO', y='MARAS', markers=True), use_container_width=True)

        st.subheader("Detalle por Distribuidor")
        tabla = df_r.groupby(['COORDINADOR', 'DISTRIBUIDORA']).agg({'MARAS': 'sum', col_vol: 'sum'}).reset_index()
        st.dataframe(
            tabla,
            column_config={
                "COORDINADOR": "Líder de Zona",
                "DISTRIBUIDORA": "Distribuidor",
                "MARAS": st.column_config.NumberColumn("Cant. Maras", format="%.2f"),
                col_vol: st.column_config.NumberColumn(f"Total {unit}", format="%.1f")
            },
            hide_index=True, 
            width='stretch'
        )

    with t1:
        render_sellin_tab(h_acum, h_range, 'LITROS', 'Litros', 'Blues')

    with t2:
        render_sellin_tab(c_acum, c_range, 'KG', 'KG', 'Reds')

    with t3:
        st.subheader("Distribución Consolidada de Maras")
        tot_h = h_range['MARAS'].sum()
        tot_c = c_range['MARAS'].sum()
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.plotly_chart(px.pie(values=[tot_h, tot_c], names=['Helados', 'Chocolates'], hole=0.4, title="Mix de Maras en Periodo"), use_container_width=True)
        
        with col_m2:
            comp_c = pd.DataFrame({
                'Helados (Maras)': h_range.groupby('COORDINADOR')['MARAS'].sum(),
                'Chocolates (Maras)': c_range.groupby('COORDINADOR')['MARAS'].sum()
            }).fillna(0)
            comp_c['Total Maras'] = comp_c.sum(axis=1)
            st.write("### Resumen de Maras por Coordinador")
            st.dataframe(comp_c.style.format("{:,.2f}"), width='stretch')


    