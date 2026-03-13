import streamlit as st
import pandas as pd
import smtplib
import ssl
import base64
from urllib.parse import quote
from email.message import EmailMessage
from fpdf import FPDF
from pathlib import Path

ARCHIVO_EXCEL = "PRUEBA_CLASIFICADO.xlsx"
CARPETA_IMAGENES = Path("imagenes")

EMAIL_REMITENTE = "jguzmanraya@gmail.com"
EMAIL_DESTINO = "jguzmanraya@gmail.com"
CONTRASENA_APP = "utjb tfrt oqis bzcg"
IVA = 0.21

FAMILIAS_ORDENADAS = [
    ("Químicos", 1, "🧪"),
    ("Celulosas", 2, "🧻"),
    ("Útiles", 3, "🧹"),
    ("Desechables", 4, "🗑️"),
    ("Equipamiento", 5, "⚙️"),
    ("Máquinas", 6, "🧽"),
    ("Otros", 7, "📦"),
    ("Servicios", 9, "🛠️"),
]

FAMILIAS = {nombre: {"id": fam_id, "icono": icono} for nombre, fam_id, icono in FAMILIAS_ORDENADAS}
FORMATOS = ["unidades", "cajas", "paquetes"]

class PedidoPDF(FPDF):
    def header(self):
        if Path("images.png").exists():
            self.image("images.png", 10, 8, 33)
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "APLYTEC - Resumen de Pedido", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Pagina " + str(self.page_no()), 0, 0, "C")

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

    if Path(adjunto_path).exists():
        with open(adjunto_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="resumen_pedido.pdf",
            )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_REMITENTE, CONTRASENA_APP)
        server.send_message(msg)

@st.cache_data
def cargar_datos():
    df = pd.read_excel(ARCHIVO_EXCEL)
    renombres = {}
    for col in df.columns:
        c = str(col).strip().upper()
        if c == "CÓDIGO":
            renombres[col] = "Código"
        elif c in ("NOMBRE", "DESCRIPCIÓN ARTÍCULO", "DESCRIPCION ARTICULO"):
            renombres[col] = "Nombre"
        elif c in ("PRECIO", "P.VENTA CON IVA0"):
            renombres[col] = "Precio"
        elif c == "FAMILIA":
            renombres[col] = "Familia"
        elif c == "SUBFAMILIA":
            renombres[col] = "Subfamilia"

    df = df.rename(columns=renombres)

    necesarios = ["Código", "Nombre", "Precio", "Familia", "Subfamilia"]
    for col in necesarios:
        if col not in df.columns:
            df[col] = ""

    df["Familia"] = df["Familia"].fillna("").astype(str).str.strip()
    df["Subfamilia"] = df["Subfamilia"].fillna("").astype(str).str.strip()
    df.loc[df["Subfamilia"] == "", "Subfamilia"] = "Otros"
    df["Precio"] = pd.to_numeric(df["Precio"], errors="coerce").fillna(0.0)
    df["Código"] = df["Código"].astype(str).str.strip()
    df["Nombre"] = df["Nombre"].astype(str).str.strip()

    familias_validas = set(FAMILIAS.keys())
    df["Familia"] = df["Familia"].apply(lambda x: x if x in familias_validas else "Otros")
    return df

def obtener_ruta_imagen_producto(codigo):
    for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        ruta = CARPETA_IMAGENES / f"{codigo}{ext}"
        if ruta.exists():
            return str(ruta)
    return None

def obtener_ruta_imagen_familia(nombre_familia):
    info = FAMILIAS.get(nombre_familia, {})
    fam_id = info.get("id")
    if fam_id is None:
        return None
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        ruta = CARPETA_IMAGENES / f"familia_{fam_id}{ext}"
        if ruta.exists():
            return ruta
    return None

