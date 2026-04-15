import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import date, datetime
from configuracion.leer_data_gs import leer_hoja_google



def vista_corrdinadores_chocolates():
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
            df_ventas = leer_hoja_google("venta_chocolates")
            df_info = leer_hoja_google("coordinadores_distribuidoras")
            # st.write(df_info)
            # st.write(df_ventas )
            
            # Limpieza de columnas
            df_ventas.columns = df_ventas.columns.astype(str).str.strip()
            df_info.columns = df_info.columns.astype(str).str.strip()
            
            # Formato de fecha
            df_ventas['FECHA'] = pd.to_datetime(df_ventas['FECHA'], format='mixed', dayfirst=True)
            df_ventas['FECHA'] = pd.to_datetime(df_ventas['FECHA'])
            
            # --- LIMPIEZA DE DATOS NUMÉRICOS (Manejo de comas) ---
            # Si el punto no existe y la coma es el decimal, convertimos a formato Python
            if 'VENTA' in df_ventas.columns:
                df_ventas['VENTA'] = pd.to_numeric(df_ventas['VENTA'], errors='coerce').fillna(0)
                
            if 'TICKET PROMEDIO' in df_ventas.columns:
                df_ventas['TICKET PROMEDIO'] = pd.to_numeric(df_ventas['TICKET PROMEDIO'], errors='coerce').fillna(0)
                
            if 'Kilos Promedio' in df_ventas.columns:
                df_ventas['Kilos Promedio'] = pd.to_numeric(df_ventas['Kilos Promedio'], errors='coerce').fillna(0)
                
            if 'CLIENTES' in df_ventas.columns:
                df_ventas['CLIENTES'] = pd.to_numeric(df_ventas['CLIENTES'], errors='coerce').fillna(0)
            # Merge para asignar Coordinador a cada registro de venta
            df_merged = pd.merge(df_ventas, df_info, on="DISTRIBUIDORA", how="left")
            
            # Rellenar coordinadores desconocidos para evitar errores en agrupaciones
            df_merged['COORDINADOR'] = df_merged['COORDINADOR'].fillna("SIN ASIGNAR")
            
            return df_merged
        except Exception as e:
            st.error(f"Error al procesar datos: {e}")
            return pd.DataFrame()

    df = load_coordinator_data()

    # --- CUERPO PRINCIPAL ---
    st.title("👥 Panel de Control: Coordinadores")

    if not df.empty:
        # --- SECCIÓN DE FILTROS ---
        st.subheader("Filtros Globales")
        c_f1, c_f2 = st.columns([2, 1])
        
        with c_f1:
            lista_coords = sorted(df['COORDINADOR'].unique().astype(str))
            coords_selected = st.multiselect(
                "Seleccionar Coordinadores", 
                lista_coords, 
                default=lista_coords
            )
        
        with c_f2:
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
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            mask = (df['COORDINADOR'].isin(coords_selected)) & \
                (df['FECHA'].dt.date >= date_range[0]) & (df['FECHA'].dt.date <= date_range[1])
            df_filtered = df.loc[mask]
        else:
            df_filtered = df[df['COORDINADOR'].isin(coords_selected)]

        st.write("---")

        if not df_filtered.empty:
            # --- MÉTRICAS TOTALES ---
            st.subheader("Resumen Total de Gestión")
            m1, m2, m3, m4 = st.columns(4)
            
            ventas_totales = df_filtered['VENTA'].sum()
            clientes_totales = df_filtered['CLIENTES'].sum()
            ticket_medio = ventas_totales / clientes_totales if clientes_totales > 0 else 0
            cant_coords = df_filtered['COORDINADOR'].nunique()
            venta_kilos_promedio = df_filtered['Kilos Promedio'].sum()
            
            
            # Formateo para visualización local
            def format_money(val):
                return f"${val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            with m1:
                st.markdown(f'<div class="metric-card"><p>Venta Consolidada</p><h3>{format_money(ventas_totales)}</h3></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><p>Cobertura Clientes</p><h3>{clientes_totales:,.0f}</h3></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-card"><p>Ticket Promedio Global</p><h3>{format_money(ticket_medio)}</h3></div>', unsafe_allow_html=True)
            with m4:
                st.markdown(f'<div class="metric-card"><p>Total Kg</p><h3>{venta_kilos_promedio:,.2f}</h3></div>', unsafe_allow_html=True)

            st.write("##")

            # --- COMPARATIVA ENTRE COORDINADORES ---
            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                st.subheader("Ventas por Coordinador")
                resumen_coord = df_filtered.groupby('COORDINADOR')['VENTA'].sum().reset_index().sort_values('VENTA', ascending=False)
                fig_coord = px.bar(
                    resumen_coord, x='COORDINADOR', y='VENTA',
                    color='VENTA', color_continuous_scale='Blues',
                    text_auto='.3s'
                )
                st.plotly_chart(fig_coord, use_container_width=True)

            with col_graf2:
                st.subheader("Evolución por Coordinador")
                evol_coord = df_filtered.groupby(['FECHA', 'COORDINADOR'])['VENTA'].sum().reset_index()
                fig_evol = px.line(evol_coord, x='FECHA', y='VENTA', color='COORDINADOR', markers=True)
                st.plotly_chart(fig_evol, use_container_width=True)

            # --- TABLAS SEPARADAS POR COORDINADOR ---
            st.write("---")
            st.subheader("Desglose Detallado por Coordinador")
            
            for coordinador in coords_selected:
                with st.expander(f"📋 Ver detalle: {coordinador}", expanded=False):
                    df_c = df_filtered[df_filtered['COORDINADOR'] == coordinador]
                    
                    # Resumen de distribuidoras bajo este coordinador
                    tabla_c = df_c.groupby('DISTRIBUIDORA').agg({
                        'VENTA': 'sum',
                        'CLIENTES': 'sum',
                        'TICKET PROMEDIO': 'mean'
                    }).reset_index().sort_values('VENTA', ascending=False)
                    
                    # Mini métricas del coordinador
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Ventas", f"${df_c['VENTA'].sum():,.2f}")
                    c2.metric("Clientes", f"{df_c['CLIENTES'].sum():,.0f}")
                    c3.metric("Distribuidoras", len(tabla_c))
                    
                    # Tabla de distribuidoras
                    st.dataframe(tabla_c, 
                        column_config={
                            "VENTA": st.column_config.NumberColumn(format="dollar"),
                            "TICKET PROMEDIO": st.column_config.NumberColumn(format="dollar")
                        },
                        width="stretch", hide_index=True
                    )

            # --- EXPORTACIÓN A EXCEL ---
            st.write("##")
            def to_excel(df):
                output = io.BytesIO()
                # Creamos un reporte que agrupa todo
                reporte_final = df.groupby(['COORDINADOR', 'DISTRIBUIDORA']).agg({
                    'VENTA': 'sum',
                    'CLIENTES': 'sum',
                    'TICKET PROMEDIO': 'mean'
                }).reset_index()
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    reporte_final.to_excel(writer, index=False, sheet_name='Resumen_Coordinadores')
                return output.getvalue()

            excel_out = to_excel(df_filtered)
            st.download_button(
                label="📥 Descargar Reporte de Coordinadores (Excel)",
                data=excel_out,
                file_name="reporte_gestion_coordinadores.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No hay datos para los filtros seleccionados.")
    else:
        st.error("No se encontraron los archivos necesarios.")

    


