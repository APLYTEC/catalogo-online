import streamlit as st

st.set_page_config(page_title="Prueba Google Sheets APLYTEC", page_icon="✅")

SHEET_ID = "1-lRMkBoIiu0o61Hoex-ecjbuwChOABD8JV-yLC9qRAQ"
SHEET_TAB = "Pedidos"

st.title("Prueba de conexión Google Sheets")
st.write("Esta pantalla no envía pedidos ni modifica la hoja.")

try:
    import gspread
    from google.oauth2.service_account import Credentials

    if "gcp_service_account" not in st.secrets:
        st.error("No existe la sección [gcp_service_account] en Streamlit Secrets.")
        st.stop()

    info = dict(st.secrets["gcp_service_account"])

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(info, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    worksheet = sheet.worksheet(SHEET_TAB)

    st.success("✅ CONEXIÓN CORRECTA")
    st.write(f"Hoja encontrada: **{sheet.title}**")
    st.write(f"Pestaña encontrada: **{worksheet.title}**")
    st.write("La cuenta de servicio puede acceder correctamente a Google Sheets.")

except ModuleNotFoundError as e:
    st.error("Falta una librería en requirements.txt.")
    st.code(str(e))
    st.info("Asegúrate de tener gspread y google-auth en requirements.txt.")

except Exception as e:
    st.error("❌ No se pudo conectar con Google Sheets.")
    st.write("Detalle técnico:")
    st.code(f"{type(e).__name__}: {e}")
