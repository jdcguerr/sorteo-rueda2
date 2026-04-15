import streamlit as st
import random
import time
from google.cloud import firestore
from google.oauth2 import service_account
import json

# --- CONFIGURACIÓN DE FIRESTORE ---
# Debes subir las credenciales a Streamlit Secrets (explicado abajo)
if "textkey" in st.secrets:
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="tu-proyecto-id")
else:
    st.error("Error de configuración de base de datos.")
    st.stop()

# Referencia al documento único del sorteo
doc_ref = db.collection("sorteos").document("general")

# --- FUNCIONES DE SINCRONIZACIÓN ---
def obtener_estado():
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        # Estado inicial si la base de datos está vacía
        estado_inicial = {
            "datos_ruleta": ["Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre", "Enero", "Febrero", "Marzo", "Abril2", "Mayo2", "Junio2"],
            "resultados": {},
            "usuarios_permitidos": ["Johanna", "Ana", "Vanessa", "Carlota", "Olga", "Norma", "Irene", "Charles", "Teresa", "Lourdes", "Lourdes2", "Jenny", "Elke", "Jhanneth", "Olga2"]
        }
        doc_ref.set(estado_inicial)
        return estado_inicial

# --- INTERFAZ ---
st.title("🎡 Sorteo Sincronizado en Tiempo Real")
estado = obtener_estado()

nombre_usuario = st.text_input("Ingrese su nombre para participar:").strip()

if st.button("🎰 GIRAR RUEDA"):
    # Recargar estado para evitar conflictos
    estado = obtener_estado()
    
    if nombre_usuario not in estado["usuarios_permitidos"]:
        st.error("❌ Usuario no existe")
    elif nombre_usuario in estado["resultados"]:
        st.warning(f"⚠️ {nombre_usuario}, ya realizaste tu lanzamiento.")
        st.info(f"Tu resultado fue: {estado['resultados'][nombre_usuario]}")
    elif len(estado["datos_ruleta"]) == 0:
        st.error("Ya no quedan meses en la rueda.")
    else:
        with st.spinner("Girando para todos los participantes..."):
            time.sleep(1)
            seleccion = random.choice(estado["datos_ruleta"])
            
            # ACTUALIZAR EN LA NUBE
            estado["resultados"][nombre_usuario] = seleccion
            estado["datos_ruleta"].remove(seleccion)
            doc_ref.update({
                "resultados": estado["resultados"],
                "datos_ruleta": estado["datos_ruleta"]
            })
            
            st.success(f"¡{nombre_usuario}, has obtenido: {seleccion}!")
            st.balloons()

# --- VISUALIZACIÓN UNIFICADA ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Resultados Globales")
    for user, mes in estado["resultados"].items():
        st.write(f"✅ **{user}**: {mes}")

with col2:
    st.subheader("🎡 Quedan en la rueda")
    st.write(", ".join(estado["datos_ruleta"]))

if st.button("🔄 Actualizar Tabla"):
    st.rerun()
