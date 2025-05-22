# -*- coding: utf-8 -*-
import streamlit as st
import pdfplumber, re, random

# Configuración de la página
st.set_page_config(page_title="Flashcards Dinámicas", layout="wide")
st.title("📄 Flashcards de Fórmulas Dinámicas")

# Paso 0: Subida de PDF
uploaded = st.file_uploader("1) Sube tu PDF de fórmulas", type=["pdf"])
if not uploaded:
    st.info("Por favor, sube un PDF con fórmulas para comenzar.")
    st.stop()

# Extraer texto y líneas
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
positions.sort(key=lambda x: x[1])
ops = ['=', '+', '-', '*', '/', '^', '√', '∑', '∫', '∂', 'lim']
systems = {}
for i, (name, start) in enumerate(positions):
    end = positions[i+1][1] if i+1 < len(positions) else len(lines)
    block = lines[start+1:end]
    systems[name] = [ln.strip() for ln in block if any(op in ln for op in ops) and ln.strip()]

# Paso 2: Selección de modo
mode = st.radio("Selecciona modo:", ["Estudio", "Práctica"], horizontal=True)

# ------------------ MODO ESTUDIO ------------------
if mode == "Estudio":
    st.header("📚 Modo Estudio")
    if not systems:
        st.warning("No se detectaron sistemas en el PDF.")
    else:
        system = st.selectbox("Elige un sistema para estudio:", list(systems.keys()))
        st.markdown(f"**Sistema seleccionado:** {system}")
        # (despliegue de fórmulas como antes)
        # ... código de despliegue existente ...

# ------------------ MODO PRÁCTICA ------------------
# ------------------ MODO PRÁCTICA ------------------
elif mode == "Práctica":
    st.header("✍️ Modo Práctica")

    if not systems:
        st.warning("No se detectaron sistemas en el PDF.")
    else:
        # 1) Selección horizontal de sistema
        st.write("**Elige tu sistema para practicar:**")
        cols = st.columns(len(systems))
        # Si no hay sistema en estado, muestro botones
        if "practice_system" not in st.session_state:
            for col, sys in zip(cols, systems.keys()):
                if col.button(sys):
                    st.session_state.practice_system = sys
                    st.session_state.idx = random.randrange(len(systems[sys]))
        # Si ya elegimos sistema
        if "practice_system" in st.session_state:
            practice_system = st.session_state.practice_system
            st.markdown(f"**Sistema seleccionado:** {practice_system}")
            
            # 2) Obtener fórmula y crear huecos
            formulas = systems[practice_system]
            idx = st.session_state.idx % len(formulas)
            latex = formulas[idx]
            st.latex(latex)

            tokens = re.findall(r"\w+|\S", latex)
            # dos huecos fijos, o ajusta aquí
            blanks = random.sample(range(len(tokens)), min(2, len(tokens)))
            answers = [tokens[i] for i in blanks]
            for i in blanks:
                tokens[i] = "___"
            st.markdown("**Rellena los huecos:**")
            st.code(" ".join(tokens))

            # 3) Área de respuesta y teclado griego
            if "resp" not in st.session_state:
                st.session_state.resp = ""
            st.session_state.resp = st.text_area("Tu respuesta:", st.session_state.resp, height=80)
            greeks = ['α','β','γ','δ','ε','λ','μ','ρ','θ','Σ','∑','∫','∂','∇']
            cols2 = st.columns(len(greeks))
            for i, g in enumerate(greeks):
                if cols2[i].button(g):
                    st.session_state.resp += g

            # 4) Botón Comprobar y Siguiente
            colc, colsx = st.columns([1,1])
            if colc.button("Comprobar respuesta"):
                user = [u.strip() for u in st.session_state.resp.split(",")]
                correct = sum(u == a for u, a in zip(user, answers))
                mistakes = len(answers) - correct
                st.write(f"Aciertos: {correct}/{len(answers)} | Errores: {mistakes}")
            if colsx.button("Siguiente fórmula"):
                # Avanzar índice y limpiar respuesta
                st.session_state.idx = (st.session_state.idx + 1) % len(formulas)
                st.session_state.resp = ""

