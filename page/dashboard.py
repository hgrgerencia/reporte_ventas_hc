import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import date, datetime
from configuracion.leer_data_gs import leer_hoja_google
from util.formato_moneda import format_latino

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

    df_h, df_c = load_coordinator_data()

    if df_h.empty and df_c.empty:
        st.warning("No se pudieron cargar los datos.")
        return

    # --- FILTROS GLOBALES ---
    with st.expander("🔍 Filtros de Fecha y Coordinación", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            # Rango de fechas basado en helados (usualmente el más completo)
            min_d, max_d = df_h['FECHA'].min().date(), df_h['FECHA'].max().date()
            rango = st.date_input("Periodo de Análisis", [min_d, max_d])
        with col2:
            todos_coords = sorted(list(set(df_h['COORDINADOR'].unique()) | set(df_c['COORDINADOR'].unique())))
            coords_sel = st.multiselect("Filtrar por Coordinador", todos_coords, default=todos_coords)

    # Filtrado dinámico
    def filtrar(df):
        if len(rango) == 2:
            mask = (df['FECHA'].dt.date >= rango[0]) & (df['FECHA'].dt.date <= rango[1]) & (df['COORDINADOR'].isin(coords_sel))
            return df.loc[mask]
        return df[df['COORDINADOR'].isin(coords_sel)]

    f_h = filtrar(df_h)
    f_c = filtrar(df_c)

    # --- PESTAÑAS ---
    st.write("### Sell Out")
    t1, t2, t3 = st.tabs(["🍦 Helados", "🍫 Chocolates", "📈 Consolidado"])

    def render_metrics(df_f, color_scale):
        if 'MES_AÑO' not in df_f.columns and not df_f.empty:
            df_f['MES_AÑO'] = df_f['FECHA'].dt.to_period('M').astype(str)
        
        total_v = df_f['VENTA'].sum()
        total_cl = df_f['CLIENTES'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><p>Venta Total</p><h3>{format_latino(total_v)}</h3></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><p>Clientes Atendidos</p><h3>{total_cl:,.0f}</h3></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><p>Ticket Promedio</p><h3>{format_latino(total_v/total_cl if total_cl > 0 else 0)}</h3></div>', unsafe_allow_html=True)

        st.write("### Evolución Mensual Acumulada")
        mensual = df_f.groupby('MES_AÑO')['VENTA'].sum().reset_index()
        fig_mes = px.line(mensual, x='MES_AÑO', y='VENTA', markers=True, text=[format_latino(x) for x in mensual['VENTA']])
        st.plotly_chart(fig_mes, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.write("### Por Coordinador")
            por_coord = df_f.groupby('COORDINADOR')['VENTA'].sum().reset_index().sort_values('VENTA')
            st.plotly_chart(px.bar(por_coord, y='COORDINADOR', x='VENTA', orientation='h', color='VENTA', color_continuous_scale=color_scale), use_container_width=True)
        
        with col_b:
            st.write("### Top 10 Distribuidoras")
            top_dist = df_f.groupby('DISTRIBUIDORA')['VENTA'].sum().reset_index().sort_values('VENTA', ascending=False)
            # 1. Calculas el top 10
            top_10 = top_dist.head(10).copy()

            # 2. Calculas la suma de todo lo que NO es el top 10
            otros_valor = top_dist.iloc[10:]['VENTA'].sum()

            # 3. Creas una fila para "Otros"
            fila_otros = pd.DataFrame({'DISTRIBUIDORA': ['Otros'], 'VENTA': [otros_valor]})

            # 4. Concatenas
            df_para_grafico = pd.concat([top_10, fila_otros], ignore_index=True)

            # 5. Graficas (ahora el 100% será el total real)
            st.plotly_chart(px.pie(df_para_grafico, values='VENTA', names='DISTRIBUIDORA', hole=0.4))

        st.write("### Detalle Acumulado por Distribuidor")
        tabla = df_f.groupby(['COORDINADOR', 'DISTRIBUIDORA']).agg({'VENTA': 'sum', 'CLIENTES': 'sum'}).reset_index()
        st.dataframe(tabla.style.format({'VENTA': '{:,.2f}', 'CLIENTES': '{:,.0f}'}), width='stretch')

    with t1:
        render_metrics(f_h, "Blues")

    with t2:
        render_metrics(f_c, "Reds")

    with t3:
        # Consolidación de ambos DataFrames
        total_v_h = f_h['VENTA'].sum()
        total_v_c = f_c['VENTA'].sum()
        
        c1, c2 = st.columns(2)
        fig_pie = px.pie(values=[total_v_h, total_v_c], names=['Helados', 'Chocolates'], title="Distribución de Ingresos")
        c1.plotly_chart(fig_pie, use_container_width=True)
        
        # Tabla comparativa por mes
        h_mes = f_h.groupby('MES_AÑO')['VENTA'].sum().rename('Venta Helados')
        c_mes = f_c.groupby('MES_AÑO')['VENTA'].sum().rename('Venta Chocolates')
        comparativo = pd.concat([h_mes, c_mes], axis=1).fillna(0)
        comparativo['Total'] = comparativo.sum(axis=1)
        
        st.write("### Comparativo Mensual Consolidado")
        st.dataframe(comparativo.style.format('{:,.2f}'), width='stretch', column_config={
            "MES_AÑO": "Periodo", 
        })


    


