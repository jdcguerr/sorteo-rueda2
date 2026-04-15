import streamlit as st
import random
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sorteo Validado", page_icon="🔒")

# --- DATOS MAESTROS ---
USUARIOS_PERMITIDOS = [
    "Johanna", "Ana", "Vanessa", "Carlota", "Olga", 
    "Norma", "Irene", "Charles", "Teresa", "Lourdes", 
    "Lourdes2", "Jenny", "Elke", "Jhanneth", "Olga2"
]

MESES_INICIALES = [
    "Abril", "Mayo", "Junio", "Julio", "Agosto", 
    "Septiembre", "Octubre", "Noviembre", "Diciembre", 
    "Enero", "Febrero", "Marzo", "Abril2", "Mayo2", "Junio2"
]

# --- INICIALIZACIÓN DEL ESTADO ---
if 'datos_ruleta' not in st.session_state:
    st.session_state.datos_ruleta = MESES_INICIALES.copy()

if 'resultados' not in st.session_state:
    st.session_state.resultados = {}  # Formato: {"Nombre": "Mes"}

# --- INTERFAZ ---
st.title("🎡 Rueda de Asignación con Validación")
st.write("Ingrese su nombre para realizar su lanzamiento único.")

# Campo de entrada para validación
nombre_usuario = st.text_input("Escriba su nombre exactamente como está registrado:").strip()

if st.button("🎰 REALIZAR LANZAMIENTO"):
    if not nombre_usuario:
        st.warning("Por favor, ingrese un nombre.")
    
    # 1. Validar si el usuario existe en la lista
    elif nombre_usuario not in USUARIOS_PERMITIDOS:
        st.error("❌ Usuario no existe")
    
    # 2. Validar si el usuario ya realizó su lanzamiento
    elif nombre_usuario in st.session_state.resultados:
        st.warning(f"⚠️ El usuario '{nombre_usuario}' ya realizó el lanzamiento.")
        st.info(f"Tu resultado fue: {st.session_state.resultados[nombre_usuario]}")
    
    # 3. Realizar el lanzamiento si todo es correcto
    else:
        if len(st.session_state.datos_ruleta) > 0:
            with st.spinner("Girando la rueda..."):
                time.sleep(1.5)
                seleccion = random.choice(st.session_state.datos_ruleta)
                
                # Guardar resultado y eliminar de la rueda
                st.session_state.resultados[nombre_usuario] = seleccion
                st.session_state.datos_ruleta.remove(seleccion)
                
                st.success(f"¡Excelente {nombre_usuario}! Tu mes asignado es: {seleccion}")
        else:
            st.error("La rueda está vacía. Todos los meses han sido asignados.")

# --- SECCIÓN DE RESULTADOS ACUMULADOS ---
st.divider()
st.subheader("📋 Estado del Sorteo")

col1, col2 = st.columns([2, 1])

with col1:
    st.write("**Lista de resultados actuales:**")
    if st.session_state.resultados:
        for user, mes in st.session_state.resultados.items():
            st.write(f"✅ {user} → {mes}")
    else:
        st.write("Aún no hay lanzamientos registrados.")

with col2:
    st.write("**Meses restantes:**")
    st.write(len(st.session_state.datos_ruleta))
    if st.checkbox("Ver meses disponibles"):
        st.write(st.session_state.datos_ruleta)

# --- CIERRE DEL SORTEO ---
if len(st.session_state.resultados) == len(USUARIOS_PERMITIDOS):
    st.balloons()
    st.success("¡Sorteo finalizado! Todos los usuarios han recibido su mes.")
    
    # Botón oculto para reiniciar (opcional, útil para pruebas)
    if st.button("Reiniciar Sistema"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()