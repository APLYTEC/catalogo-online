
import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data
def cargar_datos():
    df = pd.read_excel("PRUEBA.xlsx")
    df = df.rename(columns={
        "CÓDIGO": "Código",
        "NOMBRE": "Nombre",
        "PRECIO": "Precio"
    })
    return df

def obtener_ruta_imagen(codigo):
    extensiones = [".jpg", ".jpeg", ".png"]
    for ext in extensiones:
        ruta = Path("imagenes") / f"{codigo}{ext}"
        if ruta.exists():
            return str(ruta)
    return None

# CABECERA CON LOGO DESDE GITHUB
st.markdown("""
<div style='text-align: center'>
    <img src='https://raw.githubusercontent.com/APLYTEC/catalogo-online/main/images.png' width='150'/>
    <h1>APLYTEC</h1>
    <h3>Tarifas de productos</h3>
</div>
<hr>
""", unsafe_allow_html=True)

df = cargar_datos()

# Búsqueda
busqueda = st.text_input("Buscar producto")
if busqueda:
    df_filtrado = df[df["Nombre"].str.contains(busqueda, case=False, na=False) | df["Código"].astype(str).str.contains(busqueda)]
else:
    df_filtrado = df

# Paginación
productos_por_pagina = 20
total_productos = len(df_filtrado)
total_paginas = (total_productos - 1) // productos_por_pagina + 1

if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = 1

def mostrar_controles_paginacion():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Anterior"):
            if st.session_state.pagina_actual > 1:
                st.session_state.pagina_actual -= 1
    with col3:
        if st.button("Siguiente ➡️"):
            if st.session_state.pagina_actual < total_paginas:
                st.session_state.pagina_actual += 1
    st.markdown(f"<div style='text-align: center'><strong>Página {st.session_state.pagina_actual} de {total_paginas}</strong></div>", unsafe_allow_html=True)

# Controles de navegación - parte superior
mostrar_controles_paginacion()

# Productos de la página actual
inicio = (st.session_state.pagina_actual - 1) * productos_por_pagina
fin = inicio + productos_por_pagina
pagina_df = df_filtrado.iloc[inicio:fin]

for _, fila in pagina_df.iterrows():
    st.markdown(f"### {fila['Nombre']}")
    precio = float(fila['Precio'])
    st.markdown(f"**Código:** {fila['Código']} &nbsp;&nbsp;&nbsp; **Precio:** {precio:.2f} €")
    ruta_imagen = obtener_ruta_imagen(fila["Código"])
    if ruta_imagen:
        st.image(ruta_imagen, use_container_width=True)
    else:
        st.warning("Imagen no disponible")
    st.markdown("---")

# Controles de navegación - parte inferior
mostrar_controles_paginacion()
