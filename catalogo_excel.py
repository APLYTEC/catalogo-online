
import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data
def cargar_datos():
    return pd.read_excel("PRUEBA.xlsx")

def obtener_ruta_imagen(codigo):
    extensiones = [".jpg", ".jpeg", ".png"]
    for ext in extensiones:
        ruta = Path("imagenes") / f"{codigo}{ext}"
        if ruta.exists():
            return str(ruta)
    return None

df = cargar_datos()

# Búsqueda por nombre o código
busqueda = st.text_input("Buscar producto")
if busqueda:
    df_filtrado = df[df["Nombre"].str.contains(busqueda, case=False, na=False) | df["Código"].astype(str).str.contains(busqueda)]
else:
    df_filtrado = df

# Mostrar los productos
for _, fila in df_filtrado.iterrows():
    st.markdown(f"### {fila['Nombre']}")
    st.markdown(f"**Código:** {fila['Código']} &nbsp;&nbsp;&nbsp; **Precio:** {fila['Precio']} €")

    ruta_imagen = obtener_ruta_imagen(fila["Código"])
    if ruta_imagen:
        st.image(ruta_imagen, use_container_width=True)
    else:
        st.warning("Imagen no disponible")

    st.markdown("---")
