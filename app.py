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

# Leer texto y líneas del PDF
txt = ''
with pdfplumber.open(uploaded) as pdf:
    for page in pdf.pages:
        txt += (page.extract_text() or '') + '\n'
lines = [l.rstrip() for l in txt.split('\n')]

# Paso 1: Detectar y agrupar sistemas deseados
desired_systems = ["M/M/1", "Erlang C", "M/M/c/k", "Erlang B"]
positions = []
for idx, line in enumerate(lines):
    for name in desired_systems:
        if re.search(rf"(?:Sistema\s+)?{re.escape(name)}", line, re.IGNORECASE):
            if name not in [s for s,_ in positions]:
                positions.append((name, idx))
positions = sorted(positions, key=lambda x: x[1])

# Extraer bloques de fórmulas por sistema
systems = {}
ops = ['=', '+', '-', '*', '/', '^', '√', '∑', '∫', '∂', 'lim']
for i, (name, start) in enumerate(positions):
    end = positions[i+1][1] if i+1 < len(positions) else len(lines)
    block = lines[start+1:end]
    formulas = [ln.strip() for ln in block if any(op in ln for op in ops) and ln.strip()]
    systems[name] = formulas

# Paso 2: Selección de modo
mode = st.radio("Selecciona modo:", ["Estudio", "Práctica"], horizontal=True)

if mode == "Estudio":
    st.header("📚 Modo Estudio: Explora tus sistemas detectados")
    if not systems:
        st.warning("No se detectaron sistemas en el PDF.")
    else:
        system = st.selectbox("Elige un sistema para estudio:", list(systems.keys()))
        st.markdown(f"**Sistema seleccionado:** {system}")
        # Aquí va el despliegue de fórmulas por sistema (igual que antes)
        if system == "M/M/1":
            mm1 = [
                ("Utilización (ρ)", r"\rho = \frac{\lambda}{\mu}"),
                ("Probabilidad sistema vacío (p₀)", r"p_0 = 1 - \rho"),
                ("Probabilidad de k clientes (p_k)", r"p_k = (1 - \rho)\rho^k"),
                ("Clientes en sistema (L)", r"L = \frac{\rho}{1 - \rho}"),
                ("Clientes en cola (L_q)", r"L_q = \frac{\rho^2}{1 - \rho}"),
                ("Tiempo en sistema (W)", r"W = \frac{1}{\mu - \lambda}"),
                ("Tiempo en cola (W_q)", r"W_q = \frac{\lambda}{\mu(\mu - \lambda)}")
            ]
            for title, latex in mm1:
                with st.expander(title, expanded=False):
                    st.latex(latex)
        else:
            formulas = systems.get(system, [])
            if not formulas:
                st.warning(f"No se encontraron fórmulas para {system}.")
            else:
                for i, f in enumerate(formulas, 1):
                    with st.expander(f"Fórmula {i}", expanded=False):
                        try:
                            st.latex(f)
                        except:
                            st.code(f)

elif mode == "Práctica":
    st.header("✍️ Modo Práctica: Elige un sistema")
    if not systems:
        st.warning("No se detectaron sistemas en el PDF.")
    else:
        practice_system = st.selectbox("Elige un sistema para practicar:", list(systems.keys()))
        st.write(f"Preparando práctica para: **{practice_system}**")
        # Aquí añadiremos las preguntas interactivas según el sistema seleccionado
        st.info("(En próximas iteraciones aparecerán las flashcards de práctica para este sistema.)")
# Fin de la app

