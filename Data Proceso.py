import pandas as pd
import geopandas as gpd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- Ajusta rutas ---
excel_path = "data_consolidada.xlsx"
shp_path = "nxcantones.shp"
output_geojson = "data_preparada.geojson"

# ----------------------------------------------------------
# 1. CARGA DE DATOS
# ----------------------------------------------------------
df = pd.read_excel(excel_path)
sp = gpd.read_file(shp_path)

# ----------------------------------------------------------
# 2. CÁLCULO DE INDICADORES (equivalente al código en R)
# ----------------------------------------------------------
df["madre_10_14_2022"] = df["madre_10_19_2022"] - df["madre_15_19_2022"]
df["mujeres_10_14"] = df["mujeres_10_19"] - df["mujeres_15_19"]

df["pop_rural"] = df.apply(lambda x: x["pop_tot"] if x["area"]=="Rural" else 0, axis=1)
df["madre_10_19_rural_2022"] = df.apply(lambda x: x["madre_10_19_2022"] if x["area"]=="Rural" else 0, axis=1)
df["total_nacimientos_rural_2022"] = df.apply(lambda x: x["total_nacimientos_2022"] if x["area"]=="Rural" else 0, axis=1)

# Agrupación
agg_vars = [
    "madre_10_19_2022","madre_15_19_2022","madre_10_14_2022",
    "mujeres_10_19","mujeres_15_19","mujeres_10_14",
    "nbi","den_nbi",
    "homicidios_2022",
    "pop_tot","pop_indigena","pop_rural",
    "comp2_nbi","ninos_6_12",
    "madre_10_19_rural_2022","total_nacimientos_rural_2022"
]

df_sum = df.groupby("canton")[agg_vars].sum().reset_index()

# Indicadores
df_sum["TEF_10_19"] = 1000 * df_sum["madre_10_19_2022"] / df_sum["mujeres_10_19"]
df_sum["TEF_15_19"] = 1000 * df_sum["madre_15_19_2022"] / df_sum["mujeres_15_19"]
df_sum["TEF_10_14"] = 1000 * df_sum["madre_10_14_2022"] / df_sum["mujeres_10_14"]

df_sum["POP_MADRE_10_19_RURAL"] = df_sum["madre_10_19_rural_2022"] / df_sum["total_nacimientos_rural_2022"].replace(0, 1)
df_sum["POP_INDIGENA"] = df_sum["pop_indigena"] / df_sum["pop_tot"]
df_sum["POP_RURAL"] = df_sum["pop_rural"] / df_sum["pop_tot"]
df_sum["POB_NBI"] = df_sum["nbi"] / df_sum["den_nbi"]
df_sum["TM_HOMICIDIOS"] = 100000 * df_sum["homicidios_2022"] / df_sum["pop_tot"]
df_sum["TM_HOMICIDIOS"] = df_sum["TM_HOMICIDIOS"].fillna(0)
df_sum["PROP_SIN_ACCESO_EDUC_6_12"] = df_sum["comp2_nbi"] / df_sum["ninos_6_12"]

# ----------------------------------------------------------
# 3. PCA (solo primer componente)
# ----------------------------------------------------------
vars_pca = [
    "TEF_10_19",
    "POP_INDIGENA",
    "POP_MADRE_10_19_RURAL",
    "POB_NBI",
    "PROP_SIN_ACCESO_EDUC_6_12",
    "TM_HOMICIDIOS"
]

X = df_sum[vars_pca].fillna(0)
X_scaled = StandardScaler().fit_transform(X)

pca = PCA(n_components=1)
df_sum["INDICE_VULNERABILIDAD"] = pca.fit_transform(X_scaled)

# ----------------------------------------------------------
# 4. UNIÓN CON EL SHAPEFILE
# ----------------------------------------------------------
sp_final = sp.merge(df_sum, left_on="DPA_CANTON", right_on="canton", how="left")

# ----------------------------------------------------------
# 5. EXPORTAR
# ----------------------------------------------------------
sp_final.to_file(output_geojson, driver="GeoJSON")

print("✔ Archivo preparado: data_preparada.geojson")