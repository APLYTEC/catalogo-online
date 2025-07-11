
import streamlit as st

# Simular productos (en la versión final se cargan desde Excel)
productos = [
    {
        "nombre": "LIMPIADOR DESINFECTANTE DETERBOT-G 5L",
        "codigo": "109120104",
        "descripcion": "Detergente desincrustante para uso profesional en limpieza industrial.",
        "precio": "5,70",
        "imagen": "109120104.jpg"
    },
    {
        "nombre": "LIMPIADOR DESINFECTANTE FRESC 5 L",
        "codigo": "109125050",
        "descripcion": "Ambientador concentrado de larga duración, ideal para oficinas y espacios cerrados.",
        "precio": "10,42",
        "imagen": "109125050.jpg"
    }
]

st.set_page_config(page_title="Catálogo de Productos", layout="wide")

st.title("🧼 Catálogo Interactivo de Productos")
st.markdown("Visualiza y selecciona productos. Al final, envía el pedido por **WhatsApp o correo electrónico**.")

carrito = []

for producto in productos:
    with st.container():
        cols = st.columns([1, 2])
        with cols[0]:
            st.image(producto["imagen"], width=150)
        with cols[1]:
            st.subheader(f"{producto['nombre']} ({producto['codigo']})")
            st.write(producto["descripcion"])
            st.markdown(f"**Precio:** {producto['precio']} EUR")
            cantidad = st.number_input(f"Cantidad de {producto['codigo']}", min_value=0, max_value=100, value=0, key=producto['codigo'])
            if cantidad > 0:
                carrito.append({
                    "producto": producto,
                    "cantidad": cantidad
                })

st.markdown("---")
st.header("🛒 Resumen del pedido")

if carrito:
    total = 0
    for item in carrito:
        nombre = item['producto']['nombre']
        precio = float(item['producto']['precio'].replace(",", "."))
        cantidad = item['cantidad']
        subtotal = precio * cantidad
        total += subtotal
        st.write(f"{nombre} x {cantidad} = {subtotal:.2f} EUR")

    st.subheader(f"💰 Total: {total:.2f} EUR")

    nombre_usuario = st.text_input("Tu nombre o empresa")
    contacto = st.text_input("Teléfono o email de contacto")

    if st.button("📲 Enviar por WhatsApp"):
        mensaje = f"Hola, quiero hacer un pedido:\n"
        for item in carrito:
            mensaje += f"- {item['producto']['nombre']} x {item['cantidad']}\n"
        mensaje += f"Total: {total:.2f} EUR\n"
        if nombre_usuario:
            mensaje += f"Nombre: {nombre_usuario}\n"
        if contacto:
            mensaje += f"Contacto: {contacto}"
        mensaje_encoded = mensaje.replace(" ", "%20").replace("\n", "%0A")
        url = f"https://wa.me/34TU_NUMERO?text={mensaje_encoded}"
        st.markdown(f"[Haz clic aquí para abrir WhatsApp]({url})")

    if st.button("✉️ Enviar por correo"):
        asunto = "Pedido desde catálogo"
        cuerpo = mensaje.replace("\n", "%0D%0A").replace(" ", "%20")
        mailto = f"mailto:ventas@tuempresa.com?subject={asunto}&body={cuerpo}"
        st.markdown(f"[Haz clic aquí para enviar un correo]({mailto})")
else:
    st.info("Selecciona cantidades para añadir productos al pedido.")
