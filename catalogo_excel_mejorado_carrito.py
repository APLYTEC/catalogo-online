import streamlit as st
import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage
from fpdf import FPDF
from pathlib import Path

EMAIL_REMITENTE = "jguzmanraya@gmail.com"
EMAIL_DESTINO = "jguzmanraya@gmail.com"
CONTRASENA_APP = "utjb tfrt oqis bzcg"
IVA = 0.21

class PedidoPDF(FPDF):
    def header(self):
        self.image("images.png", 10, 8, 33)
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "APLYTEC - Resumen de Pedido", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Página " + str(self.page_no()), 0, 0, "C")

def generar_pdf(nombre, resumen, total, comentarios, output_path):
    pdf = PedidoPDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Comercial: {nombre}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, resumen)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Total del pedido: {total:.2f} euros (IVA incluido)", ln=True)
    if comentarios:
        pdf.ln(10)
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 10, f"Comentarios: {comentarios}")
    pdf.output(output_path)

def enviar_pedido_por_email(asunto, cuerpo, adjunto_path):
    msg = EmailMessage()
    msg["From"] = EMAIL_REMITENTE
    msg["To"] = EMAIL_DESTINO
    msg["Subject"] = asunto
    msg.set_content(cuerpo)

    with open(adjunto_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="resumen_pedido.pdf")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_REMITENTE, CONTRASENA_APP)
        server.send_message(msg)

@st.cache_data
def cargar_datos():
    df = pd.read_excel("PRUEBA.xlsx")
    df = df.rename(columns={"CÓDIGO": "Código", "NOMBRE": "Nombre", "PRECIO": "Precio"})
    return df

def obtener_ruta_imagen(codigo):
    for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        ruta = Path("imagenes") / f"{codigo}{ext}"
        if ruta.exists():
            return str(ruta)
    return None

st.markdown("""
<div style='text-align: center'>
    <img src='https://raw.githubusercontent.com/APLYTEC/catalogo-online/main/images.png' width='150'/>
    <h1>APLYTEC</h1>
    <h3>Tarifas de productos</h3>
</div>
<hr>
""", unsafe_allow_html=True)

df = cargar_datos()

if "carrito" not in st.session_state:
    st.session_state.carrito = []

if "next_cart_id" not in st.session_state:
    st.session_state.next_cart_id = 1

if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = 1

if "pdf_generado" not in st.session_state:
    st.session_state.pdf_generado = False

busqueda = st.text_input("Buscar producto")
if busqueda:
    df_filtrado = df[df["Nombre"].str.contains(busqueda, case=False, na=False) | df["Código"].astype(str).str.contains(busqueda)]
else:
    df_filtrado = df

productos_pagina = 10
total_paginas = (len(df_filtrado) - 1) // productos_pagina + 1
inicio = (st.session_state.pagina_actual - 1) * productos_pagina
fin = inicio + productos_pagina
pagina_df = df_filtrado.iloc[inicio:fin]

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️ Anterior", key="prev_page"):
        if st.session_state.pagina_actual > 1:
            st.session_state.pagina_actual -= 1
with col3:
    if st.button("Siguiente ➡️", key="next_page"):
        if st.session_state.pagina_actual < total_paginas:
            st.session_state.pagina_actual += 1

st.markdown(f"<div style='text-align: center'><strong>Página {st.session_state.pagina_actual} de {total_paginas}</strong></div>", unsafe_allow_html=True)