def imagen_a_base64(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def agregar_o_sumar_al_carrito(codigo, nombre, tipo, precio_con_iva, cantidad=1):
    existente = None
    for item in st.session_state.carrito:
        if item["Código"] == codigo and item["Tipo"] == tipo:
            existente = item
            break
    if existente:
        existente["Cantidad"] += int(cantidad)
    else:
        st.session_state.carrito.append({
            "id": st.session_state.next_cart_id,
            "Código": codigo,
            "Nombre": nombre,
            "Cantidad": int(cantidad),
            "Tipo": tipo,
            "PrecioUnitario": float(precio_con_iva)
        })
        st.session_state.next_cart_id += 1


def cantidad_en_carrito(codigo, tipo):
    total = 0
    for item in st.session_state.carrito:
        if item["Código"] == codigo and item["Tipo"] == tipo:
            total += int(item["Cantidad"])
    return total


def quitar_del_carrito(codigo, tipo, cantidad=1):
    for i, item in enumerate(st.session_state.carrito):
        if item["Código"] == codigo and item["Tipo"] == tipo:
            item["Cantidad"] -= int(cantidad)
            if item["Cantidad"] <= 0:
                st.session_state.carrito.pop(i)
            return

if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "next_cart_id" not in st.session_state:
    st.session_state.next_cart_id = 1
if "familia_actual" not in st.session_state:
    st.session_state.familia_actual = None
if "subfamilia_actual" not in st.session_state:
    st.session_state.subfamilia_actual = None
if "pdf_generado" not in st.session_state:
    st.session_state.pdf_generado = False

qp = st.query_params
if qp.get("familia"):
    st.session_state.familia_actual = qp.get("familia")
if qp.get("subfamilia"):
    st.session_state.subfamilia_actual = qp.get("subfamilia")

st.set_page_config(page_title="Catálogo APLYTEC", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem;}
a.family-card {text-decoration:none !important; display:block;}
.family-wrap img {border-radius: 20px; box-shadow: 0 4px 16px rgba(0,0,0,.08);}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center'>
    <img src='https://raw.githubusercontent.com/APLYTEC/catalogo-online/main/images.png' width='150'/>
    <h1>APLYTEC</h1>
    <h3>Catálogo por familias</h3>
</div>
<hr>
""", unsafe_allow_html=True)

df = cargar_datos()

def volver_a_familias():
    st.session_state.familia_actual = None
    st.session_state.subfamilia_actual = None
    st.query_params.clear()

def volver_a_subfamilias():
    st.session_state.subfamilia_actual = None
    st.query_params.clear()
    st.query_params["familia"] = st.session_state.familia_actual

st.markdown("## Buscar producto")
busqueda_global = st.text_input("Busca por nombre o código sin entrar en familias")

if busqueda_global:
    resultados = df[
        df["Nombre"].str.contains(busqueda_global, case=False, na=False) |
        df["Código"].astype(str).str.contains(busqueda_global, case=False, na=False)
    ].copy()

    st.markdown(f"### Resultados: {len(resultados)}")
    for _, fila in resultados.iterrows():
        st.markdown("---")
        c1, c2 = st.columns([1, 2])

        with c1:
            ruta_img = obtener_ruta_imagen_producto(fila["Código"])
            if ruta_img:
                st.image(ruta_img, use_container_width=True)
            else:
                st.info("Sin imagen")

        with c2:
            st.markdown(f"### {fila['Nombre']}")
            precio_con_iva = float(fila["Precio"])
            precio_sin_iva = precio_con_iva / (1 + IVA) if precio_con_iva else 0
            st.markdown(
                f"**Código:** {fila['Código']}  \n"
                f"**Familia:** {fila['Familia']}  \n"
                f"**Subfamilia:** {fila['Subfamilia']}  \n"
                f"💶 **Precio sin IVA:** {precio_sin_iva:.2f} €  \n"
                f"💰 **Precio con IVA:** {precio_con_iva:.2f} €"
            )

            tipo = st.radio(
                "Formato",
                FORMATOS,
                horizontal=True,
                key=f"tipo_busq_{fila['Código']}",
                label_visibility="collapsed"
            )

            qty_actual = cantidad_en_carrito(fila["Código"], tipo)
            a1, a2, a3, a4 = st.columns([1, 1, 1.2, 2.2])
            with a1:
                if st.button("−", key=f"menos_busq_{fila['Código']}_{tipo}", use_container_width=True):
                    quitar_del_carrito(fila["Código"], tipo, 1)
                    st.rerun()
            with a2:
                if st.button("+", key=f"mas_busq_{fila['Código']}_{tipo}", use_container_width=True):
                    agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 1)
                    st.rerun()
            with a3:
                st.markdown(f"**En carrito:** {qty_actual}")
            with a4:
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("Añadir 1", key=f"add1_busq_{fila['Código']}_{tipo}", use_container_width=True):
                        agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 1)
                        st.rerun()
                with b2:
                    if st.button("Añadir 5", key=f"add5_busq_{fila['Código']}_{tipo}", use_container_width=True):
                        agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 5)
                        st.rerun()

if st.session_state.familia_actual is None and not busqueda_global:
    st.markdown("## Selecciona una familia")
    cols = st.columns(2)
    for i, (familia, fam_id, _icono) in enumerate(FAMILIAS_ORDENADAS):
        with cols[i % 2]:
            img = obtener_ruta_imagen_familia(familia)
            if img:
                img64 = imagen_a_base64(img)
                href = f"?familia={quote(familia)}"
                st.markdown(
                    f"""
                    <div class="family-wrap">
                        <a class="family-card" href="{href}">
                            <img src="data:image/png;base64,{img64}" style="width:100%;" />
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                if st.button(familia, key=f"btn_fam_{fam_id}", use_container_width=True):
                    st.session_state.familia_actual = familia
                    st.rerun()
    st.stop()

familia_actual = st.session_state.familia_actual

if familia_actual:
    top1, top2 = st.columns([1, 3])
    with top1:
        if st.button("⬅️ Familias", use_container_width=True):
            volver_a_familias()
            st.rerun()
    with top2:
        st.markdown(f"## {familia_actual}")

    if st.session_state.subfamilia_actual is None:
        subfamilias = (
            df[df["Familia"] == familia_actual]["Subfamilia"]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", "Otros")
            .unique()
            .tolist()
        )
        subfamilias = sorted(subfamilias)
        st.markdown("### Selecciona una subfamilia")
        cols = st.columns(3)
        for i, sub in enumerate(subfamilias):
            with cols[i % 3]:
                if st.button(sub, key=f"btn_sub_{sub}", use_container_width=True):
                    st.session_state.subfamilia_actual = sub
                    st.query_params["familia"] = familia_actual
                    st.query_params["subfamilia"] = sub
                    st.rerun()
        st.stop()

subfamilia_actual = st.session_state.subfamilia_actual

if familia_actual and subfamilia_actual:
    nav1, nav2, nav3 = st.columns([1, 1, 3])
    with nav1:
        if st.button("⬅️ Subfamilias", use_container_width=True):
            volver_a_subfamilias()
            st.rerun()
    with nav2:
        if st.button("🏠 Familias", use_container_width=True):
            volver_a_familias()
            st.rerun()
    with nav3:
        st.markdown(f"### {familia_actual} / {subfamilia_actual}")

    productos = df[(df["Familia"] == familia_actual) & (df["Subfamilia"] == subfamilia_actual)].copy()

    busqueda = st.text_input("Buscar dentro de esta subfamilia")
    if busqueda:
        productos = productos[
            productos["Nombre"].str.contains(busqueda, case=False, na=False) |
            productos["Código"].astype(str).str.contains(busqueda, case=False, na=False)
        ]

    for _, fila in productos.iterrows():
        st.markdown("---")
        c1, c2 = st.columns([1, 2])

        with c1:
            ruta_img = obtener_ruta_imagen_producto(fila["Código"])
            if ruta_img:
                st.image(ruta_img, use_container_width=True)
            else:
                st.info("Sin imagen")

        with c2:
            st.markdown(f"### {fila['Nombre']}")
            precio_con_iva = float(fila["Precio"])
            precio_sin_iva = precio_con_iva / (1 + IVA) if precio_con_iva else 0
            st.markdown(
                f"**Código:** {fila['Código']}  \n"
                f"💶 **Precio sin IVA:** {precio_sin_iva:.2f} €  \n"
                f"💰 **Precio con IVA:** {precio_con_iva:.2f} €"
            )

            tipo = st.radio(
                "Formato",
                FORMATOS,
                horizontal=True,
                key=f"tipo_{fila['Código']}",
                label_visibility="collapsed"
            )

            qty_actual = cantidad_en_carrito(fila["Código"], tipo)
            a1, a2, a3, a4 = st.columns([1, 1, 1.2, 2.2])
            with a1:
                if st.button("−", key=f"menos_{fila['Código']}_{tipo}", use_container_width=True):
                    quitar_del_carrito(fila["Código"], tipo, 1)
                    st.rerun()
            with a2:
                if st.button("+", key=f"mas_{fila['Código']}_{tipo}", use_container_width=True):
                    agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 1)
                    st.rerun()
            with a3:
                st.markdown(f"**En carrito:** {qty_actual}")
            with a4:
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("Añadir 1", key=f"add1_{fila['Código']}_{tipo}", use_container_width=True):
                        agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 1)
                        st.rerun()
                with b2:
                    if st.button("Añadir 5", key=f"add5_{fila['Código']}_{tipo}", use_container_width=True):
                        agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 5)
                        st.rerun()

