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
CARPETAS_IMAGENES_CANDIDATAS = [Path("imagenes"), Path("Imagenes"), Path("image"), Path("images")]

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

CELULOSAS_SUBFAMILIAS_ORDENADAS = [
    ("Servilletas", "sub_celulosas_servilletas.png"),
    ("Manteles y mantelines", "sub_celulosas_manteles_mantelines.png"),
    ("Toallas", "sub_celulosas_toallas.png"),
    ("Papel higiénico industrial / jumbo", "sub_celulosas_papel_higienico_industrial_jumbo.png"),
    ("Bobinas y papel mecha", "sub_celulosas_bobinas_papel_mecha.png"),
    ("Papel higiénico doméstico", "sub_celulosas_papel_higienico_domestico.png"),
    ("Papel camilla y sanitario", "sub_celulosas_papel_camilla_sanitario.png"),
    ("Pañuelos y toallitas", "sub_celulosas_panuelos_toallitas.png"),
]

UTILES_SUBFAMILIAS_ORDENADAS = [
    ("Bayetas, paños y estropajos", "sub_utiles_bayetas_panos_estropajos.png"),
    ("Mopas, fregonas y recambios", "sub_utiles_mopas_fregonas_recambios.png"),
    ("Escobas, cepillos y recogedores", "sub_utiles_escobas_cepillos_recogedores.png"),
    ("Limpiacristales y útiles de cristalería", "sub_utiles_limpiacristales_utiles_cristaleria.png"),
    ("Cubos, carros y escurridores", "sub_utiles_cubos_carros_escurridores.png"),
    ("Pulverizadores, dosificación y señalización", "sub_utiles_pulverizadores_dosificacion_senalizacion.png"),
    ("Guantes y protección", "sub_utiles_guantes_proteccion.png"),
    ("Otros útiles y accesorios", "sub_utiles_otros_utiles_accesorios.png"),
]

DESECHABLES_SUBFAMILIAS_ORDENADAS = [
    ("Bolsas de basura y sacos", "sub_desechables_bolsas_basura_sacos.png"),
    ("Bolsas alimentarias y uso especial", "sub_desechables_bolsas_alimentarias_uso_especial.png"),
    ("Guantes desechables", "sub_desechables_guantes_desechables.png"),
    ("Vestuario y protección desechable", "sub_desechables_vestuario_proteccion_desechable.png"),
    ("Vajilla desechable y reutilizable", "sub_desechables_vajilla_desechable_reutilizable.png"),
    ("Envases, tapas y tarrinas", "sub_desechables_envases_tapas_tarrinas.png"),
    ("Films, aluminio y precintos", "sub_desechables_films_aluminio_precintos.png"),
    ("Higiene y consumibles desechables", "sub_desechables_higiene_consumibles_desechables.png"),
]

EQUIPAMIENTO_SUBFAMILIAS_ORDENADAS = [
    ("Dispensadores de jabón y gel", "sub_equipamiento_dispensadores_jabon_gel.png"),
    ("Dispensadores de papel higiénico", "sub_equipamiento_dispensadores_papel_higienico.png"),
    ("Dispensadores de toallas, mecha y servilletas", "sub_equipamiento_dispensadores_toallas_mecha_servilletas.png"),
    ("Dosificación y dilución química", "sub_equipamiento_dosificacion_dilucion_quimica.png"),
    ("Ambientación y urinarios", "sub_equipamiento_ambientacion_urinarios.png"),
    ("Accesorios de baño y sala", "sub_equipamiento_accesorios_bano_sala.png"),
    ("Carros, soportes y mobiliario auxiliar", "sub_equipamiento_carros_soportes_mobiliario_auxiliar.png"),
    ("Otros equipamientos", "sub_equipamiento_otros_equipamientos.png"),
]

MAQUINAS_SUBFAMILIAS_ORDENADAS = [
    ("Máquinas de limpieza de suelos", "sub_maquinas_limpieza_suelos.png"),
    ("Lavado industrial, cocina y lavandería", "sub_maquinas_lavado_industrial_cocina_lavanderia.png"),
    ("Dosificación, dilución y laboratorio", "sub_maquinas_dosificacion_dilucion_laboratorio.png"),
    ("Repuestos, accesorios y SAT", "sub_maquinas_repuestos_accesorios_sat.png"),
]

