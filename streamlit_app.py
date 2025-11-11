import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(
    page_title="Control de Visitas Comerciales",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Control de Visitas Comerciales")
st.markdown("---")

# Función para cargar datos
@st.cache_data
def cargar_datos():
    try:
        # Cargar el archivo Excel
        df = pd.read_excel('visitas.xlsx')
        
        # Convertir columnas de fecha si existen
        columnas_fecha = ['fecha', 'fecha_visita', 'fecha_creacion']
        for col in columnas_fecha:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'visitas.xlsx'")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {e}")
        return pd.DataFrame()

# Cargar datos
df = cargar_datos()

if not df.empty:
    # Mostrar información básica
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_visitas = len(df)
        st.metric("Total Visitas", total_visitas)
    
    with col2:
        comerciales_unicos = df['comercial'].nunique() if 'comercial' in df.columns else 0
        st.metric("Comerciales", comerciales_unicos)
    
    with col3:
        clientes_unicos = df['cliente'].nunique() if 'cliente' in df.columns else 0
        st.metric("Clientes", clientes_unicos)
    
    with col4:
        if 'fecha' in df.columns:
            ultima_visita = df['fecha'].max()
            st.metric("Última Visita", ultima_visita.strftime('%d/%m/%Y') if pd.notna(ultima_visita) else 'N/A')

    st.markdown("---")

    # Filtros
    st.subheader("🔍 Filtros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'comercial' in df.columns:
            comerciales = ['Todos'] + sorted(df['comercial'].unique().tolist())
            comercial_seleccionado = st.selectbox("Comercial:", comerciales)
        else:
            comercial_seleccionado = 'Todos'
    
    with col2:
        if 'cliente' in df.columns:
            clientes = ['Todos'] + sorted(df['cliente'].unique().tolist())
            cliente_seleccionado = st.selectbox("Cliente:", clientes)
        else:
            cliente_seleccionado = 'Todos'
    
    with col3:
        if 'estado' in df.columns:
            estados = ['Todos'] + sorted(df['estado'].unique().tolist())
            estado_seleccionado = st.selectbox("Estado:", estados)
        else:
            estado_seleccionado = 'Todos'

    # Aplicar filtros
    df_filtrado = df.copy()
    
    if comercial_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['comercial'] == comercial_seleccionado]
    
    if cliente_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['cliente'] == cliente_seleccionado]
    
    if estado_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['estado'] == estado_seleccionado]

    # Mostrar datos filtrados
    st.subheader("📋 Historial de Visitas")
    
    # Mostrar dataframe con opciones de columnas
    columnas_disponibles = df_filtrado.columns.tolist()
    columnas_seleccionadas = st.multiselect(
        "Selecciona las columnas a mostrar:",
        columnas_disponibles,
        default=columnas_disponibles[:min(6, len(columnas_disponibles))]
    )
    
    if columnas_seleccionadas:
        st.dataframe(df_filtrado[columnas_seleccionadas], use_container_width=True)
    else:
        st.dataframe(df_filtrado, use_container_width=True)

    # Estadísticas y gráficos
    st.markdown("---")
    st.subheader("📈 Estadísticas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'comercial' in df.columns and 'cliente' in df.columns:
            # Visitas por comercial
            visitas_por_comercial = df_filtrado['comercial'].value_counts()
            fig1 = px.bar(
                visitas_por_comercial,
                title="Visitas por Comercial",
                labels={'value': 'Número de Visitas', 'index': 'Comercial'}
            )
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        if 'estado' in df.columns:
            # Visitas por estado
            visitas_por_estado = df_filtrado['estado'].value_counts()
            fig2 = px.pie(
                visitas_por_estado,
                title="Distribución por Estado",
                values=visitas_por_estado.values,
                names=visitas_por_estado.index
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Búsqueda específica
    st.markdown("---")
    st.subheader("🔎 Búsqueda Avanzada")
    
    termino_busqueda = st.text_input("Buscar en todas las columnas:")
    if termino_busqueda:
        mask = df_filtrado.astype(str).apply(lambda x: x.str.contains(termino_busqueda, case=False, na=False)).any(axis=1)
        resultados_busqueda = df_filtrado[mask]
        st.write(f"Resultados de búsqueda: {len(resultados_busqueda)} registros")
        st.dataframe(resultados_busqueda, use_container_width=True)

else:
    st.info("💡 Para empezar, guarda tu archivo Excel como 'visitas.xlsx' en la misma carpeta que esta aplicación.")

# Instrucciones
with st.expander("📝 Instrucciones de Uso"):
    st.markdown("""
    1. **Prepara tu Excel**: Guarda tu archivo de visitas como `visitas.xlsx`
    2. **Columnas recomendadas**:
       - `comercial`: Nombre del comercial
       - `cliente`: Nombre del cliente visitado
       - `fecha`: Fecha de la visita
       - `estado`: Estado de la visita (completada, pendiente, cancelada)
       - `notas` o `comentarios`: Información de lo que se hizo en la visita
       - `productos`: Productos presentados
    3. **Ejecuta la app**: `streamlit run app.py`
    4. **Filtra y explora** tus datos usando los controles superiores
    """)

# Footer
st.markdown("---")
st.markdown("*Sistema de Control de Visitas - Desarrollado con Streamlit*")
