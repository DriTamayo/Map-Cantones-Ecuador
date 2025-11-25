import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.features import GeoJsonTooltip

# --------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------
st.set_page_config(page_title="Mapa Interactivo", layout="wide")
st.title("🗺️ Mapa Interactivo – Cantones de Ecuador")

# --------------------------------------------
# CARGA DE ARCHIVO GEOJSON PREPARADO
# --------------------------------------------
sp = gpd.read_file("data_preparada.geojson")

# Variables para visualizar (todas las numéricas)
variables = [
    col for col in sp.columns
    if col not in ["geometry", "DPA_CANTON", "canton"]
       and (sp[col].dtype in ["float64", "int64"])
]

st.subheader("Selecciona la variable a visualizar")
var = st.selectbox("Variable", variables)

# --------------------------------------------
# MAPA FOLIUM
# --------------------------------------------
st.subheader("Mapa interactivo")

m = folium.Map(location=[-1.5, -78.0], zoom_start=6, tiles="CartoDB positron")

# Capa coroplética
folium.Choropleth(
    geo_data=sp,
    data=sp,
    columns=["DPA_CANTON", var],
    key_on="feature.properties.DPA_CANTON",
    fill_color="YlOrRd",
    fill_opacity=0.8,
    line_opacity=0.4,
    nan_fill_color="lightgray",
    legend_name=var
).add_to(m)

# Tooltip
tooltip = GeoJsonTooltip(
    fields=["DPA_CANTON", var],
    aliases=["Cantón:", f"{var}:"]
)

folium.GeoJson(
    sp,
    tooltip=tooltip
).add_to(m)

st_folium(m, width=1000, height=600)