OTROS_SUBFAMILIAS_ORDENADAS = [
    ("Otros", "familia_7.png"),
]

SERVICIOS_SUBFAMILIAS_ORDENADAS = [
    ("Otros", "familia_9.png"),
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


class DocumentoPDF(FPDF):
    def __init__(self, titulo_documento="Pedido"):
        super().__init__()
        self.titulo_documento = titulo_documento

    def header(self):
        if Path("images.png").exists():
            self.image("images.png", 10, 8, 33)
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, f"APLYTEC - {self.titulo_documento}", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Pagina " + str(self.page_no()), 0, 0, "C")


def _asegurar_espacio_pdf(pdf, alto_necesario=25):
    if pdf.get_y() + alto_necesario > 270:
        pdf.add_page()


def generar_pdf(nombre, resumen, total, comentarios, output_path, tipo_documento="pedido", incluir_imagenes=False, carrito=None, telefono=""):
    titulo = "Presupuesto" if str(tipo_documento).lower() == "presupuesto" else "Pedido"
    pdf = DocumentoPDF(titulo)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Cliente: {nombre}", ln=True)
    if telefono:
        pdf.cell(0, 10, f"Telefono: {telefono}", ln=True)
    pdf.ln(3)

    if incluir_imagenes and carrito:
        for item in carrito:
            _asegurar_espacio_pdf(pdf, 34)
            ruta_img = obtener_ruta_imagen_producto(item.get("Código", ""))
            y_inicio = pdf.get_y()
            if ruta_img and Path(ruta_img).exists():
                try:
                    pdf.image(str(ruta_img), x=10, y=y_inicio, w=24, h=24)
                except Exception:
                    pass
            pdf.set_xy(38, y_inicio)
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 6, str(item.get("Nombre", "")))
            pdf.set_x(38)
            pdf.set_font("Arial", "", 10)
            subtotal = float(item.get("Cantidad", 0)) * float(item.get("PrecioUnitario", 0.0))
            pdf.multi_cell(0, 5, f"Codigo: {item.get('Código', '')}\nCantidad: {item.get('Cantidad', 0)} {item.get('Tipo', '')}\nSubtotal: {subtotal:.2f} euros")
            pdf.ln(2)
    else:
        pdf.multi_cell(0, 8, resumen)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    etiqueta_total = "Total del presupuesto" if titulo == "Presupuesto" else "Total del pedido"
    pdf.cell(0, 10, f"{etiqueta_total}: {total:.2f} euros (IVA incluido)", ln=True)

    if titulo == "Presupuesto":
        pdf.set_font("Arial", "I", 10)
        pdf.multi_cell(0, 8, "Presupuesto sujeto a disponibilidad y revision de precios.")

    if comentarios:
        pdf.ln(6)
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 8, f"Comentarios: {comentarios}")
    pdf.output(output_path)


def enviar_documento_por_email(asunto, cuerpo, adjunto_path, nombre_adjunto="documento.pdf"):
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
                filename=nombre_adjunto,
            )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_REMITENTE, CONTRASENA_APP)
        server.send_message(msg)


def obtener_configuracion_documento(opcion):
    opcion = str(opcion).strip()
    if opcion == "Presupuesto con imágenes":
        return {
            "tipo_documento": "presupuesto",
            "incluir_imagenes": True,
            "titulo": "Presupuesto",
            "archivo": "presupuesto_con_imagenes.pdf",
            "asunto": "Nuevo presupuesto de catálogo",
            "boton": "📨 Enviar presupuesto con imágenes",
            "success": "✅ Presupuesto con imágenes enviado correctamente",
            "download": "📄 Descargar presupuesto con imágenes",
        }
    if opcion == "Presupuesto sin imágenes":
        return {
            "tipo_documento": "presupuesto",
            "incluir_imagenes": False,
            "titulo": "Presupuesto",
            "archivo": "presupuesto_sin_imagenes.pdf",
            "asunto": "Nuevo presupuesto de catálogo",
            "boton": "📨 Enviar presupuesto",
            "success": "✅ Presupuesto enviado correctamente",
            "download": "📄 Descargar presupuesto",
        }
    return {
        "tipo_documento": "pedido",
        "incluir_imagenes": False,
        "titulo": "Pedido",
        "archivo": "resumen_pedido.pdf",
        "asunto": "Nuevo pedido de catálogo",
        "boton": "📨 Enviar pedido",
        "success": "✅ Pedido enviado correctamente",
        "download": "📄 Descargar resumen en PDF",
    }


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