st.markdown("---")
st.markdown("## 🛒 Resumen del pedido")
ruta_pdf = "resumen_pedido.pdf"

if st.session_state.carrito:
    total = 0.0
    resumen = ""
    nuevo_carrito = []
    borrado = False

    for item in st.session_state.carrito:
        s1, s2, s3, s4, s5 = st.columns([3, 1, 1, 1.2, 0.8])

        with s1:
            st.markdown(f"**{item['Nombre']}**  \nCódigo: {item['Código']}")
        with s2:
            nueva_cantidad = st.number_input(
                f"Cantidad carrito {item['id']}",
                min_value=1,
                max_value=1000,
                value=int(item["Cantidad"]),
                key=f"cart_qty_{item['id']}",
                label_visibility="collapsed"
            )
        with s3:
            nuevo_tipo = st.selectbox(
                f"Formato carrito {item['id']}",
                FORMATOS,
                index=FORMATOS.index(item["Tipo"]) if item["Tipo"] in FORMATOS else 0,
                key=f"cart_tipo_{item['id']}",
                label_visibility="collapsed"
            )
        with s4:
            subtotal = float(nueva_cantidad) * float(item["PrecioUnitario"])
            st.write(f"{subtotal:.2f} €")
        with s5:
            borrar = st.button("❌", key=f"delete_{item['id']}", use_container_width=True)

        if not borrar:
            item["Cantidad"] = int(nueva_cantidad)
            item["Tipo"] = nuevo_tipo
            nuevo_carrito.append(item)
            total += subtotal
            resumen += f"- {item['Cantidad']} {item['Tipo']} de {item['Nombre']} (Codigo: {item['Código']}) -> {subtotal:.2f} euros\n"
        else:
            borrado = True

        st.markdown("---")

    if nuevo_carrito != st.session_state.carrito or borrado:
        st.session_state.carrito = nuevo_carrito

    st.markdown(f"### Total: {total:.2f} euros (IVA incluido)")

    with st.form("form_pedido"):
        nombre = st.text_input("Tu nombre")
        comentarios = st.text_area("Comentarios adicionales (opcional)")
        enviar = st.form_submit_button("📨 Enviar pedido")

        if enviar:
            resumen_txt = f"Pedido enviado por: {nombre}\n\n{resumen}\nTotal: {total:.2f} euros (IVA incluido)\n\nComentarios: {comentarios}"
            generar_pdf(nombre, resumen, total, comentarios, ruta_pdf)
            enviar_pedido_por_email("Nuevo pedido de catálogo", resumen_txt, ruta_pdf)
            st.success("✅ Pedido enviado correctamente")
            st.session_state.pdf_generado = True
            st.session_state.carrito = []

    b1, b2 = st.columns(2)
    with b1:
        if st.session_state.pdf_generado and Path(ruta_pdf).exists():
            with open(ruta_pdf, "rb") as f:
                st.download_button("📄 Descargar resumen en PDF", f, file_name="resumen_pedido.pdf", use_container_width=True)
    with b2:
        if st.button("🗑️ Vaciar carrito", use_container_width=True):
            st.session_state.carrito = []
            st.session_state.pdf_generado = False
            st.warning("Carrito vaciado")
else:
    st.info("No hay productos en el pedido.")
