import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import date, datetime
from configuracion.leer_data_gs import leer_hoja_google

def vista_distribuidoras():
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

    # --- CARGA DE DATOS DIRECTA DESDE EXCEL ---
    @st.cache_data
    def load_and_merge_data():
        try:
            # Lectura de archivos originales .xlsx
            # Nota: Asegúrate de tener instalada la librería 'openpyxl'
            df_ventas = leer_hoja_google("ventas_helados")
            df_info = leer_hoja_google("coordinadores_distribuidoras")
            
            # Limpieza de nombres de columnas (quitar espacios en blanco)
            df_ventas.columns = df_ventas.columns.astype(str).str.strip()
            df_info.columns = df_info.columns.astype(str).str.strip()
            
            # Asegurar formato de fecha en la columna FECHA
            df_ventas['FECHA'] = pd.to_datetime(df_ventas['FECHA'], format='mixed', dayfirst=True)
            df_ventas['FECHA'] = pd.to_datetime(df_ventas['FECHA'])
            
            # --- LIMPIEZA DE DATOS NUMÉRICOS (Manejo de comas) ---
            # Si el punto no existe y la coma es el decimal, convertimos a formato Python
            if 'VENTA' in df_ventas.columns:
                # df_ventas['VENTA'] = (
                #     df_ventas['VENTA']
                #     .astype(str)
                #     .str.replace(',', '.', regex=False)
                #     .str.strip()
                # )
                df_ventas['VENTA'] = pd.to_numeric(df_ventas['VENTA'], errors='coerce').fillna(0)
            if 'TICKET PROMEDIO' in df_ventas.columns:
                # df_ventas['TICKET PROMEDIO'] = (
                #     df_ventas['TICKET PROMEDIO']
                #     .astype(str)
                #     .str.replace(',', '.', regex=False)
                #     .str.strip()
                # )
                df_ventas['TICKET PROMEDIO'] = pd.to_numeric(df_ventas['TICKET PROMEDIO'], errors='coerce').fillna(0)
            if 'CLIENTES' in df_ventas.columns:
                df_ventas['CLIENTES'] = pd.to_numeric(df_ventas['CLIENTES'], errors='coerce').fillna(0)
            
            # Cruce de información por la columna DISTRIBUIDORA
            # Realizamos un merge para traer la información del COORDINADOR a las ventas
            df_final = pd.merge(df_ventas, df_info, on="DISTRIBUIDORA", how="left")
            
            # Limpieza de columnas vacías o residuales
            df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]
            
            return df_final
        except Exception as e:
            st.error(f"Error al leer los archivos Excel: {e}")
            return pd.DataFrame()

    df = load_and_merge_data()

    # --- CUERPO PRINCIPAL ---
    st.title("📈 Resumen Ejecutivo por Distribuidora")

    if not df.empty:
        # --- FILTROS EN LA VISTA ---
        st.subheader("Filtros de Análisis")
        col_f1, col_f2 = st.columns([2, 1])
        
        with col_f1:
            # Obtener lista de distribuidoras únicas
            lista_dist = sorted([c for c in df['DISTRIBUIDORA'].unique() if pd.notna(c)])
            dist_selected = st.multiselect(
                "Seleccionar Distribuidoras", 
                lista_dist, 
                default=lista_dist
            )
        
        with col_f2:
            # Cálculo de límites de datos
            min_data_date = df['FECHA'].min().date()
            max_data_date = df['FECHA'].max().date()
            
            # Cálculo de primer y último día del mes actual
            today = date.today()
            first_day_month = today.replace(day=1)
            # Para el último día, vamos al primero del mes siguiente y restamos 1 día
            if today.month == 12:
                last_day_month = today.replace(year=today.year + 1, month=1, day=1) - pd.Timedelta(days=1)
            else:
                last_day_month = today.replace(month=today.month + 1, day=1) - pd.Timedelta(days=1)
            
            # Asegurarse de que el valor por defecto esté dentro de los límites de los datos
            # Si el mes actual no tiene datos, podrías preferir usar min/max del df, 
            # pero aquí forzamos la lógica del mes actual solicitada.
            default_range = [first_day_month, last_day_month]
            
            date_range = st.date_input(
                "Rango de Fechas", 
                value=default_range,
                min_value=min_data_date
            )

        # --- LÓGICA DE FILTRADO ---
        if isinstance(date_range, list) or isinstance(date_range, tuple):
            if len(date_range) == 2:
                start_date, end_date = date_range
                mask = (df['DISTRIBUIDORA'].isin(dist_selected)) & \
                    (df['FECHA'].dt.date >= start_date) & (df['FECHA'].dt.date <= end_date)
                df_filtered = df.loc[mask]
            else:
                # Si solo se ha seleccionado una fecha en el picker todavía
                df_filtered = df[df['DISTRIBUIDORA'].isin(dist_selected)]
        else:
            df_filtered = df[df['DISTRIBUIDORA'].isin(dist_selected)]

        st.write("---")

        # --- MÉTRICAS ---
        if not df_filtered.empty:
            m1, m2, m3, m4 = st.columns(4)
            
            total_venta = df_filtered['VENTA'].sum()
            total_clientes = df_filtered['CLIENTES'].sum()
            ticket_avg = total_venta / total_clientes if total_clientes > 0 else 0
            dist_activas = df_filtered['DISTRIBUIDORA'].nunique()

            with m1:
                st.markdown(f'<div class="metric-card"><p>Ventas Totales</p><h3>${total_venta:,.2f}</h3></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><p>Total Clientes</p><h3>{total_clientes:,.0f}</h3></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-card"><p>Ticket Promedio</p><h3>${ticket_avg:,.2f}</h3></div>', unsafe_allow_html=True)
            with m4:
                st.markdown(f'<div class="metric-card"><p>Distribuidoras</p><h3>{dist_activas:,.0f}</h3></div>', unsafe_allow_html=True)

            st.write("##")

            # --- GRÁFICOS ---
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.subheader("Ventas por Distribuidora")
                ventas_dist = df_filtered.groupby('DISTRIBUIDORA')['VENTA'].sum().reset_index().sort_values('VENTA', ascending=False)
                fig_bar = px.bar(
                    ventas_dist, 
                    x='DISTRIBUIDORA', 
                    y='VENTA',
                    color='VENTA',
                    color_continuous_scale='Viridis',
                    text_auto='.2s'
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_chart2:
                st.subheader("Evolución Temporal de Ventas")
                evolucion = df_filtered.groupby('FECHA')['VENTA'].sum().reset_index()
                fig_line = px.line(evolucion, x='FECHA', y='VENTA', markers=True)
                fig_line.update_traces(line_color='#4f46e5')
                st.plotly_chart(fig_line, use_container_width=True)

            # --- TABLA DE DETALLE ---
            st.subheader("Detalle por Coordinador y Distribuidora")
            
            # Agrupamos para mostrar el resumen consolidado
            resumen_tabla = df_filtered.groupby(['COORDINADOR', 'DISTRIBUIDORA']).agg({
                'VENTA': 'sum',
                'CLIENTES': 'sum',
                'TICKET PROMEDIO': 'mean'
            }).reset_index().sort_values(by='VENTA', ascending=False)

            st.dataframe(resumen_tabla, 
                column_config={
                    "VENTA": st.column_config.NumberColumn(format="dollar"),
                    "TICKET PROMEDIO": st.column_config.NumberColumn(format="dollar")
                },     
                width="stretch", hide_index=True
            )

            # --- BOTÓN DE DESCARGA EXCEL ---
            # Función para convertir DF a Excel en memoria
            def to_excel(df):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Resumen')
                return output.getvalue()

            excel_data = to_excel(resumen_tabla)
            
            st.download_button(
                label="📥 Descargar Reporte Excel",
                data=excel_data,
                file_name="resumen_distribuidoras.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No hay datos disponibles para los filtros seleccionados.")
    else:
        st.error("No se pudieron cargar los archivos Excel. Por favor, asegúrate de que los archivos 'ventas_helados.xlsx' y 'data_coord_dist.xlsx' estén en la misma carpeta.")