def buscar_imagen_por_bases(bases, extensiones=(".png", ".jpg", ".jpeg", ".webp", ".gif")):
    if isinstance(bases, str):
        bases = [bases]
    carpetas = []
    for carpeta in CARPETAS_IMAGENES_CANDIDATAS:
        if carpeta not in carpetas:
            carpetas.append(carpeta)
    if CARPETA_IMAGENES not in carpetas:
        carpetas.insert(0, CARPETA_IMAGENES)

    for carpeta in carpetas:
        for base in bases:
            base = str(base)
            if Path(base).suffix:
                ruta_directa = carpeta / base
                if ruta_directa.exists():
                    return ruta_directa
            for ext in extensiones:
                ruta = carpeta / f"{base}{ext}"
                if ruta.exists():
                    return ruta
    return None


def obtener_ruta_imagen_producto(codigo):
    return buscar_imagen_por_bases(str(codigo).strip())


def obtener_ruta_imagen_familia(nombre_familia):
    info = FAMILIAS.get(nombre_familia, {})
    fam_id = info.get("id")
    if fam_id is None:
        return None
    return buscar_imagen_por_bases(f"familia_{fam_id}")


def _obtener_ruta_desde_mapa(subfamilia, mapa):
    base = mapa.get(str(subfamilia).strip())
    if not base:
        return None
    return buscar_imagen_por_bases(base)


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
    return _obtener_ruta_desde_mapa(subfamilia, mapa)


def obtener_ruta_imagen_subfamilia_celulosas(subfamilia):
    mapa = {
        "Servilletas": "sub_celulosas_servilletas",
        "Manteles y mantelines": "sub_celulosas_manteles_mantelines",
        "Toallas": "sub_celulosas_toallas",
        "Papel higiénico industrial / jumbo": "sub_celulosas_papel_higienico_industrial_jumbo",
        "Bobinas y papel mecha": "sub_celulosas_bobinas_papel_mecha",
        "Papel higiénico doméstico": "sub_celulosas_papel_higienico_domestico",
        "Papel camilla y sanitario": "sub_celulosas_papel_camilla_sanitario",
        "Pañuelos y toallitas": "sub_celulosas_panuelos_toallitas",
    }
    return _obtener_ruta_desde_mapa(subfamilia, mapa)


def obtener_ruta_imagen_subfamilia_utiles(subfamilia):
    mapa = {
        "Bayetas, paños y estropajos": "sub_utiles_bayetas_panos_estropajos",
        "Mopas, fregonas y recambios": "sub_utiles_mopas_fregonas_recambios",
        "Escobas, cepillos y recogedores": "sub_utiles_escobas_cepillos_recogedores",
        "Limpiacristales y útiles de cristalería": "sub_utiles_limpiacristales_utiles_cristaleria",
        "Cubos, carros y escurridores": "sub_utiles_cubos_carros_escurridores",
        "Pulverizadores, dosificación y señalización": "sub_utiles_pulverizadores_dosificacion_senalizacion",
        "Guantes y protección": "sub_utiles_guantes_proteccion",
        "Otros útiles y accesorios": "sub_utiles_otros_utiles_accesorios",
    }
    return _obtener_ruta_desde_mapa(subfamilia, mapa)


