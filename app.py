import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
import json
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sorteo en Tiempo Real", layout="centered")

# --- CONEXIÓN A LA BASE DE DATOS ---
# Las credenciales se configuran en los "Secrets" de Streamlit Cloud
if "textkey" in st.secrets:
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds)
else:
    st.error("Configuración de base de datos no encontrada.")
    st.stop()

doc_ref = db.collection("sorteos").document("rueda_oficial")

# --- FUNCIONES DE BASE DE DATOS ---
def inicializar_o_leer_datos():
    doc = doc_ref.get()
    if not doc.exists:
        # Si es la primera vez, creamos el estado inicial
        datos_iniciales = {
            "usuarios_permitidos": ["Johanna", "Ana", "Vanessa", "Carlota", "Olga", "Norma", "Irene", "Charles", "Teresa", "Lourdes", "Lourdes2", "Jenny", "Elke", "Jhanneth", "Olga2"],
            "meses_disponibles": ["Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre", "Enero", "Febrero", "Marzo", "Abril2", "Mayo2", "Junio2"],
            "resultados": {}
        }
        doc_ref.set(datos_iniciales)
        return datos_iniciales
    return doc.to_dict()

# --- INTERFAZ DE USUARIO ---
st.title("🎡 Sorteo Institucional en Vivo")
st.write("Todos los participantes verán las actualizaciones en tiempo real.")

estado = inicializar_o_leer_datos()

# Entrada de usuario
nombre_ingresado = st.text_input("Ingresa tu nombre para validar:").strip()

if st.button("🎰 GIRAR RULETA"):
    # Volvemos a leer la base de datos para estar seguros de que nadie ganó el mes hace un segundo
    estado = inicializar_o_leer_datos()
    
    if nombre_ingresado not in estado["usuarios_permitidos"]:
        st.error("❌ Usuario no existe en la lista oficial.")
    
    elif nombre_ingresado in estado["resultados"]:
        st.warning(f"⚠️ {nombre_ingresado}, ya realizaste tu lanzamiento.")
        st.info(f"Tu mes asignado es: {estado['resultados'][nombre_ingresado]}")
    
    elif len(estado["meses_disponibles"]) == 0:
        st.error("No quedan meses disponibles en la rueda.")
    
    else:
        # Proceso de sorteo
        seleccion = random.choice(estado["meses_disponibles"])
        
        # Actualización atómica en la base de datos
        estado["resultados"][nombre_ingresado] = seleccion
        estado["meses_disponibles"].remove(seleccion)
        
        doc_ref.update({
            "resultados": estado["resultados"],
            "meses_disponibles": estado["meses_disponibles"]
        })
        
        st.success(f"¡Felicidades {nombre_ingresado}! Has obtenido: {seleccion}")
        st.balloons()

# --- PANEL DE CONTROL EN TIEMPO REAL ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Resultados")
    if estado["resultados"]:
        for user, mes in estado["resultados"].items():
            st.write(f"👤 **{user}** → 📅 {mes}")
    else:
        st.write("Esperando lanzamientos...")

with col2:
    st.subheader("🎡 En la rueda")
    st.write(f"Quedan **{len(estado['meses_disponibles'])}** meses.")
    st.caption(", ".join(estado["meses_disponibles"]))

# Botón para forzar actualización visual
if st.button("🔄 Refrescar Pantalla"):
    st.rerun()
