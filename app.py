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

# Leer todo el texto del PDF y líneas
txt = ''
with pdfplumber.open(uploaded) as pdf:
    for page in pdf.pages:
        txt += (page.extract_text() or '') + '\n'
lines = [l.rstrip() for l in txt.split('\n')]

# Paso 1: Detectar los 4 sistemas y agrupar fórmulas
desired_systems = ["M/M/1", "Erlang C", "M/M/c/k", "Erlang B"]
# Lista de (name, index)
sys_positions = []
for i, line in enumerate(lines):
    for name in desired_systems:
        if re.search(rf"(?:Sistema\s+)?{re.escape(name)}", line, re.IGNORECASE):
            if name not in [s for s,_ in sys_positions]:
                sys_positions.append((name, i))
# Ordenar por aparición en el documento
sys_positions = sorted(sys_positions, key=lambda x: x[1])

# Extraer fórmulas por sistema
systems_formulas = {}
for idx, (name, start) in enumerate(sys_positions):
    end = sys_positions[idx+1][1] if idx+1 < len(sys_positions) else len(lines)
    block = lines[start+1:end]
    # Considerar fórmula si contiene operador matemático
    ops = ['=', '+', '-', '*', '/', '^', '√', '∑', '∫', '∂', 'lim']
    formulas = [ln.strip() for ln in block if any(op in ln for op in ops) and ln.strip()]
    systems_formulas[name] = formulas

# Paso 2: Mostrar modo Estudio con selección de sistema
st.header("📚 Modo Estudio: Explora tus sistemas")
if systems_formulas:
    system = st.selectbox("Elige un sistema:", list(systems_formulas.keys()))
    st.write(f"**Sistema seleccionado:** {system}")
    formulas = systems_formulas[system]
    if formulas:
        for i, formula in enumerate(formulas, 1):
            with st.expander(f"Fórmula {i}"):
                try:
                    st.latex(formula)
                except:
                    st.code(formula)
    else:
        st.warning(f"No se encontraron fórmulas para {system}.")
else:
    st.warning("No se detectaron sistemas válidos en el PDF.")

# Fin del prototipo de modo Estudio

# En siguientes pasos implementaremos Práctica, descripciones y más funcionalidades.