def obtener_ruta_imagen_subfamilia_desechables(subfamilia):
    mapa = {
        "Bolsas de basura y sacos": "sub_desechables_bolsas_basura_sacos",
        "Bolsas alimentarias y uso especial": "sub_desechables_bolsas_alimentarias_uso_especial",
        "Guantes desechables": "sub_desechables_guantes_desechables",
        "Vestuario y protección desechable": "sub_desechables_vestuario_proteccion_desechable",
        "Vajilla desechable y reutilizable": "sub_desechables_vajilla_desechable_reutilizable",
        "Envases, tapas y tarrinas": "sub_desechables_envases_tapas_tarrinas",
        "Films, aluminio y precintos": "sub_desechables_films_aluminio_precintos",
        "Higiene y consumibles desechables": "sub_desechables_higiene_consumibles_desechables",
    }
    return _obtener_ruta_desde_mapa(subfamilia, mapa)


def obtener_ruta_imagen_subfamilia_equipamiento(subfamilia):
    mapa = {
        "Dispensadores de jabón y gel": "sub_equipamiento_dispensadores_jabon_gel",
        "Dispensadores de papel higiénico": "sub_equipamiento_dispensadores_papel_higienico",
        "Dispensadores de toallas, mecha y servilletas": "sub_equipamiento_dispensadores_toallas_mecha_servilletas",
        "Dosificación y dilución química": "sub_equipamiento_dosificacion_dilucion_quimica",
        "Ambientación y urinarios": "sub_equipamiento_ambientacion_urinarios",
        "Accesorios de baño y sala": "sub_equipamiento_accesorios_bano_sala",
        "Carros, soportes y mobiliario auxiliar": "sub_equipamiento_carros_soportes_mobiliario_auxiliar",
        "Otros equipamientos": "sub_equipamiento_otros_equipamientos",
    }
    return _obtener_ruta_desde_mapa(subfamilia, mapa)


def obtener_ruta_imagen_subfamilia_maquinas(subfamilia):
    mapa = {
        "Máquinas de limpieza de suelos": "sub_maquinas_limpieza_suelos",
        "Lavado industrial, cocina y lavandería": "sub_maquinas_lavado_industrial_cocina_lavanderia",
        "Dosificación, dilución y laboratorio": "sub_maquinas_dosificacion_dilucion_laboratorio",
        "Repuestos, accesorios y SAT": "sub_maquinas_repuestos_accesorios_sat",
    }
    return _obtener_ruta_desde_mapa(subfamilia, mapa)


def obtener_ruta_imagen_subfamilia_otros(_subfamilia):
    return obtener_ruta_imagen_familia("Otros")


