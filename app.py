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
elif mode == "Práctica":
    st.header('✍️ Modo Práctica')
    if not systems:
        st.warning('No se detectaron sistemas en el PDF.')
    else:
        # Selección horizontal de sistema
        st.write('**Elige tu sistema para practicar:**')
        cols = st.columns(len(systems))
        if 'practice_system' not in st.session_state:
            for col, sys in zip(cols, systems.keys()):
                if col.button(sys):
                    st.session_state.practice_system = sys
                    st.session_state.idx = random.randrange(len(systems[sys]))
                    st.session_state.resp = {}
                    st.session_state.attempts = {}
            st.stop()
        practice_system = st.session_state.practice_system
        st.markdown(f'**Sistema seleccionado:** {practice_system}')

        # Dificultad
        levels = {'Fácil': 1, 'Medio': 2, 'Difícil': 4}
        difficulty = st.select_slider('Nivel de dificultad:', options=list(levels.keys()), value='Medio')
        max_huecos = levels[difficulty]

        # Obtener fórmula y tokens
        formulas = systems[practice_system]
        idx = st.session_state.idx % len(formulas)
        latex = formulas[idx]
        tokens = re.findall(r"\w+|\S", latex)
        n_huecos = min(max_huecos, len(tokens))
        # Determinar posiciones de huecos si es primera vez
        if 'blanks' not in st.session_state or st.session_state.idx_changed:
            blanks = random.sample(range(len(tokens)), n_huecos)
            st.session_state.blanks = blanks
            st.session_state.idx_changed = False
            # inicializar intentos por hueco
            for b in blanks:
                st.session_state.attempts[b] = 3
        blanks = st.session_state.blanks

        # Construir display con inputs inline
        filled = []
        for i, tok in enumerate(tokens):
            if i in blanks:
                # mostrar input en línea para cada hueco
                input_key = f'hueco_{i}'
                val = st.session_state.resp.get(input_key, '')
                # determinar color según estado
                attempts_left = st.session_state.attempts.get(i, 3)
                is_correct = (val == tokens[i])
                color = 'lightgreen' if is_correct else ('lightcoral' if attempts_left < 3 else 'white')
                filled.append(st.text_input(f'', value=val, key=input_key, label_visibility='collapsed', help=f'Intentos restantes: {attempts_left}', args={'style': f'background-color: {color}'}))
            else:
                filled.append(tok)
        # Mostrar la fórmula con inputs
        st.markdown("**Completa la fórmula:**")
        st.code(' '.join(filled))

        # Teclado especial: griegas y operadores
        special = ['α','β','γ','δ','ε','λ','μ','ρ','θ','Σ','∑','∫','∂','∇','+','-','*','/','^','=']
        st.write('## Teclado Especial')
        for row in [special[:9], special[9:]]:
            cols_sp = st.columns(len(row))
            for c, ch in zip(cols_sp, row):
                if c.button(ch):
                    # añade carácter en último hueco seleccionado
                    # encontrar último input key
                    last = max(st.session_state.blanks)
                    key = f'hueco_{last}'
                    st.session_state.resp[key] = st.session_state.resp.get(key, '') + ch
                    st.experimental_rerun()

        # Comprobar
        if st.button('Comprobar respuestas'):
            correct = 0
            for b in blanks:
                key = f'hueco_{b}'
                ans = st.session_state.resp.get(key, '')
                if ans == tokens[b]:
                    correct += 1
                else:
                    st.session_state.attempts[b] -= 1
            mistakes = len(blanks) - correct
            st.write(f'Aciertos: {correct}/{len(blanks)}')

            # mostrar colores actualizados
            st.session_state.idx_changed = False

        # Siguiente
        if st.button('Siguiente fórmula'):
            st.session_state.idx = (st.session_state.idx + 1) % len(formulas)
            st.session_state.idx_changed = True
            st.session_state.resp = {}
            st.stop()
