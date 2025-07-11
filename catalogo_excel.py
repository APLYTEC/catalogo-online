
import streamlit as st
import pandas as pd
import os
from PIL import Image

# Título de la app
st.set_page_config(page_title="Catálogo de Productos", layout="wide")
st.title("📦 Catálogo de Productos")

# Cargar datos desde el Excel
@st.cache_data
def cargar_datos():
    df = pd.read_excel("PRUEBA.xlsx")
    df = df[["CÓDIGO", "NOMBRE", "PRECIO"]]
    df = df.rename(columns={"CÓDIGO": "Código", "NOMBRE": "Nombre", "PRECIO": "Precio"})
    return df

df = cargar_datos()

# Barra de búsqueda
busqueda = st.text_input("🔍 Buscar por nombre o código:")

# Filtrar resultados
if busqueda:
    df_filtrado = df[df["Nombre"].str.contains(busqueda, case=False, na=False) | 
                     df["Código"].astype(str).str.contains(busqueda)]
else:
    df_filtrado = df

# Mostrar productos
for _, fila in df_filtrado.iterrows():
    col1, col2 = st.columns([1, 3])
    with col1:
        imagen_path = os.path.join("imagenes", f"{fila['Código']}.jpg")
        if not os.path.exists(imagen_path):  # probar también con .jpeg
            imagen_path = os.path.join("imagenes", f"{fila['Código']}.jpeg")
        if os.path.exists(imagen_path):
            st.image(Image.open(imagen_path), use_column_width=True)
        else:
            st.warning("Imagen no encontrada")
    with col2:
        st.subheader(fila["Nombre"])
        st.write(f"**Código:** {fila['Código']}")
        st.write(f"**Precio:** {fila['Precio']} €")
    st.markdown("---")
