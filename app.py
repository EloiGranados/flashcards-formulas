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
txt = ""
with pdfplumber.open(uploaded) as pdf:
    for page in pdf.pages:
        txt += (page.extract_text() or "") + "\n"
lines = [l.rstrip() for l in txt.split("\n")]

# Paso 1: Detectar sistemas
desired_systems = ["M/M/1", "Erlang C", "M/M/c/k", "Erlang B"]
positions = []
for idx, line in enumerate(lines):
    for name in desired_systems:
        if re.search(rf"(?:Sistema\s+)?{re.escape(name)}", line, re.IGNORECASE):
            if name not in [s for s,_ in positions]:
                positions.append((name, idx))
positions.sort(key=lambda x: x[1])

# Extraer fórmulas genéricas
ops = ['=', '+', '-', '*', '/', '^', '√', '∑', '∫', '∂', 'lim']
systems = {}
for i, (name, start) in enumerate(positions):
    end = positions[i+1][1] if i+1 < len(positions) else len(lines)
    block = lines[start+1:end]
    formulas = [ln.strip() for ln in block if any(op in ln for op in ops) and ln.strip()]
    systems[name] = formulas

# Paso 2: Selección de modo
mode = st.radio("Selecciona modo:", ["Estudio", "Práctica"], horizontal=True)

if mode == "Estudio":
    st.header("📚 Modo Estudio")
    if not systems:
        st.warning("No se detectaron sistemas en el PDF.")
        st.stop()

    system = st.selectbox("Elige un sistema para estudio:", list(systems.keys()))
    st.markdown(f"**Sistema seleccionado:** {system}")

    # Despliegue fijo por sistema
    if system == "M/M/1":
        mm1 = [
            ("Utilización (ρ)", r"\rho = \frac{\lambda}{\mu}"),
            ("Probabilidad sistema vacío (p₀)", r"p_0 = 1 - \rho"),
            ("Probabilidad de k clientes (p_k)", r"p_k = (1 - \rho)\,\rho^k"),
            ("Clientes en sistema (L)", r"L = \frac{\rho}{1 - \rho}"),
            ("Clientes en cola (L_q)", r"L_q = \frac{\rho^2}{1 - \rho}"),
            ("Tiempo en sistema (W)", r"W = \frac{1}{\mu - \lambda}"),
            ("Tiempo en cola (W_q)", r"W_q = \frac{\lambda}{\mu\,(\mu - \lambda)}"),
        ]
        for title, latex in mm1:
            with st.expander(title):
                st.latex(latex)

    elif system == "Erlang C":
        ec = [
            ("Carga total (r)", r"r = \frac{\lambda}{\mu}"),
            ("Utilización por servidor (ρ)", r"\rho = \frac{r}{c}"),
            ("Probabilidad de n clientes (p_n)", 
             r"p_n = \begin{cases}"
             r"\frac{r^n}{n!}\,p_0 & n < c \\[6pt]"
             r"\frac{r^n}{c!\,(n-c)!}\,p_0 & n \ge c"
             r"\end{cases}"),
            ("Probabilidad sistema vacío (p₀)",
             r"p_0 = \left[\sum_{n=0}^{c-1}\frac{r^n}{n!} + \sum_{n=c}^K\frac{r^n}{c!\,(n-c)!}\right]^{-1}"),
            ("Probabilidad de rechazo (p_K)", r"P_{\text{rechazo}} = p_K"),
            ("Tasa efectiva de llegada (λ_eff)", r"\lambda_{\text{ef}} = \lambda\,(1 - p_K)"),
            ("Número medio en sistema (L)", r"L = \sum_{n=0}^K n\,p_n"),
            ("Tiempo medio en sistema (W)", r"W = \frac{L}{\lambda_{\text{ef}}}"),
            ("Número medio en cola (L_q)", r"L_q = \sum_{n=c}^K (n-c)\,p_n"),
            ("Tiempo de espera en cola (W_q)", r"W_q = W - \frac{1}{\mu}"),
        ]
        for title, latex in ec:
            with st.expander(title):
                st.latex(latex)

    elif system == "M/M/c/k":
        mmck = [
            ("Carga total (r)", r"r = \frac{\lambda}{\mu}"),
            ("Probabilidad de n clientes (p_n)",
             r"p_n = \begin{cases}"
             r"\frac{(c\,\rho)^n}{n!}\,p_0 & n \le c \\[6pt]"
             r"\frac{c^c\,\rho^n}{c!\,(n-c)!}\,p_0 & c < n \le k"
             r"\end{cases}"),
            ("Probabilidad sistema vacío (p₀)",
             r"p_0 = \left[\sum_{n=0}^{c}\frac{(c\,\rho)^n}{n!}\right]^{-1}"),
            ("Probabilidad de rechazo (p_k)", r"p_k = \frac{c^c\,\rho^k}{c!\,(k-c)!}\,p_0"),
            ("Tasa efectiva de llegada (λ_eff)", r"\lambda_{\text{ef}} = \lambda\,(1 - p_k)"),
            ("Número medio en sistema (L)", r"L = \sum_{n=0}^k n\,p_n"),
            ("Tiempo medio en sistema (W)", r"W = \frac{L}{\lambda_{\text{ef}}}"),
            ("Número medio en cola (L_q)", r"L_q = \sum_{n=c}^k (n-c)\,p_n"),
            ("Tiempo de espera en cola (W_q)", r"W_q = W - \frac{1}{\mu}"),
        ]
        for title, latex in mmck:
            with st.expander(title):
                st.latex(latex)

    elif system == "Erlang B":
        eb = [
            ("Carga total (r)", r"r = \frac{\lambda}{\mu}"),
            ("Probabilidad de n clientes (p_n)", r"p_n = \frac{r^n}{n!}\,p_0 \quad (0 \le n \le c)"),
            ("Probabilidad sistema vacío (p₀)", r"p_0 = \left[\sum_{n=0}^c \frac{r^n}{n!}\right]^{-1}"),
            ("Probabilidad de bloqueo (B(c,ρ))", r"B(c,\rho) = \frac{\rho^c/c!}{\sum_{n=0}^c \rho^n/n!}"),
            ("Tasa efectiva de llegada (λ_eff)", r"\lambda_{\text{ef}} = \lambda\,(1 - B(c,\rho))"),
            ("Número medio en sistema (L)", r"L = \sum_{n=0}^c n\,\frac{\rho^n}{n!}\,p_0"),
            ("Tiempo medio en sistema (W)", r"W = \frac{L}{\lambda_{\text{ef}}}"),
        ]
        for title, latex in eb:
            with st.expander(title):
                st.latex(latex)

