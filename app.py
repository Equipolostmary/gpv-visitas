import streamlit as st
import pandas as pd

st.set_page_config(page_title="📍 Buscador de Visitas - Lost Mary", layout="wide")

st.title("📋 Buscador de Visitas a Puntos de Venta")
st.markdown("Consulta la última visita registrada en los puntos de venta de **Valencia**, **Asturias** y **Málaga**.")

# --- Función para cargar los datos desde Google Sheets ---
@st.cache_data
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/1RzAMfJvg7OQmVITHw0rAeHPAnn34qocMzVa6qvARMAQ/export?format=xlsx"
    xls = pd.ExcelFile(url)
    datos = {}
    for hoja in xls.sheet_names:
        df = pd.read_excel(xls, hoja)
        df["Provincia_origen"] = hoja.upper()
        datos[hoja] = df
    return datos

datos = cargar_datos()

# --- Unificar todas las pestañas en un único dataframe ---
df_total = pd.concat(datos.values(), ignore_index=True)

# Asegurar que la columna de fecha esté en formato datetime
df_total["Marca temporal"] = pd.to_datetime(df_total["Marca temporal"], errors="coerce")

# --- BUSCADOR ---
st.subheader("🔍 Buscar punto de venta por dirección")
busqueda = st.text_input("Introduce parte de la dirección (columna C):")

if busqueda:
    coincidencias = df_total[df_total["Dirección"].str.contains(busqueda, case=False, na=False)]
    
    if not coincidencias.empty:
        seleccion = st.selectbox("Selecciona la dirección exacta:", coincidencias["Dirección"].unique())
        df_filtrado = coincidencias[coincidencias["Dirección"] == seleccion]

        # Mostrar la última visita (según fecha más reciente)
        ultima_visita = df_filtrado.sort_values("Marca temporal", ascending=False).head(1).T
        ultima_visita.columns = ["Última visita"]

        st.success(f"Mostrando información de la última visita para: **{seleccion}**")
        st.dataframe(ultima_visita)

    else:
        st.warning("No se han encontrado coincidencias con esa dirección.")
else:
    st.info("Escribe parte de una dirección para comenzar la búsqueda.")

# --- INFO ADICIONAL ---
st.markdown("---")
st.caption("Desarrollado por Antonio Meca · Lost Mary · © 2025")
