
import streamlit as st
import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage
from fpdf import FPDF
from pathlib import Path

# Generar PDF del pedido
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
    pdf.cell(0, 10, f"Total del pedido: {total:.2f} euros", ln=True)
    if comentarios:
        pdf.ln(10)
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 10, f"Comentarios: {comentarios}")
    pdf.output(output_path)

# Enviar correo con PDF adjunto
def enviar_pedido_por_email(destinatario, asunto, cuerpo, adjunto_path):
    remitente = "jguzmanraya@gmail.com"
    password = "utjb tfrt oqis bzcg"

    msg = EmailMessage()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.set_content(cuerpo)

    with open(adjunto_path, "rb") as f:
        pdf_data = f.read()
    msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename="resumen_pedido.pdf")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(remitente, password)
        server.send_message(msg)

# Funciones auxiliares
@st.cache_data
def cargar_datos():
    df = pd.read_excel("PRUEBA.xlsx")
    df = df.rename(columns={"CÓDIGO": "Código", "NOMBRE": "Nombre", "PRECIO": "Precio"})
    return df

def obtener_ruta_imagen(codigo):
    extensiones = [".jpg", ".jpeg", ".png"]
    for ext in extensiones:
        ruta = Path("imagenes") / f"{codigo}{ext}"
        if ruta.exists():
            return str(ruta)
    return None
