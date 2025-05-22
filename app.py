# -*- coding: utf-8 -*-
import streamlit as st
import pdfplumber, re

# Configuración de la página
st.set_page_config(page_title="Flashcards Dinámicas", layout="wide")
st.title("📄 Flashcards de Fórmulas Dinámicas")

# Paso 0: Subida de PDF
uploaded = st.file_uploader("1) Sube tu PDF de fórmulas", type=["pdf"])
if not uploaded:
    st.info("Por favor, sube un PDF con fórmulas para comenzar.")
    st.stop()

# Leer todo el texto del PDF
txt = ''
with pdfplumber.open(uploaded) as pdf:
    for page in pdf.pages:
        txt += (page.extract_text() or '') + '\n'

# Paso 1: Detectar los 4 sistemas principales
desired_systems = ["M/M/1", "Erlang C", "M/M/c/k", "Erlang B"]
systems_found = []
for line in txt.split('\n'):
    stripped = line.strip()
    for name in desired_systems:
        # Coincidir nombre exacto, opcionalmente con "Sistema " delante
        if re.fullmatch(rf"(?:Sistema\s+)?{re.escape(name)}", stripped, re.IGNORECASE):
            if name not in systems_found:
                systems_found.append(name)

# Mostrar resultados en modo Estudio
st.header("📚 Modo Estudio: Sistemas Detectados")
if systems_found:
    st.write("Los siguientes sistemas han sido detectados en el PDF:")
    for sys in systems_found:
        st.markdown(f"- **{sys}**")
else:
    st.warning("No se detectó ninguno de los sistemas: M/M/1, Erlang C, M/M/c/k, Erlang B.")

# Para desarrollar: en futuros pasos agregaremos definiciones y fórmulas de cada sistema.  

        st.write(f"Aciertos: {correct}/{len(answers)} — Errores: {mistakes}")
        st.write("Respuestas correctas:", ", ".join(answers))
