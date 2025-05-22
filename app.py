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

# Paso 1: Detectar sistemas deseados y agrupar fórmulas
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
        # Despliegue detallado según sistema
        if system == "M/M/1":
            mm1 = [
                ("Utilización (ρ)", r"\rho = \frac{\lambda}{\mu}"),
                ("Probabilidad sistema vacío (p₀)", r"p_0 = 1 - \rho"),
                ("Probabilidad k clientes (p_k)", r"p_k = (1 - \rho)\, \rho^k"),
                ("Clientes en sistema (L)", r"L = \frac{\rho}{1 - \rho}"),
                ("Clientes en cola (L_q)", r"L_q = \frac{\rho^2}{1 - \rho}"),
                ("Tiempo en sistema (W)", r"W = \frac{1}{\mu - \lambda}"),
                ("Tiempo en cola (W_q)", r"W_q = \frac{\lambda}{\mu (\mu - \lambda)}"),
            ]
            for title, latex in mm1:
                with st.expander(title):
                    st.latex(latex)
        elif system == "Erlang C":
            ec = [
                ("Carga total (r)", r"r = \frac{\lambda}{\mu}"),
                ("Utilización por servidor (ρ)", r"\rho = \frac{r}{c}"),
                ("Probabilidad n clientes (p_n)",
                 r"p_n = \begin{cases}\\frac{r^n}{n!} p_0 & n<c \\ \\frac{r^n}{c! (n-c)!} p_0 & n\\ge c \end{cases}"),
                ("Probabilidad sistema vacío (p₀)",
                 r"p_0 = \left[\sum_{n=0}^{c-1} \frac{r^n}{n!} + \sum_{n=c}^K \frac{r^n}{c! (n-c)!} \right]^{-1}"),
                ("Probabilidad de rechazo (p_K)", r"P_{rechazo} = p_K"),
                ("Tasa efectiva de llegada (λ_eff)", r"\lambda_{ef} = \lambda (1 - p_K)"),
                ("Número medio en sistema (L)", r"L = \sum_{n=0}^K n p_n"),
                ("Tiempo medio en sistema (W)", r"W = \frac{L}{\lambda_{ef}}"),
                ("Número medio en cola (L_q)", r"L_q = \sum_{n=c}^K (n-c) p_n"),
                ("Tiempo de espera en cola (W_q)", r"W_q = W - \frac{1}{\mu}"),
            ]
            for title, latex in ec:
                with st.expander(title):
                    st.latex(latex)
        elif system == "M/M/c/k":
            mmck = [
                ("Carga total (r)", r"r = \frac{\lambda}{\mu}"),
                ("Probabilidad n clientes (p_n)",
                 r"p_n = \begin{cases}\\frac{(c\rho)^n}{n!} p_0 & n\le c \\ \\frac{c^c \rho^n}{c! (n-c)!} p_0 & c<n\end{cases}"),
                ("Probabilidad sistema vacío (p₀)",
                 r"p_0 = \left[\sum_{n=0}^c \frac{(c\rho)^n}{n!}\right]^{-1}"),
                ("Probabilidad de rechazo (p_k)", r"p_k = \frac{c^c \rho^k}{c! (k-c)!} p_0"),
                ("Tasa efectiva de llegada (λ_eff)", r"\lambda_{ef} = \lambda (1 - p_k)"),
                ("Número medio en sistema (L)", r"L = \sum_{n=0}^k n p_n"),
                ("Tiempo medio en sistema (W)", r"W = \frac{L}{\lambda_{ef}}"),
                ("Número medio en cola (L_q)", r"L_q = \sum_{n=c}^k (n-c) p_n"),
                ("Tiempo de espera en cola (W_q)", r"W_q = W - \frac{1}{\mu}"),
            ]
            for title, latex in mmck:
                with st.expander(title):
                    st.latex(latex)
        elif system == "Erlang B":
            eb = [
                ("Carga total (r)", r"r = \frac{\lambda}{\mu}"),
                ("Probabilidad n clientes (p_n)", r"p_n = \frac{r^n}{n!} p_0 \quad (0 \le n \le c)"),
                ("Probabilidad sistema vacío (p₀)", r"p_0 = \left[\sum_{n=0}^c \frac{r^n}{n!}\right]^{-1}"),
                ("Probabilidad de bloqueo (B(c,ρ))", r"B(c,\rho) = \frac{\rho^c/c!}{\sum_{n=0}^c \rho^n/n!}"),
                ("Tasa efectiva de llegada (λ_eff)", r"\lambda_{ef} = \lambda (1 - B(c,\rho))"),
                ("Número medio en sistema (L)", r"L = \sum_{n=0}^c n \frac{\rho^n}{n!} p_0"),
                ("Tiempo medio en sistema (W)", r"W = \frac{L}{\lambda_{ef}}"),
            ]
            for title, latex in eb:
                with st.expander(title):
                    st.latex(latex)

# ------------------ MODO PRÁCTICA ------------------
elif mode == "Práctica":
    st.header("✍️ Modo Práctica")
    if not systems:
        st.warning("No se detectaron sistemas en el PDF.")
    else:
        # Selector horizontal de sistema
        st.write("**Elige tu sistema para practicar:**")
        cols = st.columns(len(systems))
        if 'practice_system' not in st.session_state:
            for col, sys in zip(cols, systems.keys()):
                if col.button(sys):
                    st.session_state.practice_system = sys
                    st.session_state.idx = random.randrange(len(systems[sys]))
                    st.session_state.resp = ""
            st.stop()
        practice_system = st.session_state.practice_system
        st.markdown(f"**Sistema seleccionado:** {practice_system}")
        # Flashcard actual
        formulas = systems[practice_system]
        latex = formulas[st.session_state.idx]
        st.latex(latex)
        # Crear huecos
        tokens = re.findall(r"\w+|\S", latex)
        blanks = random.sample(range(len(tokens)), min(2, len(tokens)))
        answers = [tokens[i] for i in blanks]
        for i in blanks:
            tokens[i] = '___'
        st.markdown("**Rellena los huecos:**")
        st.code(" ".join(tokens))
        # Respuesta y teclado griego
        st.session_state.resp = st.text_area("Tu respuesta:", value=st.session_state.resp, height=80)
        greeks = ['α','β','γ','δ','ε','λ','μ','ρ','θ','Σ','∑','∫','∂','∇']
        cols2 = st.columns(len(greeks))
        for i, g in enumerate(greeks):
            if cols2[i].button(g):
                st.session_state.resp += g
                st.experimental_rerun()
        if st.button("Comprobar respuesta"):
            user = [u.strip() for u in st.session_state.resp.split(",")]
            correct = sum(u == a for u, a in zip(user, answers))
            mistakes = len(answers) - correct
            st.write(f"Aciertos: {correct}/{len(answers)} | Errores ronda: {mistakes}")
        if st.button("Siguiente fórmula"):
            st.session_state.idx = random.randrange(len(formulas))
            st.session_state.resp = ""
            st.experimental_rerun()


