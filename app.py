# -*- coding: utf-8 -*-
import streamlit as st
import pdfplumber, re

# Configuración de la página
st.set_page_config(page_title="Flashcards Dinámicas", layout="wide")
st.title("📄 Flashcards de Fórmulas Dinámicas")

# Paso 0: Subida de PDF
uploader = st.file_uploader("1) Sube tu PDF de fórmulas", type=["pdf"])
if not uploader:
    st.info("Por favor, sube un PDF con fórmulas para comenzar.")
    st.stop()

# Leer y segmentar texto
txt = ''
with pdfplumber.open(uploader) as pdf:
    for page in pdf.pages:
        txt += (page.extract_text() or '') + '\n'
lines = [l.rstrip() for l in txt.split('\n')]

# Paso 1: Detectar sistemas principales y agrupar fórmulas
desired = ["M/M/1", "Erlang C", "M/M/c/k", "Erlang B"]
pos = []
for i, line in enumerate(lines):
    for name in desired:
        if re.search(rf"(?:Sistema\s+)?{re.escape(name)}", line, re.IGNORECASE):
            if name not in [s for s,_ in pos]: pos.append((name, i))
pos = sorted(pos, key=lambda x: x[1])
systems = {}
for idx, (name, start) in enumerate(pos):
    end = pos[idx+1][1] if idx+1 < len(pos) else len(lines)
    block = lines[start+1:end]
    ops = ['=', '+', '-', '*', '/', '^', '√', '∑', '∫', '∂', 'lim']
    formulas = [ln.strip() for ln in block if any(op in ln for op in ops) and ln.strip()]
    systems[name] = formulas

# Paso 2: Modo Estudio
st.header("📚 Modo Estudio: Explora tus sistemas")
if not systems:
    st.warning("No se detectaron sistemas en el PDF.")
else:
    system = st.selectbox("Elige un sistema:", list(systems.keys()))
    st.write(f"**Sistema seleccionado:** {system}")

    # M/M/1 fijo
    if system == "M/M/1":
        mm1 = [
            ("Utilización (ρ)", r"\rho = \frac{\lambda}{\mu}"),
            ("Probabilidad sistema vacío (p₀)", r"p_0 = 1 - \rho"),
            ("Probabilidad de k clientes (p_k)", r"p_k = (1 - \rho)\rho^k"),
            ("Número medio en sistema (L)", r"L = \frac{\rho}{1 - \rho}"),
            ("Número medio en cola (L_q)", r"L_q = \frac{\rho^2}{1 - \rho}"),
            ("Tiempo medio en sistema (W)", r"W = \frac{1}{\mu - \lambda}"),
            ("Tiempo medio en cola (W_q)", r"W_q = \frac{\lambda}{\mu(\mu - \lambda)}")
        ]
        for title, latex in mm1:
            with st.expander(f"🔹 {title}", expanded=False):
                st.latex(latex)

    # Erlang C fijo
    elif system == "Erlang C":
        ec = [
            ("Utilización total (r)", r"r = \frac{\lambda}{\mu}"),
            ("Utilización por servidor (ρ)", r"\rho = \frac{r}{c}"),
            ("Probabilidad de n clientes (p_n)",
             r"p_n = \begin{cases}"
                        r"\frac{(c\rho)^n}{n!}\,p_0 & n < c \\"
                        r"\frac{\rho^n\,c^c}{c!}\,p_0 & n \ge c\end{cases}"),
            ("Probabilidad sistema vacío (p₀)",
             r"p_0 = \left(\frac{(c\rho)^c}{c!\,(1-\rho)} + \sum_{n=0}^{c-1}\frac{(c\rho)^n}{n!}\right)^{-1}"),
            ("Probabilidad de espera (P_{wait})", r"P_{wait} = \frac{(c\rho)^c}{c!\,(1-\rho)}\,p_0"),
            ("Tiempo medio en cola (W_q)",
             r"W_q = \frac{r^c}{c!\,(c\mu)(1-\rho)^2}\,p_0"),
            ("Tiempo medio en el sistema (W)",
             r"W = \frac{1}{\mu} + W_q"),
            ("Número medio en el sistema (L)",
             r"L = \lambda W = r + \frac{\rho\,r^c}{c!\,(1-\rho)^2}\,p_0")
        ]
        for title, latex in ec:
            with st.expander(f"🔹 {title}", expanded=False):
                st.latex(latex)

    # Genérico para otros sistemas
    else:
        formulas = systems.get(system, [])
        if not formulas:
            st.warning(f"No se encontraron fórmulas para {system}.")
        else:
            for i, f in enumerate(formulas, 1):
                with st.expander(f"🔹 Fórmula {i}", expanded=False):
                    try:
                        st.latex(f)
                    except:
                        st.code(f)