for _, fila in pagina_df.iterrows():
    st.markdown(f"### {fila['Nombre']}")
    precio_con_iva = float(fila['Precio'])
    precio_sin_iva = precio_con_iva / (1 + IVA)
    st.markdown(f"**Código:** {fila['Código']}<br>💶 Precio sin IVA: {precio_sin_iva:.2f} €<br>💰 Precio con IVA: {precio_con_iva:.2f} €", unsafe_allow_html=True)
    ruta_img = obtener_ruta_imagen(fila["Código"])
    if ruta_img:
        st.image(ruta_img, use_container_width=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        cantidad = st.number_input(
            f"Cantidad ({fila['Código']})",
            min_value=1,
            max_value=1000,
            value=1,
            key=f"cantidad_{fila['Código']}"
        )
    with col2:
        tipo = st.selectbox("Formato", ["unidades", "cajas", "paquetes"], key=f"tipo_{fila['Código']}")
    with col3:
        if st.button("➕ Agregar al pedido", key=f"add_{fila['Código']}"):
            st.session_state.carrito.append({
                "id": st.session_state.next_cart_id,
                "Código": fila["Código"],
                "Nombre": fila["Nombre"],
                "Cantidad": int(cantidad),
                "Tipo": tipo,
                "PrecioUnitario": precio_con_iva
            })
            st.session_state.next_cart_id += 1
            st.success(f"{cantidad} {tipo} de '{fila['Nombre']}' añadido al pedido.")
    st.markdown("---")

down1, down2, down3 = st.columns([1, 2, 1])
with down1:
    if st.button("⬅️ Anterior", key="prev_page_bottom"):
        if st.session_state.pagina_actual > 1:
            st.session_state.pagina_actual -= 1
with down3:
    if st.button("Siguiente ➡️", key="next_page_bottom"):
        if st.session_state.pagina_actual < total_paginas:
            st.session_state.pagina_actual += 1

st.markdown("## 🛒 Resumen del pedido")
ruta_pdf = "resumen_pedido.pdf"

if st.session_state.carrito:
    total = 0
    resumen = ""
    carrito_actualizado = []
    hay_cambios = False

    for item in st.session_state.carrito:
        st.markdown(f"**{item['Nombre']}**")
        c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1])

        with c1:
            nueva_cantidad = st.number_input(
                f"Cantidad carrito {item['id']}",
                min_value=1,
                max_value=1000,
                value=int(item["Cantidad"]),
                key=f"cart_qty_{item['id']}",
                label_visibility="collapsed"
            )
        with c2:
            st.write(item["Tipo"])
        with c3:
            subtotal = nueva_cantidad * item["PrecioUnitario"]
            st.write(f"{subtotal:.2f} €")
        with c4:
            borrar = st.button("❌", key=f"delete_{item['id']}")

        if not borrar:
            item["Cantidad"] = int(nueva_cantidad)
            carrito_actualizado.append(item)
            total += subtotal
            linea = f"- {item['Cantidad']} {item['Tipo']} de {item['Nombre']} (Codigo: {item['Código']}) -> {subtotal:.2f} euros\n"
            resumen += linea
        else:
            hay_cambios = True

        st.markdown("---")

    if carrito_actualizado != st.session_state.carrito or hay_cambios:
        st.session_state.carrito = carrito_actualizado

    st.markdown(f"### Total: {total:.2f} euros (IVA incluido)")

    st.markdown("## ✉️ Enviar pedido")
    with st.form("form_pedido"):
        nombre = st.text_input("Tu nombre")
        comentarios = st.text_area("Comentarios adicionales (opcional)")
        enviado = st.form_submit_button("📨 Enviar pedido")
        if enviado:
            resumen_txt = f"Pedido enviado por: {nombre}\n\n{resumen}\nTotal: {total:.2f} euros (IVA incluido)\n\nComentarios: {comentarios}"
            generar_pdf(nombre, resumen, total, comentarios, ruta_pdf)
            enviar_pedido_por_email("Nuevo pedido de catálogo", resumen_txt, ruta_pdf)
            st.success("✅ Pedido enviado correctamente.")
            st.session_state.pdf_generado = True
            st.session_state.carrito = []

    if st.session_state.pdf_generado and Path(ruta_pdf).exists():
        with open(ruta_pdf, "rb") as f:
            st.download_button("📄 Descargar resumen en PDF", f, file_name="resumen_pedido.pdf")

    if st.button("🗑️ Borrar pedido completo"):
        st.session_state.carrito = []
        st.session_state.pdf_generado = False
        st.warning("El pedido ha sido borrado.")
else:
    st.info("No hay productos en el pedido.")
