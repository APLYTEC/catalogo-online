import streamlit as st
import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage
from fpdf import FPDF
from pathlib import Path

# =========================
# CONFIGURACIÓN
# =========================
ARCHIVO_EXCEL = "PRUEBA_CLASIFICADO.xlsx"
CARPETA_IMAGENES = Path("imagenes")

EMAIL_REMITENTE = "jguzmanraya@gmail.com"
EMAIL_DESTINO = "jguzmanraya@gmail.com"
CONTRASENA_APP = "utjb tfrt oqis bzcg"
IVA = 0.21

FAMILIAS = {
    "Químicos": {"id": 1, "icono": "🧪"},
    "Celulosas": {"id": 2, "icono": "🧻"},
    "Útiles": {"id": 3, "icono": "🧹"},
    "Desechables": {"id": 4, "icono": "🗑️"},
    "Equipamiento": {"id": 5, "icono": "⚙️"},
    "Máquinas": {"id": 6, "icono": "🚚"},
    "Alquiler": {"id": 7, "icono": "📦"},
    "Servicios": {"id": 9, "icono": "🛠️"},
}

FORMATOS = ["unidades", "cajas", "paquetes"]

# =========================
# PDF
# =========================
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

# =========================
# DATOS
# =========================
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

    df["Familia"] = df["Familia"].fillna("Sin familia").astype(str).str.strip()
    df["Subfamilia"] = df["Subfamilia"].fillna("").astype(str).str.strip()
    df.loc[df["Subfamilia"] == "", "Subfamilia"] = "Otros"
    df["Precio"] = pd.to_numeric(df["Precio"], errors="coerce").fillna(0.0)
    df["Código"] = df["Código"].astype(str).str.strip()
    df["Nombre"] = df["Nombre"].astype(str).str.strip()
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
    candidatos = []
    if fam_id is not None:
        candidatos += [
            CARPETA_IMAGENES / f"familia_{fam_id}.png",
            CARPETA_IMAGENES / f"familia_{fam_id}.jpg",
            CARPETA_IMAGENES / f"familia_{fam_id}.jpeg",
            CARPETA_IMAGENES / f"familia_{fam_id}.webp",
        ]
    slug = (
        nombre_familia.lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    candidatos += [
        CARPETA_IMAGENES / f"{slug}.png",
        CARPETA_IMAGENES / f"{slug}.jpg",
        CARPETA_IMAGENES / f"{slug}.jpeg",
        CARPETA_IMAGENES / f"{slug}.webp",
    ]
    for ruta in candidatos:
        if ruta.exists():
            return str(ruta)
    return None

# =========================
# ESTADO
# =========================
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

# =========================
# UI BASE
# =========================
st.set_page_config(page_title="Catálogo APLYTEC", layout="wide")

st.markdown("""
<div style='text-align: center'>
    <img src='https://raw.githubusercontent.com/APLYTEC/catalogo-online/main/images.png' width='150'/>
    <h1>APLYTEC</h1>
    <h3>Catálogo por familias</h3>
</div>
<hr>
""", unsafe_allow_html=True)

df = cargar_datos()

# =========================
# NAVEGACIÓN
# =========================
def volver_a_familias():
    st.session_state.familia_actual = None
    st.session_state.subfamilia_actual = None

def volver_a_subfamilias():
    st.session_state.subfamilia_actual = None

# Pantalla familias
if st.session_state.familia_actual is None:
    st.markdown("## Selecciona una familia")
    familias_disponibles = [f for f in df["Familia"].dropna().unique().tolist() if str(f).strip()]

    cols = st.columns(2)
    for i, familia in enumerate(sorted(familias_disponibles)):
        with cols[i % 2]:
            img = obtener_ruta_imagen_familia(familia)
            if img:
                st.image(img, use_container_width=True)
                label = familia
            else:
                icono = FAMILIAS.get(familia, {}).get("icono", "📁")
                label = f"{icono} {familia}"

            if st.button(label, key=f"btn_fam_{familia}", use_container_width=True):
                st.session_state.familia_actual = familia
                st.rerun()

    st.stop()

familia_actual = st.session_state.familia_actual

top1, top2 = st.columns([1, 3])
with top1:
    if st.button("⬅️ Familias", use_container_width=True):
        volver_a_familias()
        st.rerun()
with top2:
    st.markdown(f"## {familia_actual}")

# Pantalla subfamilias
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
                st.rerun()
    st.stop()

subfamilia_actual = st.session_state.subfamilia_actual

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

productos = df[
    (df["Familia"] == familia_actual) &
    (df["Subfamilia"] == subfamilia_actual)
].copy()

busqueda = st.text_input("Buscar dentro de esta subfamilia")
if busqueda:
    productos = productos[
        productos["Nombre"].str.contains(busqueda, case=False, na=False) |
        productos["Código"].astype(str).str.contains(busqueda, case=False, na=False)
    ]

# =========================
# PRODUCTOS
# =========================
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

        a1, a2, a3 = st.columns([1, 1, 1.4])
        with a1:
            cantidad = st.number_input(
                f"Cantidad {fila['Código']}",
                min_value=1,
                max_value=1000,
                value=1,
                key=f"cantidad_{fila['Código']}"
            )
        with a2:
            tipo = st.selectbox(
                "Formato",
                FORMATOS,
                key=f"tipo_{fila['Código']}"
            )
        with a3:
            if st.button("➕ Añadir al pedido", key=f"add_{fila['Código']}", use_container_width=True):
                existente = None
                for item in st.session_state.carrito:
                    if item["Código"] == fila["Código"] and item["Tipo"] == tipo:
                        existente = item
                        break

                if existente:
                    existente["Cantidad"] += int(cantidad)
                else:
                    st.session_state.carrito.append({
                        "id": st.session_state.next_cart_id,
                        "Código": fila["Código"],
                        "Nombre": fila["Nombre"],
                        "Cantidad": int(cantidad),
                        "Tipo": tipo,
                        "PrecioUnitario": precio_con_iva
                    })
                    st.session_state.next_cart_id += 1

                st.success("Artículo añadido al pedido")

# =========================
# CARRITO
# =========================
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
            resumen += (
                f"- {item['Cantidad']} {item['Tipo']} de {item['Nombre']} "
                f"(Codigo: {item['Código']}) -> {subtotal:.2f} euros\n"
            )
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
            resumen_txt = (
                f"Pedido enviado por: {nombre}\n\n"
                f"{resumen}\n"
                f"Total: {total:.2f} euros (IVA incluido)\n\n"
                f"Comentarios: {comentarios}"
            )
            generar_pdf(nombre, resumen, total, comentarios, ruta_pdf)
            enviar_pedido_por_email("Nuevo pedido de catálogo", resumen_txt, ruta_pdf)
            st.success("✅ Pedido enviado correctamente")
            st.session_state.pdf_generado = True
            st.session_state.carrito = []

    b1, b2 = st.columns(2)
    with b1:
        if st.session_state.pdf_generado and Path(ruta_pdf).exists():
            with open(ruta_pdf, "rb") as f:
                st.download_button(
                    "📄 Descargar resumen en PDF",
                    f,
                    file_name="resumen_pedido.pdf",
                    use_container_width=True
                )
    with b2:
        if st.button("🗑️ Vaciar carrito", use_container_width=True):
            st.session_state.carrito = []
            st.session_state.pdf_generado = False
            st.warning("Carrito vaciado")
else:
    st.info("No hay productos en el pedido.")
