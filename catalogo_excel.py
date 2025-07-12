
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

# CABECERA
st.markdown("""
<div style='text-align: center'>
    <img src='https://raw.githubusercontent.com/APLYTEC/catalogo-online/main/images.png' width='150'/>
    <h1>APLYTEC</h1>
    <h3>Tarifas de productos</h3>
</div>
<hr>
""", unsafe_allow_html=True)

df = cargar_datos()

# Inicializar el carrito
if "carrito" not in st.session_state:
    st.session_state.carrito = []

# Búsqueda
busqueda = st.text_input("Buscar producto")
if busqueda:
    df_filtrado = df[df["Nombre"].str.contains(busqueda, case=False, na=False) | df["Código"].astype(str).str.contains(busqueda)]
else:
    df_filtrado = df

# Paginación
productos_por_pagina = 10
total_productos = len(df_filtrado)
total_paginas = (total_productos - 1) // productos_por_pagina + 1

if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = 1

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️ Anterior", key="prev"):
        if st.session_state.pagina_actual > 1:
            st.session_state.pagina_actual -= 1
with col3:
    if st.button("Siguiente ➡️", key="next"):
        if st.session_state.pagina_actual < total_paginas:
            st.session_state.pagina_actual += 1

inicio = (st.session_state.pagina_actual - 1) * productos_por_pagina
fin = inicio + productos_por_pagina
pagina_df = df_filtrado.iloc[inicio:fin]

st.markdown(f"<div style='text-align: center'><strong>Página {st.session_state.pagina_actual} de {total_paginas}</strong></div>", unsafe_allow_html=True)

# Mostrar productos
for _, fila in pagina_df.iterrows():
    st.markdown(f"### {fila['Nombre']}")
    precio = float(fila['Precio'])
    st.markdown(f"**Código:** {fila['Código']} &nbsp;&nbsp;&nbsp; **Precio:** {precio:.2f} €")
    ruta_imagen = obtener_ruta_imagen(fila["Código"])
    if ruta_imagen:
        st.image(ruta_imagen, use_container_width=True)
    else:
        st.warning("Imagen no disponible")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        cantidad = st.number_input(f"Cantidad ({fila['Código']})", min_value=1, max_value=1000, value=1, key=f"cantidad_{fila['Código']}")
    with col2:
        tipo = st.selectbox("Formato", ["unidades", "cajas"], key=f"tipo_{fila['Código']}")
    with col3:
        if st.button("➕ Agregar al pedido", key=f"add_{fila['Código']}"):
            st.session_state.carrito.append({
                "Código": fila["Código"],
                "Nombre": fila["Nombre"],
                "Cantidad": cantidad,
                "Tipo": tipo,
                "PrecioUnitario": precio
            })
            st.success(f"{cantidad} {tipo} de '{fila['Nombre']}' añadido al pedido.")
    st.markdown("---")

# Mostrar carrito
st.markdown("## 🛒 Resumen del pedido")
if st.session_state.carrito:
    total = 0
    for item in st.session_state.carrito:
        subtotal = item["Cantidad"] * item["PrecioUnitario"]
        total += subtotal
        st.markdown(f"- {item['Cantidad']} {item['Tipo']} de **{item['Nombre']}** → {subtotal:.2f} €")
    st.markdown(f"### Total: {total:.2f} €")
    if st.button("🗑️ Vaciar pedido"):
        st.session_state.carrito = []
        st.warning("Pedido vaciado.")
else:
    st.info("No hay productos en el pedido aún.")
