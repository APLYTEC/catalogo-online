import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import smtplib
import ssl
import base64
import json
from urllib.parse import quote, unquote
from email.message import EmailMessage
from fpdf import FPDF
from pathlib import Path

ARCHIVO_EXCEL = "PRUEBA_CLASIFICADO.xlsx"
CARPETA_IMAGENES = Path("imagenes")

EMAIL_REMITENTE = "jguzmanraya@gmail.com"
EMAIL_DESTINO = "jguzmanraya@gmail.com"
CONTRASENA_APP = "utjb tfrt oqis bzcg"
IVA = 0.21
WHATSAPP_NUMERO = "+34647936356"
WHATSAPP_LINK = "https://wa.me/34647936356"
LOGO_LOCAL = Path("aplytec_logo_upscaled_16x.png")
LOGO_FALLBACK = "https://raw.githubusercontent.com/APLYTEC/catalogo-online/main/images.png"
APLY_SALUDA = CARPETA_IMAGENES / "aply_saludando.png"
APLY_SENALA = CARPETA_IMAGENES / "aply_senalando.png"
APLY_CARRITO = CARPETA_IMAGENES / "aply_carrito.png"
APLY_MOVIL = CARPETA_IMAGENES / "aply_movil.png"

QUIMICOS_SUBFAMILIAS_ORDENADAS = [
    ("Lavavajillas", "sub_quimicos_lavavajillas.png"),
    ("Desengrasantes", "sub_quimicos_desengrasantes.png"),
    ("Suelos y superficies", "sub_quimicos_suelos_superficies.png"),
    ("Baños y sanitarios", "sub_quimicos_banos_sanitarios.png"),
    ("Desinfección", "sub_quimicos_desinfeccion.png"),
    ("Lavandería", "sub_quimicos_lavanderia.png"),
    ("Ambientadores", "sub_quimicos_ambientadores.png"),
    ("Aseo personal", "sub_quimicos_aseo_personal.png"),
]

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
    pdf.cell(0, 10, f"Cliente: {nombre}", ln=True)
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




def obtener_ruta_imagen_subfamilia_quimicos(subfamilia):
    mapa = {
        "Lavavajillas": "sub_quimicos_lavavajillas",
        "Desengrasantes": "sub_quimicos_desengrasantes",
        "Suelos y superficies": "sub_quimicos_suelos_superficies",
        "Baños y sanitarios": "sub_quimicos_banos_sanitarios",
        "Desinfección": "sub_quimicos_desinfeccion",
        "Lavandería": "sub_quimicos_lavanderia",
        "Ambientadores": "sub_quimicos_ambientadores",
        "Aseo personal": "sub_quimicos_aseo_personal",
    }
    nombre = mapa.get(str(subfamilia).strip())
    if not nombre:
        return None
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        ruta = CARPETA_IMAGENES / f"{nombre}{ext}"
        if ruta.exists():
            return ruta
    return None

def _mtime_seguro(ruta):
    try:
        return Path(ruta).stat().st_mtime
    except Exception:
        return 0


