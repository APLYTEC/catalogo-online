import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import smtplib
import ssl
import base64
import json
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
    try:
        data = [{
            "id": int(item.get("id", 0)),
            "Código": str(item.get("Código", "")),
            "Nombre": str(item.get("Nombre", "")),
            "Cantidad": int(item.get("Cantidad", 0)),
            "Tipo": str(item.get("Tipo", "")),
            "PrecioUnitario": float(item.get("PrecioUnitario", 0.0)),
        } for item in st.session_state.carrito]
        return quote(json.dumps(data, ensure_ascii=False, separators=(",", ":")), safe="")
    except Exception:
        return ""


def restaurar_carrito_desde_qp(valor):
    if not valor:
        return []
    try:
        data = json.loads(valor)
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
        parts.append(f"cart={cart}")
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
    total = total_items_carrito()
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
        .cta-band {
            background:#355e2b;
            color:white;
            border-radius:22px;
            padding:1.2rem 1.2rem;
            box-shadow: 0 12px 26px rgba(53,94,43,.22);
        }
        .cta-band p, .cta-band h3 {color:white; margin:0;}
        .topbar-btn button {height: 48px; font-weight: 700;}
        @media (max-width: 900px) {
            .hero-mini-grid {grid-template-columns: 1fr;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    b1, b2, b3, b4 = st.columns([1.1, 1.1, 1.1, 1.2])
    with b1:
        if st.button("🏠 Inicio", use_container_width=True, key="top_inicio"):
            ir_a_inicio()
            st.rerun()
    with b2:
        if st.button("📦 Ver productos", use_container_width=True, key="top_productos"):
            ir_a_catalogo()
            st.rerun()
    with b3:
        if st.button(f"🛒 Mi carrito ({total})", use_container_width=True, key="top_carrito"):
            ir_a_carrito()
            st.rerun()
    with b4:
        st.link_button("💬 WhatsApp", WHATSAPP_LINK, use_container_width=True)

    st.markdown("<div style='margin-top:0.3rem'></div>", unsafe_allow_html=True)


def render_inicio():
    logo_src = obtener_logo_src()

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
    render_aply(APLY_SALUDA, "Hola, soy Aply. Entra al catálogo y prepara tu pedido en pocos pasos.", altura=280)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📦 Ver productos", use_container_width=True, key="inicio_productos"):
            ir_a_catalogo()
            st.rerun()
    with c2:
        if st.button(f"🛒 Mi carrito ({total_items_carrito()})", use_container_width=True, key="inicio_carrito"):
            ir_a_carrito()
            st.rerun()
    with c3:
        if st.button("📞 Contacto", use_container_width=True, key="inicio_contacto"):
            ir_a_contacto()
            st.rerun()

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    cta1, cta2 = st.columns([1.8, 1.2])
    with cta1:
        st.markdown(
            """
            <div class='cta-band'>
                <h3>Escanea, entra y pide</h3>
                <p style='margin-top:.35rem;'>Ideal para panfletos y clientes: acceso directo al catálogo, navegación fácil y contacto inmediato.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cta2:
        st.link_button("💬 Pedir por WhatsApp", WHATSAPP_LINK, use_container_width=True)

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    w1, w2 = st.columns([2, 1])
    with w1:
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
    with w2:
        if st.button("📦 Entrar al catálogo", use_container_width=True, key="inicio_catalogo_extra"):
            ir_a_catalogo()
            st.rerun()



def render_contacto():
    st.markdown("## Contacto")
    c1, c2 = st.columns([1.7, 1])
    with c1:
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
        st.link_button("💬 Hablar por WhatsApp", WHATSAPP_LINK, use_container_width=True)
    with c2:
        render_aply(APLY_MOVIL, "¿Tienes dudas? Escríbenos por WhatsApp y te ayudamos con el pedido.", altura=280)



def render_carrito():
    st.markdown("## 🛒 Mi carrito")
    c1, c2 = st.columns([1.8, 1])
    with c1:
        st.markdown("Completa tu pedido y envíalo cuando esté todo correcto.")
    with c2:
        render_aply(APLY_CARRITO, "Revisa tu pedido y no olvides indicar tu nombre y tu teléfono.", altura=230)
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
                    label_visibility="collapsed",
                )
            with s3:
                nuevo_tipo = st.selectbox(
                    f"Formato carrito {item['id']}",
                    FORMATOS,
                    index=FORMATOS.index(item["Tipo"]) if item["Tipo"] in FORMATOS else 0,
                    key=f"cart_tipo_{item['id']}",
                    label_visibility="collapsed",
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

        st.markdown("<div id='datos-pedido'></div>", unsafe_allow_html=True)
        with st.form("form_pedido"):
            nombre = st.text_input("Tu nombre", key="pedido_nombre")
            telefono = st.text_input("Teléfono", key="pedido_telefono")
            comentarios = st.text_area(
                "Observaciones",
                key="pedido_observaciones",
                placeholder="Si es tu primera compra añade tus datos para facturar (CIF/NIF, Nombre, Dirección)"
            )
            enviar = st.form_submit_button("📨 Enviar pedido")

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

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.session_state.pdf_generado and Path(ruta_pdf).exists():
                with open(ruta_pdf, "rb") as f:
                    st.download_button(
                        "📄 Descargar resumen en PDF",
                        f,
                        file_name="resumen_pedido.pdf",
                        use_container_width=True,
                    )
        with b2:
            if st.button("🗑️ Vaciar carrito", use_container_width=True):
                st.session_state.carrito = []
                st.session_state.pdf_generado = False
                st.warning("Carrito vaciado")
                st.rerun()
        with b3:
            if st.button("📦 Seguir comprando", use_container_width=True):
                ir_a_catalogo()
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


def render_rejilla_component(items, altura=780):
    import html, json
    cards = []
    for item in items:
        href = item["href"]
        alt = item["alt"]
        href_js = json.dumps(href)
        alt_attr = html.escape(alt, quote=True)
        href_attr = html.escape(href, quote=True)
        if item.get("img"):
            media = f'<img src="{item["img"]}" alt="{alt_attr}">'
        else:
            fallback = html.escape(str(item.get("fallback", "📦")))
            media = f'<div class="grid-fallback">{fallback}</div>'
        onclick = f"try{{window.parent.location.search={href_js};}}catch(e){{window.location.search={href_js};}} return false;"
        cards.append(
            f'<a class="grid-card" href="{href_attr}" aria-label="{alt_attr}" onclick="{html.escape(onclick, quote=True)}">{media}</a>'
        )

    html = f"""
    <!doctype html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      html, body {{ margin:0; padding:0; background:transparent; overflow:hidden; }}
      .grid-wrap {{
        display:grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
        padding: 2px 2px 8px 2px;
        box-sizing:border-box;
      }}
      .grid-card {{
        display:block;
        text-decoration:none;
        background:#fff;
        border:1px solid #e6efe2;
        border-radius:20px;
        padding:3px;
        box-shadow:0 7px 18px rgba(0,0,0,.08);
        overflow:hidden;
        min-height: 120px;
      }}
      .grid-card img {{
        display:block;
        width:100%;
        height:auto;
        border-radius:17px;
      }}
      .grid-fallback {{
        display:flex; align-items:center; justify-content:center;
        min-height:120px;
        border-radius:17px;
        background:linear-gradient(135deg,#f8fbf8,#eef7eb);
        font-size:3rem;
      }}
    </style>
    </head>
    <body>
      <div class="grid-wrap">{''.join(cards)}</div>
    </body>
    </html>
    """
    components.html(html, height=altura, scrolling=False)


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
    render_rejilla_component(items, altura=720)


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
    render_rejilla_component(items, altura=720)


def construir_mapa_cantidades_carrito():
    cantidades = {}
    for item in st.session_state.carrito:
        clave = (str(item["Código"]), str(item["Tipo"]))
        cantidades[clave] = cantidades.get(clave, 0) + int(item["Cantidad"])
    return cantidades

def render_catalogo(df):
    if st.session_state.familia_actual is None:
        st.markdown("## Familias")
        st.caption("Toca una familia para ver los productos")

        render_rejilla_familias()

        cantidades_carrito = construir_mapa_cantidades_carrito()

        with st.expander("🔎 Buscar producto por nombre o código"):

            busqueda_global = st.text_input("Busca por nombre o código", key="busqueda_global_catalogo")
            if busqueda_global:
                resultados = df[
                    df["Nombre"].str.contains(busqueda_global, case=False, na=False)
                    | df["Código"].astype(str).str.contains(busqueda_global, case=False, na=False)
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
                            label_visibility="collapsed",
                        )

                        qty_actual = cantidades_carrito.get((str(fila["Código"]), str(tipo)), 0)
                        a1, a2, a3, a4 = st.columns([1, 1, 1.3, 1.5])
                        with a1:
                            if st.button("-1", key=f"menos_busq_{fila['Código']}_{tipo}", use_container_width=True):
                                quitar_del_carrito(fila["Código"], tipo, 1)
                                st.rerun()
                        with a2:
                            if st.button("+1", key=f"mas_busq_{fila['Código']}_{tipo}", use_container_width=True):
                                agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 1)
                                st.rerun()
                        with a3:
                            st.markdown(f"**En carrito:** {qty_actual}")
                        with a4:
                            if st.button("Añadir 5", key=f"add5_busq_{fila['Código']}_{tipo}", use_container_width=True):
                                agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 5)
                                st.rerun()
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

    render_aply(APLY_SENALA, "Pulsa +1 o Añadir 5 para meter productos en tu pedido.", altura=190)

    cantidades_carrito = construir_mapa_cantidades_carrito()

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
                label_visibility="collapsed",
            )

            qty_actual = cantidades_carrito.get((str(fila["Código"]), str(tipo)), 0)
            a1, a2, a3, a4 = st.columns([1, 1, 1.3, 1.5])
            with a1:
                if st.button("-1", key=f"menos_{fila['Código']}_{tipo}", use_container_width=True):
                    quitar_del_carrito(fila["Código"], tipo, 1)
                    st.rerun()
            with a2:
                if st.button("+1", key=f"mas_{fila['Código']}_{tipo}", use_container_width=True):
                    agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 1)
                    st.rerun()
            with a3:
                st.markdown(f"**En carrito:** {qty_actual}")
            with a4:
                if st.button("Añadir 5", key=f"add5_{fila['Código']}_{tipo}", use_container_width=True):
                    agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 5)
                    st.rerun()


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