def obtener_ruta_imagen_subfamilia_servicios(_subfamilia):
    return obtener_ruta_imagen_familia("Servicios")


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
        .hero-info-box {
            max-width: 760px;
            margin: 1.3rem auto 0 auto;
            background: rgba(255,255,255,.88);
            border: 1px solid #dfeedd;
            border-radius: 20px;
            padding: 1rem 1.1rem;
            text-align: left;
            box-shadow: 0 8px 18px rgba(0,0,0,.04);
        }
        .hero-info-box ul {
            list-style: none;
            margin: 0;
            padding: 0;
        }
        .hero-info-box li {
            color:#355e2b;
            font-weight:600;
            padding: .28rem 0;
            line-height:1.35;
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
            .hero-info-box {padding: .95rem 1rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1.1, 3.8, 1.1])
    with c1:
        if st.button("🏠 Ir a inicio", use_container_width=True, key="top_inicio"):
            ir_a_inicio()
            st.rerun()
    with c2:
        st.markdown("", unsafe_allow_html=True)
    with c3:
        st.markdown("", unsafe_allow_html=True)

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
            <div class='hero-info-box'>
                <ul>
                    <li>📦 Productos organizados por familias</li>
                    <li>🛒 Compra rápida y clara</li>
                    <li>💬 Atención directa por WhatsApp</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    render_aply(APLY_SALUDA, 'Hola, soy Aply. Entra en el catálogo pulsando el botón "Ver productos" y prepara tu pedido en pocos pasos.', altura=280)

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
        st.markdown("Completa tu pedido o genera un presupuesto y envíalo cuando esté todo correcto.")
    with c2:
        render_aply(APLY_CARRITO, "Revisa tu pedido y no olvides indicar tu nombre y tu teléfono.", altura=230)

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
            tipo_salida = st.radio(
                "Tipo de documento",
                ["Pedido", "Presupuesto sin imágenes", "Presupuesto con imágenes"],
                index=0,
                key="tipo_documento_salida",
            )
            comentarios = st.text_area(
                "Observaciones",
                key="pedido_observaciones",
                placeholder="Si es tu primera compra añade tus datos para facturar (CIF/NIF, Nombre, Dirección)"
            )
            config_doc = obtener_configuracion_documento(tipo_salida)
            enviar = st.form_submit_button(config_doc["boton"])

            if enviar:
                nombre_limpio = nombre.strip()
                telefono_limpio = telefono.strip()

                if not nombre_limpio or not telefono_limpio:
                    if not nombre_limpio and not telefono_limpio:
                        aviso = f"Faltan nombre y teléfono para poder enviar el {config_doc['titulo'].lower()}."
                    elif not nombre_limpio:
                        aviso = f"Falta el nombre para poder enviar el {config_doc['titulo'].lower()}."
                    else:
                        aviso = f"Falta el teléfono para poder enviar el {config_doc['titulo'].lower()}."

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
                    ruta_pdf = config_doc["archivo"]
                    resumen_txt = (
                        f"{config_doc['titulo']} enviado por: {nombre_limpio}\n"
                        f"Telefono: {telefono_limpio}\n"
                        f"Modalidad: {tipo_salida}\n\n{resumen}\n"
                        f"Total: {total:.2f} euros (IVA incluido)\n\nComentarios: {comentarios}"
                    )
                    generar_pdf(
                        nombre_limpio,
                        resumen,
                        total,
                        comentarios,
                        ruta_pdf,
                        tipo_documento=config_doc["tipo_documento"],
                        incluir_imagenes=config_doc["incluir_imagenes"],
                        carrito=st.session_state.carrito,
                        telefono=telefono_limpio,
                    )
                    enviar_documento_por_email(
                        config_doc["asunto"],
                        resumen_txt,
                        ruta_pdf,
                        nombre_adjunto=config_doc["archivo"],
                    )
                    st.success(config_doc["success"])
                    st.session_state.pdf_generado = True
                    st.session_state.ultimo_pdf_path = ruta_pdf
                    st.session_state.ultimo_pdf_nombre = config_doc["archivo"]
                    st.session_state.ultimo_pdf_boton = config_doc["download"]
                    st.session_state.carrito = []

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.session_state.pdf_generado and st.session_state.get("ultimo_pdf_path") and Path(st.session_state["ultimo_pdf_path"]).exists():
                with open(st.session_state["ultimo_pdf_path"], "rb") as f:
                    st.download_button(
                        st.session_state.get("ultimo_pdf_boton", "📄 Descargar PDF"),
                        f,
                        file_name=st.session_state.get("ultimo_pdf_nombre", "documento.pdf"),
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


def render_rejilla_subfamilias_celulosas():
    items = []
    for subfamilia, _archivo in CELULOSAS_SUBFAMILIAS_ORDENADAS:
        img = obtener_ruta_imagen_subfamilia_celulosas(subfamilia)
        items.append({
            "href": qp_url(pantalla="catalogo", familia="Celulosas", subfamilia=subfamilia),
            "alt": subfamilia,
            "img": imagen_data_uri(img) if img and img.exists() else None,
            "fallback": subfamilia,
        })
    render_rejilla_component(items)


def render_rejilla_subfamilias_utiles():
    items = []
    for subfamilia, _archivo in UTILES_SUBFAMILIAS_ORDENADAS:
        img = obtener_ruta_imagen_subfamilia_utiles(subfamilia)
        items.append({
            "href": qp_url(pantalla="catalogo", familia="Útiles", subfamilia=subfamilia),
            "alt": subfamilia,
            "img": imagen_data_uri(img) if img and img.exists() else None,
            "fallback": subfamilia,
        })
    render_rejilla_component(items)


def render_rejilla_subfamilias_desechables():
    items = []
    for subfamilia, _archivo in DESECHABLES_SUBFAMILIAS_ORDENADAS:
        img = obtener_ruta_imagen_subfamilia_desechables(subfamilia)
        items.append({
            "href": qp_url(pantalla="catalogo", familia="Desechables", subfamilia=subfamilia),
            "alt": subfamilia,
            "img": imagen_data_uri(img) if img and img.exists() else None,
            "fallback": subfamilia,
        })
    render_rejilla_component(items)


def render_rejilla_subfamilias_equipamiento():
    items = []
    for subfamilia, _archivo in EQUIPAMIENTO_SUBFAMILIAS_ORDENADAS:
        img = obtener_ruta_imagen_subfamilia_equipamiento(subfamilia)
        items.append({
            "href": qp_url(pantalla="catalogo", familia="Equipamiento", subfamilia=subfamilia),
            "alt": subfamilia,
            "img": imagen_data_uri(img) if img and img.exists() else None,
            "fallback": subfamilia,
        })
    render_rejilla_component(items)


def render_rejilla_subfamilias_maquinas():
    items = []
    for subfamilia, _archivo in MAQUINAS_SUBFAMILIAS_ORDENADAS:
        img = obtener_ruta_imagen_subfamilia_maquinas(subfamilia)
        items.append({
            "href": qp_url(pantalla="catalogo", familia="Máquinas", subfamilia=subfamilia),
            "alt": subfamilia,
            "img": imagen_data_uri(img) if img and img.exists() else None,
            "fallback": subfamilia,
        })
    render_rejilla_component(items)


def render_rejilla_subfamilias_otros():
    items = []
    for subfamilia, _archivo in OTROS_SUBFAMILIAS_ORDENADAS:
        img = obtener_ruta_imagen_subfamilia_otros(subfamilia)
        items.append({
            "href": qp_url(pantalla="catalogo", familia="Otros", subfamilia=subfamilia),
            "alt": subfamilia,
            "img": imagen_data_uri(img) if img and img.exists() else None,
            "fallback": subfamilia,
        })
    render_rejilla_component(items)


def render_rejilla_subfamilias_servicios():
    items = []
    for subfamilia, _archivo in SERVICIOS_SUBFAMILIAS_ORDENADAS:
        img = obtener_ruta_imagen_subfamilia_servicios(subfamilia)
        items.append({
            "href": qp_url(pantalla="catalogo", familia="Servicios", subfamilia=subfamilia),
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

    if st.session_state.familia_actual is None:
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
                            f"**Subfamilia:** {fila['Subfamilia']}  \n"
                            f"💶 **Precio sin IVA:** {precio_sin_iva:.2f} €  \n"
                            f"💰 **Precio con IVA:** {precio_con_iva:.2f} €"
                        )

                        tipo = st.radio(
                            "Formato",
                            FORMATOS,
                            horizontal=True,
                            key=f"tipo_fam_{fila['Código']}",
                            label_visibility="collapsed",
                        )

                        qty_actual = cantidades_carrito.get((str(fila["Código"]), str(tipo)), 0)
                        a1, a2, a3, a4 = st.columns([1, 1, 1.3, 1.5])
                        with a1:
                            if st.button("-1", key=f"menos_fam_{fila['Código']}_{tipo}", use_container_width=True):
                                quitar_del_carrito(fila["Código"], tipo, 1)
                                st.rerun()
                        with a2:
                            if st.button("+1", key=f"mas_fam_{fila['Código']}_{tipo}", use_container_width=True):
                                agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 1)
                                st.rerun()
                        with a3:
                            st.markdown(f"**En carrito:** {qty_actual}")
                        with a4:
                            if st.button("Añadir 5", key=f"add5_fam_{fila['Código']}_{tipo}", use_container_width=True):
                                agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 5)
                                st.rerun()

            render_aply(APLY_SENALA, "Elige una subfamilia para ver los productos.", altura=190)
            if familia_actual == "Químicos":
                st.markdown("### Selecciona una subfamilia")
                render_rejilla_subfamilias_quimicos()
                return
            if familia_actual == "Celulosas":
                st.markdown("### Selecciona una subfamilia")
                render_rejilla_subfamilias_celulosas()
                return
            if familia_actual == "Útiles":
                st.markdown("### Selecciona una subfamilia")
                render_rejilla_subfamilias_utiles()
                return
            if familia_actual == "Desechables":
                st.markdown("### Selecciona una subfamilia")
                render_rejilla_subfamilias_desechables()
                return
            if familia_actual == "Equipamiento":
                st.markdown("### Selecciona una subfamilia")
                render_rejilla_subfamilias_equipamiento()
                return
            if familia_actual == "Máquinas":
                st.markdown("### Selecciona una subfamilia")
                render_rejilla_subfamilias_maquinas()
                return
            if familia_actual == "Otros":
                st.markdown("### Selecciona una subfamilia")
                render_rejilla_subfamilias_otros()
                return
            if familia_actual == "Servicios":
                st.markdown("### Selecciona una subfamilia")
                render_rejilla_subfamilias_servicios()
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

    st.markdown(
        """
        <style>
        .aply-producto-compacto {
            border:1px solid #e6efe2;
            border-radius:18px;
            padding:.7rem .75rem;
            margin:.45rem 0;
            background:#ffffff;
            box-shadow:0 5px 14px rgba(0,0,0,.04);
        }
        .aply-producto-compacto .nombre {
            font-weight:700;
            color:#1f2a1f;
            line-height:1.2;
            margin-bottom:.2rem;
            font-size:1rem;
        }
        .aply-producto-compacto .meta {
            color:#4e5f50;
            font-size:.92rem;
            line-height:1.35;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cantidades_carrito = construir_mapa_cantidades_carrito()

    for _, fila in productos.iterrows():
        precio_con_iva = float(fila["Precio"])
        precio_sin_iva = precio_con_iva / (1 + IVA) if precio_con_iva else 0
        ruta_img = obtener_ruta_imagen_producto(fila["Código"])

        st.markdown('<div class="aply-producto-compacto">', unsafe_allow_html=True)
        c1, c2 = st.columns([0.9, 3.2])

        with c1:
            if ruta_img:
                st.image(ruta_img, width=95)
            else:
                st.markdown(
                    """
                    <div style="width:95px;height:95px;border-radius:14px;background:linear-gradient(135deg,#f8fbf8,#eef7eb);display:flex;align-items:center;justify-content:center;font-size:2rem;border:1px solid #e6efe2;">📦</div>
                    """,
                    unsafe_allow_html=True,
                )

        with c2:
            st.markdown(
                f"""
                <div class="nombre">{fila['Nombre']}</div>
                <div class="meta">
                    Código: {fila['Código']}<br>
                    Sin IVA: {precio_sin_iva:.2f} € · Con IVA: {precio_con_iva:.2f} €
                </div>
                """,
                unsafe_allow_html=True,
            )

            s1, s2, s3, s4 = st.columns([1.35, 0.9, 0.9, 1.15])
            with s1:
                tipo = st.selectbox(
                    "Formato",
                    FORMATOS,
                    key=f"tipo_{fila['Código']}",
                    label_visibility="collapsed",
                )
            qty_actual = cantidades_carrito.get((str(fila["Código"]), str(tipo)), 0)
            with s2:
                if st.button("-1", key=f"menos_{fila['Código']}_{tipo}", use_container_width=True):
                    quitar_del_carrito(fila["Código"], tipo, 1)
                    st.rerun()
            with s3:
                if st.button("+1", key=f"mas_{fila['Código']}_{tipo}", use_container_width=True):
                    agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 1)
                    st.rerun()
            with s4:
                if st.button("Añadir 5", key=f"add5_{fila['Código']}_{tipo}", use_container_width=True):
                    agregar_o_sumar_al_carrito(fila["Código"], fila["Nombre"], tipo, precio_con_iva, 5)
                    st.rerun()

            st.caption(f"En carrito: {qty_actual} {tipo}")

        st.markdown('</div>', unsafe_allow_html=True)


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
if "ultimo_pdf_path" not in st.session_state:
    st.session_state.ultimo_pdf_path = ""
if "ultimo_pdf_nombre" not in st.session_state:
    st.session_state.ultimo_pdf_nombre = ""
if "ultimo_pdf_boton" not in st.session_state:
    st.session_state.ultimo_pdf_boton = "📄 Descargar PDF"

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