@st.cache_data(show_spinner=False)
def imagen_a_base64_cacheada(ruta_str, mtime):
    with open(ruta_str, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def imagen_a_base64(ruta):
    ruta = Path(ruta)
    return imagen_a_base64_cacheada(str(ruta), _mtime_seguro(ruta))


def imagen_data_uri(ruta):
    if not ruta:
        return None
    ruta = Path(ruta)
    ext = ruta.suffix.lower().replace('.', '') or 'png'
    if ext == 'jpg':
        ext = 'jpeg'
    return f"data:image/{ext};base64,{imagen_a_base64(ruta)}"


def serializar_carrito_para_qp():
    """Devuelve JSON sin pre-codificar.

    Streamlit ya codifica los valores al escribir st.query_params. Si se hace
    quote() aquí también, el carrito queda doblemente codificado y no puede
    restaurarse correctamente después de refrescar la página.
    """
    try:
        data = [{
            "id": int(item.get("id", 0)),
            "Código": str(item.get("Código", "")),
            "Nombre": str(item.get("Nombre", "")),
            "Cantidad": int(item.get("Cantidad", 0)),
            "Tipo": str(item.get("Tipo", "")),
            "PrecioUnitario": float(item.get("PrecioUnitario", 0.0)),
        } for item in st.session_state.carrito]
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        return ""


def restaurar_carrito_desde_qp(valor):
    if not valor:
        return []
    try:
        # Compatibilidad con URLs generadas por versiones anteriores:
        # intentamos JSON directo y, si hace falta, hasta dos decodificaciones.
        candidatos = [str(valor)]
        candidatos.append(unquote(candidatos[-1]))
        candidatos.append(unquote(candidatos[-1]))
        data = None
        for candidato in candidatos:
            try:
                data = json.loads(candidato)
                break
            except Exception:
                continue
        if data is None:
            return []

        carrito = []
        for item in data:
            carrito.append({
                "id": int(item.get("id", 0)),
                "Código": str(item.get("Código", "")),
                "Nombre": str(item.get("Nombre", "")),
                "Cantidad": int(item.get("Cantidad", 0)),
                "Tipo": str(item.get("Tipo", "")),
                "PrecioUnitario": float(item.get("PrecioUnitario", 0.0)),
            })
        return carrito
    except Exception:
        return []


def sync_query_params():
    params = {"pantalla": st.session_state.pantalla_actual}
    if st.session_state.familia_actual:
        params["familia"] = st.session_state.familia_actual
    if st.session_state.subfamilia_actual:
        params["subfamilia"] = st.session_state.subfamilia_actual
    cart = serializar_carrito_para_qp()
    if cart:
        params["cart"] = cart
    st.query_params.clear()
    st.query_params.update(params)


def qp_url(pantalla=None, familia=None, subfamilia=None):
    pantalla = pantalla or st.session_state.pantalla_actual or "catalogo"
    parts = [f"pantalla={quote(str(pantalla), safe='')}"]
    if familia:
        parts.append(f"familia={quote(str(familia), safe='')}")
    if subfamilia:
        parts.append(f"subfamilia={quote(str(subfamilia), safe='')}")
    cart = serializar_carrito_para_qp()
    if cart:
        parts.append(f"cart={quote(cart, safe='')}")
    return "?" + "&".join(parts)


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
    sync_query_params()


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
            sync_query_params()
            return
    sync_query_params()


def total_items_carrito():
    return sum(int(item["Cantidad"]) for item in st.session_state.carrito)


def total_importe_carrito():
    return sum(float(item["Cantidad"]) * float(item["PrecioUnitario"]) for item in st.session_state.carrito)


def render_boton_carrito_flotante():
    total_items = total_items_carrito()
    total_importe = total_importe_carrito()
    href = qp_url(pantalla="carrito")

    st.markdown(
        f"""
        <style>
        .aply-cart-floating-link {{
            position: fixed;
            top: 4.15rem;
            right: 0.65rem;
            z-index: 99999;
            width: 170px;
            text-decoration:none !important;
        }}
        .aply-cart-floating-chip {{
            width:100%;
            border-radius:999px;
            background: linear-gradient(135deg, #355e2b 0%, #4f8a3d 100%);
            color: white;
            border: 1px solid rgba(255,255,255,.18);
            box-shadow: 0 12px 26px rgba(53,94,43,.28);
            font-weight: 800;
            padding: .72rem .85rem;
            text-align:center;
            line-height:1.1;
        }}
        @media (max-width: 768px) {{
            .aply-cart-floating-link {{ top: 4.0rem; right: 0.5rem; width: 150px; }}
            .aply-cart-floating-chip {{ padding: .62rem .72rem; font-size: .92rem; }}
        }}
        </style>
        <a class="aply-cart-floating-link" href="{href}">
            <div class="aply-cart-floating-chip">🛒 {total_importe:.2f} € ({total_items})</div>
        </a>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def obtener_logo_src():
    if LOGO_LOCAL.exists():
        return imagen_data_uri(LOGO_LOCAL)
    if Path("images.png").exists():
        return imagen_data_uri(Path("images.png"))
    return LOGO_FALLBACK


def render_aply(ruta, mensaje, altura=240):
    if not ruta.exists():
        st.info(mensaje)
        return

    img64 = imagen_a_base64(ruta)
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#f8fbf8 0%,#eef7eb 100%);border:1px solid #d9ead3;border-radius:22px;padding:1rem;text-align:center;box-shadow:0 8px 20px rgba(0,0,0,.05);">
            <img src="data:image/png;base64,{img64}" style="max-height:{altura}px;width:auto;max-width:100%;object-fit:contain;">
            <div style="margin-top:.65rem;font-weight:700;color:#355e2b;font-size:1rem;line-height:1.35;">💬 {mensaje}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ir_a_inicio():
    st.session_state.pantalla_actual = "inicio"
    st.session_state.familia_actual = None
    st.session_state.subfamilia_actual = None
    sync_query_params()


def ir_a_catalogo():
    st.session_state.pantalla_actual = "catalogo"
    sync_query_params()


def seleccionar_familia(familia):
    st.session_state.familia_actual = familia
    st.session_state.subfamilia_actual = None
    st.session_state.pantalla_actual = "catalogo"
    sync_query_params()


def ir_a_contacto():
    st.session_state.pantalla_actual = "contacto"
    sync_query_params()


def ir_a_carrito():
    st.session_state.pantalla_actual = "carrito"
    sync_query_params()


def volver_a_familias():
    st.session_state.pantalla_actual = "catalogo"
    st.session_state.familia_actual = None
    st.session_state.subfamilia_actual = None
    sync_query_params()


def volver_a_subfamilias():
    st.session_state.subfamilia_actual = None
    sync_query_params()


def render_menu_superior():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.1rem;}
        a.family-card {text-decoration:none !important; display:block;}
        .family-wrap img {border-radius: 22px; box-shadow: 0 8px 24px rgba(0,0,0,.10);}
        .hero-card {
            background:
                radial-gradient(circle at top right, rgba(111, 168, 72, 0.22), transparent 32%),
                linear-gradient(135deg, #ffffff 0%, #f6faf5 55%, #eef7eb 100%);
            border: 1px solid #d9ead3;
            border-radius: 28px;
            padding: 2.4rem 1.8rem 2rem 1.8rem;
            text-align: center;
            box-shadow: 0 14px 34px rgba(0,0,0,.08);
        }
        .hero-badge {
            display:inline-block;
            background:#eaf5e5;
            color:#355e2b;
            font-weight:700;
            border-radius:999px;
            padding:.38rem .9rem;
            margin-bottom:.9rem;
            font-size:.92rem;
            border:1px solid #d9ead3;
        }
        .hero-title {
            font-size: clamp(2rem, 4vw, 3rem);
            line-height:1.08;
            margin:.1rem 0 .6rem 0;
            color:#1f2a1f;
        }
        .hero-subtitle {
            font-size:1.1rem;
            line-height:1.55;
            max-width:720px;
            margin:0 auto;
            color:#3e5140;
        }
        .hero-mini-grid {
            display:grid;
            grid-template-columns: repeat(3, minmax(0,1fr));
            gap:.8rem;
            margin-top:1.4rem;
        }
        .hero-mini-card {
            background: rgba(255,255,255,.78);
            border:1px solid #dfeedd;
            border-radius:18px;
            padding:.9rem;
            font-weight:600;
            color:#355e2b;
        }
        .contact-card {
            background: linear-gradient(135deg, #f8fbf8 0%, #eef7eb 100%);
            border:1px solid #d9ead3;
            border-radius:22px;
            padding:1.25rem;
            box-shadow: 0 8px 20px rgba(0,0,0,.05);
        }
        @media (max-width: 900px) {
            .hero-mini-grid {grid-template-columns: 1fr;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_inicio():
    logo_src = obtener_logo_src()

    render_aply(APLY_SALUDA, "Hola, soy Aply. Entra al catálogo y prepara tu pedido en pocos pasos.", altura=280)
    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='hero-card'>
            <div class='hero-badge'>Catálogo online · Pedido rápido</div>
            <img src='{logo_src}' style='width: min(430px, 82%); margin-bottom: 1rem;' />
            <h1 class='hero-title'>Haz tu pedido online</h1>
            <p class='hero-subtitle'>Accede al catálogo de Aplytec de forma rápida y sencilla. Encuentra lo que necesitas, añádelo al carrito y envía tu pedido desde el móvil en pocos pasos.</p>
            <div class='hero-mini-grid'>
                <div class='hero-mini-card'>📦 Productos organizados por familias</div>
                <div class='hero-mini-card'>🛒 Compra rápida y clara</div>
                <div class='hero-mini-card'>💬 Atención directa por WhatsApp</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    if st.button("📦 Entrar al catálogo", key="btn_inicio_catalogo", type="primary", use_container_width=True):
        ir_a_catalogo()
        st.rerun()

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='contact-card'>
            <h3 style='margin-top:0;'>Pedido rápido desde tu móvil</h3>
            <p style='margin-bottom:0.45rem;'>Explora las familias, añade productos al carrito y envía tu pedido de forma cómoda, clara y sin llamadas innecesarias.</p>
            <p style='margin-bottom:0;'><strong>WhatsApp:</strong> +34 647 93 63 56</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_contacto():
    render_aply(APLY_MOVIL, "¿Tienes dudas? Escríbenos por WhatsApp y te ayudamos con el pedido.", altura=280)
    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown("## Contacto")
    st.markdown(
        """
        <div class='contact-card'>
            <h3 style='margin-top:0;'>Aplytec</h3>
            <p><strong>WhatsApp:</strong> +34 647 93 63 56</p>
            <p>Escríbenos si prefieres ayuda directa para preparar tu pedido.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_carrito():
    render_aply(APLY_CARRITO, "Revisa tu pedido y no olvides indicar tu nombre y tu teléfono.", altura=230)
    st.markdown("<div style='height: 0.45rem;'></div>", unsafe_allow_html=True)
    st.markdown("## 🛒 Mi carrito")
    ruta_pdf = "resumen_pedido.pdf"

    st.markdown(
        """
        <style>
        .cart-resumen-sticky {
            position: sticky;
            top: 3.9rem;
            z-index: 50;
            background: rgba(255,255,255,.97);
            border: 1px solid #dfead9;
            border-radius: 16px;
            padding: .72rem .9rem;
            margin: .45rem 0 .85rem 0;
            box-shadow: 0 5px 16px rgba(0,0,0,.07);
            backdrop-filter: blur(6px);
        }
        .cart-resumen-sticky .cart-total {
            font-size: 1.18rem;
            font-weight: 800;
            line-height: 1.15;
        }
        .cart-resumen-sticky .cart-items {
            font-size: .86rem;
            opacity: .72;
            margin-top: .12rem;
        }
        .cart-linea {
            border: 1px solid #e6eee2;
            border-radius: 18px;
            padding: .78rem .85rem .45rem .85rem;
            margin: 0 0 .72rem 0;
            background: #fff;
            box-shadow: 0 4px 13px rgba(0,0,0,.045);
        }
        .cart-linea-nombre {
            font-size: 1rem;
            font-weight: 750;
            line-height: 1.22;
            margin-bottom: .2rem;
        }
        .cart-linea-meta {
            font-size: .79rem;
            opacity: .68;
            margin-bottom: .25rem;
        }
        .cart-linea-subtotal {
            font-size: 1.02rem;
            font-weight: 750;
            margin: .25rem 0 .45rem 0;
        }
        .cart-cantidad {
            text-align:center;
            font-size:1.05rem;
            font-weight:800;
            padding-top:.42rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.carrito:
        # El total mostrado en la cabecera se calcula siempre a partir del estado actual.
        total_cabecera = total_importe_carrito()
        items_cabecera = total_items_carrito()
        st.markdown(
            f"""
            <div class='cart-resumen-sticky'>
                <div class='cart-total'>Total: {total_cabecera:.2f} €</div>
                <div class='cart-items'>{items_cabecera} artículo{'s' if items_cabecera != 1 else ''} · IVA incluido</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        resumen = ""

        # Recorremos una copia para poder modificar/eliminar con seguridad.
        for item in list(st.session_state.carrito):
            item_id = item['id']
            cantidad = int(item['Cantidad'])
            precio_unitario = float(item['PrecioUnitario'])
            subtotal = cantidad * precio_unitario

            st.markdown("<div class='cart-linea'>", unsafe_allow_html=True)
            st.markdown(f"<div class='cart-linea-nombre'>{item['Nombre']}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='cart-linea-meta'>Código: {item['Código']} · {precio_unitario:.2f} €/ud.</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"<div class='cart-linea-subtotal'>Subtotal: {subtotal:.2f} €</div>", unsafe_allow_html=True)

            # Formato en una línea propia para que sea cómodo en móvil.
            nuevo_tipo = st.selectbox(
                "Formato",
                FORMATOS,
                index=FORMATOS.index(item["Tipo"]) if item["Tipo"] in FORMATOS else 0,
                key=f"cart_tipo_{item_id}",
            )
            if nuevo_tipo != item["Tipo"]:
                item["Tipo"] = nuevo_tipo
                sync_query_params()

            c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
            with c1:
                menos = st.button("−1", key=f"cart_minus_{item_id}", use_container_width=True)
            with c2:
                st.markdown(f"<div class='cart-cantidad'>{cantidad}</div>", unsafe_allow_html=True)
            with c3:
                mas = st.button("+1", key=f"cart_plus_{item_id}", use_container_width=True)
            with c4:
                mas5 = st.button("+5", key=f"cart_plus5_{item_id}", use_container_width=True)
            with c5:
                borrar = st.button("🗑️", key=f"delete_{item_id}", use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if borrar:
                st.session_state.carrito = [x for x in st.session_state.carrito if x['id'] != item_id]
                sync_query_params()
                st.rerun()
            if menos:
                if item["Cantidad"] <= 1:
                    st.session_state.carrito = [x for x in st.session_state.carrito if x['id'] != item_id]
                else:
                    item["Cantidad"] -= 1
                sync_query_params()
                st.rerun()
            if mas:
                item["Cantidad"] += 1
                sync_query_params()
                st.rerun()
            if mas5:
                item["Cantidad"] += 5
                sync_query_params()
                st.rerun()

        # Reconstruimos resumen y total después de posibles cambios de formato.
        total = total_importe_carrito()
        for item in st.session_state.carrito:
            subtotal = float(item["Cantidad"]) * float(item["PrecioUnitario"])
            resumen += f"- {item['Cantidad']} {item['Tipo']} de {item['Nombre']} (Codigo: {item['Código']}) -> {subtotal:.2f} euros\n"

        st.markdown(f"### Total del pedido: {total:.2f} €")
        st.caption("IVA incluido")

        # Acción principal antes de los datos del cliente: volver al catálogo sin perder el carrito.
        if st.button("➕ Seguir añadiendo productos", key="seguir_comprando_arriba", use_container_width=True):
            ir_a_catalogo()
            st.rerun()

        st.markdown("<div id='datos-pedido'></div>", unsafe_allow_html=True)
        st.markdown("### Datos para enviar el pedido")
        with st.form("form_pedido"):
            nombre = st.text_input("Tu nombre", key="pedido_nombre")
            telefono = st.text_input("Teléfono", key="pedido_telefono")
            comentarios = st.text_area(
                "Observaciones",
                key="pedido_observaciones",
                placeholder="Si es tu primera compra añade tus datos para facturar (CIF/NIF, Nombre, Dirección)"
            )
            enviar = st.form_submit_button("📨 Enviar pedido", use_container_width=True)

            if enviar:
                nombre_limpio = nombre.strip()
                telefono_limpio = telefono.strip()

                if not nombre_limpio or not telefono_limpio:
                    if not nombre_limpio and not telefono_limpio:
                        aviso = "Faltan nombre y teléfono para poder enviar el pedido."
                    elif not nombre_limpio:
                        aviso = "Falta el nombre para poder enviar el pedido."
                    else:
                        aviso = "Falta el teléfono para poder enviar el pedido."

                    st.warning(aviso)
                    components.html(
                        """
                        <script>
                        const doc = window.parent.document;
                        const heading = Array.from(doc.querySelectorAll('*')).find(el => (el.innerText || '').trim() === 'Tu nombre');
                        if (heading) {
                            heading.scrollIntoView({behavior: 'smooth', block: 'center'});
                        }
                        const inputs = Array.from(doc.querySelectorAll('input')).filter(el => el.offsetParent !== null);
                        const target = inputs.find(el => !el.value.trim());
                        if (target) {
                            target.focus();
                        }
                        </script>
                        """,
                        height=0,
                    )
                else:
                    resumen_txt = (
                        f"Pedido enviado por: {nombre_limpio}\n"
                        f"Telefono: {telefono_limpio}\n\n{resumen}\n"
                        f"Total: {total:.2f} euros (IVA incluido)\n\nComentarios: {comentarios}"
                    )
                    generar_pdf(nombre_limpio, resumen, total, comentarios, ruta_pdf)
                    enviar_pedido_por_email("Nuevo pedido de catálogo", resumen_txt, ruta_pdf)
                    st.success("✅ Pedido enviado correctamente")
                    st.session_state.pdf_generado = True
                    st.session_state.carrito = []
                    sync_query_params()

        b1, b2 = st.columns(2)
        with b1:
            if st.session_state.pdf_generado and Path(ruta_pdf).exists():
                with open(ruta_pdf, "rb") as f:
                    st.download_button(
                        "📄 Descargar PDF",
                        f,
                        file_name="resumen_pedido.pdf",
                        use_container_width=True,
                    )
        with b2:
            if st.button("🗑️ Vaciar carrito", use_container_width=True):
                st.session_state.carrito = []
                st.session_state.pdf_generado = False
                sync_query_params()
                st.rerun()
    else:
        st.info("No hay productos en el pedido.")
        if st.button("📦 Ver productos", use_container_width=True):
            ir_a_catalogo()
            st.rerun()



def inyectar_css_tarjetas_rejilla():
    st.markdown(
        """
        <style>
        .aply-grid-html {display:grid;grid-template-columns:1fr 1fr;gap:.7rem;margin:.25rem 0 1rem 0;}
        .aply-grid-card-link {text-decoration:none !important;color:inherit !important;}
        .aply-grid-card-box {background:#fff;border:1px solid #e6efe2;border-radius:22px;padding:.22rem;box-shadow:0 7px 18px rgba(0,0,0,.07);overflow:hidden;}
        .aply-grid-card-box img {display:block;width:100%;height:auto;border-radius:18px;}
        .aply-grid-card-fallback {display:flex;align-items:center;justify-content:center;min-height:132px;font-size:3.1rem;background:linear-gradient(135deg,#f8fbf8,#eef7eb);border-radius:18px;}
        @media (max-width: 768px) {
            .aply-grid-html {grid-template-columns:1fr 1fr !important;gap:.55rem;}
            .aply-grid-card-box {border-radius:18px;padding:.16rem;}
            .aply-grid-card-box img, .aply-grid-card-fallback {border-radius:15px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_rejilla_component(items):
    import html
    rows = []
    for i in range(0, len(items), 2):
        pares = items[i:i+2]
        celdas = []
        for item in pares:
            href = html.escape(item["href"], quote=True)
            alt = html.escape(item["alt"], quote=True)
            if item.get("img"):
                media = f'<img src="{item["img"]}" alt="{alt}">'
            else:
                fallback = html.escape(str(item.get("fallback", "📦")))
                media = f'<div class="aply-grid-card-fallback">{fallback}</div>'
            celdas.append(
                f'<td style="width:50%; padding:0 5px 10px 5px; vertical-align:top;">'
                f'<a class="aply-grid-card-link" href="{href}">'
                f'<div class="aply-grid-card-box">{media}</div>'
                f'</a></td>'
            )
        if len(celdas) == 1:
            celdas.append('<td style="width:50%; padding:0 5px 10px 5px;"></td>')
        rows.append('<tr>' + ''.join(celdas) + '</tr>')

    html_block = (
        '<table style="width:100%; table-layout:fixed; border-collapse:collapse; margin:0 0 .8rem 0;">'
        + ''.join(rows)
        + '</table>'
    )
    st.markdown(html_block, unsafe_allow_html=True)


def render_rejilla_familias():
    items = []
    for familia, _fam_id, icono in FAMILIAS_ORDENADAS:
        img = obtener_ruta_imagen_familia(familia)
        items.append({
            "href": qp_url(pantalla="catalogo", familia=familia),
            "alt": familia,
            "img": imagen_data_uri(img) if img and img.exists() else None,
            "fallback": icono,
        })
    render_rejilla_component(items)


def render_rejilla_subfamilias_quimicos():
    items = []
    for subfamilia, _archivo in QUIMICOS_SUBFAMILIAS_ORDENADAS:
        img = obtener_ruta_imagen_subfamilia_quimicos(subfamilia)
        items.append({
            "href": qp_url(pantalla="catalogo", familia="Químicos", subfamilia=subfamilia),
            "alt": subfamilia,
            "img": imagen_data_uri(img) if img and img.exists() else None,
            "fallback": subfamilia,
        })
    render_rejilla_component(items)


def construir_mapa_cantidades_carrito():
    cantidades = {}
    for item in st.session_state.carrito:
        clave = (str(item["Código"]), str(item["Tipo"]))
        cantidades[clave] = cantidades.get(clave, 0) + int(item["Cantidad"])
    return cantidades

def render_producto_compacto(fila, prefijo, mostrar_ubicacion=False):
    codigo = str(fila["Código"])
    nombre = str(fila["Nombre"])
    precio_con_iva = float(fila["Precio"])

    st.markdown(
        """
        <style>
        .producto-card-title {
            font-size:1.05rem;
            font-weight:800;
            line-height:1.2;
            margin:.15rem 0 .25rem 0;
            color:#263526;
        }
        .producto-precio {
            font-size:1.25rem;
            font-weight:900;
            color:#355e2b;
            margin:.05rem 0 .2rem 0;
        }
        .producto-meta {
            font-size:.78rem;
            color:#6a746a;
            margin-bottom:.25rem;
        }
        .producto-en-carrito {
            text-align:center;
            font-size:.9rem;
            font-weight:800;
            color:#355e2b;
            padding:.35rem .1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        ruta_img = obtener_ruta_imagen_producto(codigo)
        if ruta_img:
            img64 = imagen_a_base64(ruta_img)
            st.markdown(
                f'<div style="text-align:center;height:130px;overflow:hidden;display:flex;align-items:center;justify-content:center;">'
                f'<img src="data:image/png;base64,{img64}" style="max-height:125px;max-width:100%;object-fit:contain;">'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown(f'<div class="producto-card-title">{nombre}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="producto-precio">{precio_con_iva:.2f} € <span style="font-size:.72rem;font-weight:600;color:#6a746a;">IVA incluido</span></div>', unsafe_allow_html=True)

        meta = f"Código: {codigo}"
        if mostrar_ubicacion:
            meta += f" · {fila['Familia']} · {fila['Subfamilia']}"
        st.markdown(f'<div class="producto-meta">{meta}</div>', unsafe_allow_html=True)

        tipo = st.radio(
            "Formato",
            FORMATOS,
            horizontal=True,
            key=f"tipo_{prefijo}_{codigo}",
            label_visibility="collapsed",
        )

        qty_actual = cantidad_en_carrito(codigo, tipo)
        b1, b2, b3, b4 = st.columns([1, 1, 1, 1.2], gap="small")
        with b1:
            if st.button("−1", key=f"menos_{prefijo}_{codigo}_{tipo}", use_container_width=True):
                quitar_del_carrito(codigo, tipo, 1)
                st.rerun()
        with b2:
            st.markdown(f'<div class="producto-en-carrito">{qty_actual}</div>', unsafe_allow_html=True)
        with b3:
            if st.button("+1", key=f"mas_{prefijo}_{codigo}_{tipo}", use_container_width=True, type="primary"):
                agregar_o_sumar_al_carrito(codigo, nombre, tipo, precio_con_iva, 1)
                st.rerun()
        with b4:
            if st.button("+5", key=f"add5_{prefijo}_{codigo}_{tipo}", use_container_width=True):
                agregar_o_sumar_al_carrito(codigo, nombre, tipo, precio_con_iva, 5)
                st.rerun()

def render_catalogo(df):
    busqueda_global = st.text_input("🔎 Buscar producto por nombre o código", key="busqueda_global_catalogo")

    if busqueda_global:
        resultados = df[
            df["Nombre"].str.contains(busqueda_global, case=False, na=False)
            | df["Código"].astype(str).str.contains(busqueda_global, case=False, na=False)
        ].copy()

        st.markdown(f"### Resultados: {len(resultados)}")
        cantidades_carrito = construir_mapa_cantidades_carrito()

        for _, fila in resultados.iterrows():
            render_producto_compacto(fila, "busq", mostrar_ubicacion=True)

    if st.session_state.familia_actual is None:
        render_aply(APLY_SENALA, "Elige una familia para ver los productos.", altura=190)
        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        st.markdown("## Familias")
        st.caption("Toca una familia para ver los productos")
        render_rejilla_familias()
        return

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
            busqueda_familia = st.text_input(
                "🔎 Buscar dentro de esta familia",
                key=f"busqueda_familia_{familia_actual}"
            )

            if busqueda_familia:
                productos_familia = df[
                    (df["Familia"] == familia_actual)
                    & (
                        df["Nombre"].str.contains(busqueda_familia, case=False, na=False)
                        | df["Código"].astype(str).str.contains(busqueda_familia, case=False, na=False)
                    )
                ].copy()

                st.markdown(f"### Resultados en {familia_actual}: {len(productos_familia)}")
                cantidades_carrito = construir_mapa_cantidades_carrito()

                for _, fila in productos_familia.iterrows():
                    render_producto_compacto(fila, "fam", mostrar_ubicacion=False)

            render_aply(APLY_SENALA, "Elige una subfamilia para ver los productos.", altura=190)
            if familia_actual == "Químicos":
                st.markdown("### Selecciona una subfamilia")
                render_rejilla_subfamilias_quimicos()
                return
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
            return

    subfamilia_actual = st.session_state.subfamilia_actual
    productos = df[
        (df["Familia"] == familia_actual) & (df["Subfamilia"] == subfamilia_actual)
    ].copy()

    top1, top2, top3 = st.columns([1, 2, 1.4])
    with top1:
        if st.button("⬅️ Subfamilias", use_container_width=True):
            volver_a_subfamilias()
            st.rerun()
    with top2:
        st.markdown(f"### {subfamilia_actual}")
    with top3:
        if st.button(f"🛒 Ver carrito ({total_items_carrito()})", key="btn_carrito_catalogo", use_container_width=True):
            ir_a_carrito()
            st.rerun()

    busqueda_subfamilia = st.text_input(
        "🔎 Buscar dentro de esta subfamilia",
        key=f"busqueda_subfamilia_{familia_actual}_{subfamilia_actual}"
    )
    if busqueda_subfamilia:
        productos = productos[
            productos["Nombre"].str.contains(busqueda_subfamilia, case=False, na=False)
            | productos["Código"].astype(str).str.contains(busqueda_subfamilia, case=False, na=False)
        ].copy()

    render_aply(APLY_SENALA, "Pulsa +1 o Añadir 5 para meter productos en tu pedido.", altura=190)

    cantidades_carrito = construir_mapa_cantidades_carrito()

    for _, fila in productos.iterrows():
        render_producto_compacto(fila, "sub", mostrar_ubicacion=False)


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
if "pantalla_actual" not in st.session_state:
    st.session_state.pantalla_actual = "inicio"

qp = st.query_params
cart_qp = qp.get("cart")
if cart_qp:
    carrito_qp = restaurar_carrito_desde_qp(cart_qp)
    if carrito_qp:
        st.session_state.carrito = carrito_qp
        st.session_state.next_cart_id = max([int(x.get("id", 0)) for x in carrito_qp] + [0]) + 1
if qp.get("familia"):
    st.session_state.familia_actual = qp.get("familia")
    st.session_state.pantalla_actual = "catalogo"
if qp.get("subfamilia"):
    st.session_state.subfamilia_actual = qp.get("subfamilia")
    st.session_state.pantalla_actual = "catalogo"
if qp.get("pantalla") in {"inicio", "catalogo", "carrito", "contacto"}:
    st.session_state.pantalla_actual = qp.get("pantalla")

st.set_page_config(page_title="Catálogo APLYTEC", layout="wide")

sync_query_params()
df = cargar_datos()
render_menu_superior()
render_boton_carrito_flotante()

if st.session_state.pantalla_actual == "inicio":
    render_inicio()
elif st.session_state.pantalla_actual == "contacto":
    render_contacto()
elif st.session_state.pantalla_actual == "carrito":
    render_carrito()
else:
    render_catalogo(df)