elif mode == "Práctica":
    st.header("✍️ Modo Práctica")
    if not systems:
        st.warning("No se detectaron sistemas en el PDF.")
        st.stop()

    # 1) Selección horizontal de sistema
    st.write("**Elige tu sistema para practicar:**")
    cols = st.columns(len(systems))
    if "practice_system" not in st.session_state:
        for col, sys in zip(cols, systems.keys()):
            if col.button(sys):
                st.session_state.practice_system = sys
                st.session_state.idx = random.randrange(len(systems[sys]))
                st.session_state.idx_changed = True
        st.stop()

    practice_system = st.session_state.practice_system
    st.markdown(f"**Sistema seleccionado:** {practice_system}")

    # 2) Nivel de dificultad
    levels = {"Fácil":1, "Medio":2, "Difícil":4}
    diff = st.select_slider("Nivel de dificultad:", options=list(levels.keys()), value="Medio")
    max_huecos = levels[diff]

    # 3) Seleccionar fórmula y preparar huecos
    formulas = systems[practice_system]
    idx = st.session_state.idx % len(formulas)
    latex = formulas[idx]
    tokens = re.findall(r"\w+|\S", latex)

    if st.session_state.idx_changed:
        # inicializar huecos e intentos
        n = min(max_huecos, len(tokens))
        st.session_state.blanks = random.sample(range(len(tokens)), n)
        st.session_state.attempts = {b:3 for b in st.session_state.blanks}
        st.session_state.idx_changed = False
        # limpiar respuestas previas
        for b in st.session_state.blanks:
            st.session_state.pop(f"ans_{b}", None)

    blanks = st.session_state.blanks

    # 4) Mostrar fórmula enmascarada con ___
    masked = " ".join(" ___ " if i in blanks else tok for i,tok in enumerate(tokens))
    st.subheader("Completa la fórmula:")
    st.latex(masked)

    # 5) Inputs para cada hueco con coloreado
    for j, b in enumerate(blanks, start=1):
        key = f"ans_{b}"
        val = st.session_state.get(key, "")
        attempts = st.session_state.attempts[b]
        correct = (val == tokens[b])
        # verde si correcto, rojo si fallado alguna vez
        bg = "#d4f8d4" if correct else ("#f8d4d4" if attempts < 3 else "white")
        st.text_input(f"Hueco {j}:", value=val, key=key, help=f"Intentos: {attempts}", 
                      label_visibility="collapsed", placeholder="...", 
                      args={"style": f"background-color: {bg}"})

    # 6) Teclado Especial
    special = ['α','β','γ','δ','ε','λ','μ','ρ','θ','Σ','∑','∫','∂','∇','+','-','*','/','^','=']
    st.write("**Teclado Especial**")
    for row in [special[:10], special[10:]]:
        cols_sp = st.columns(len(row))
        for col, ch in zip(cols_sp, row):
            if col.button(ch):
                # añade carácter al último hueco editado
                last = blanks[-1]
                st.session_state[f"ans_{last}"] = st.session_state.get(f"ans_{last}", "") + ch
                st.experimental_rerun()

    # 7) Botones de control
    c1, c2 = st.columns(2)
    if c1.button("Comprobar respuestas"):
        correct = 0
        for b in blanks:
            ans = st.session_state.get(f"ans_{b}", "")
            if ans == tokens[b]:
                correct += 1
            else:
                st.session_state.attempts[b] -= 1
        st.write(f"Aciertos: {correct}/{len(blanks)}")
    if c2.button("Siguiente fórmula"):
        st.session_state.idx = random.randrange(len(formulas))
        st.session_state.idx_changed = True
        st.stop()

else:
    st.error("Modo no reconocido.")

