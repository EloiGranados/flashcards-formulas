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

# Paso 2: Modo Estudio
st.header("📚 Modo Estudio: Explora tus sistemas detectados")
if not systems:
    st.warning("No se detectaron sistemas en el PDF.")
else:
    system = st.selectbox("Elige un sistema:", list(systems.keys()))
    st.markdown(f"**Sistema seleccionado:** {system}")
    
    # Despliegue específico para cada sistema
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

    elif system == "Erlang C":
        ec = [
            ("Carga total (r)", r"r = \frac{\lambda}{\mu}"),
            ("Utilización por servidor (ρ)", r"\rho = \frac{r}{c}"),
            ("Probabilidad n clientes (p_n)",
             r"p_n = \begin{cases}\frac{r^n}{n!}p_0,&n<c\\\frac{r^n}{c!\,(n-c)!}p_0,&n\ge c\end{cases}"),
            ("Probabilidad sistema vacío (p₀)",
             r"p_0 = \left[\sum_{n=0}^{c-1}\frac{r^n}{n!}+\sum_{n=c}^k\frac{r^n}{c!\,(n-c)!}\right]^{-1}"),
            ("Probabilidad de rechazo (p_K)", r"P_{rechazo} = p_K"),
            ("Tasa efectiva de llegada (λ_eff) ", r"\lambda_{ef} = \lambda(1 - p_K)"),
            ("Número medio en sistema (L)", r"L = \sum_{n=0}^K n\,p_n"),
            ("Tiempo medio en sistema (W)", r"W = \frac{L}{\lambda_{ef}}"),
            ("Número medio en cola (L_q)", r"L_q = \sum_{n=c}^K (n-c)\,p_n"),
            ("Tiempo de espera en cola (W_q)", r"W_q = W - \frac{1}{\mu}")
        ]
        for title, latex in ec:
            with st.expander(title, expanded=False):
                st.latex(latex)

    elif system == "M/M/c/k":
        mmck = [
            ("Carga total (r)", r"r = \frac{\lambda}{\mu}"),
            ("Probabilidad n clientes (p_n)", r"p_n = \begin{cases}\frac{(c\rho)^n}{n!}p_0,&n\le c\\\frac{c^c\rho^n}{c!\,(n-c)!}p_0,&c<n\end{cases}"),
            ("p₀ normalización", r"p_0 = \left[\sum_{n=0}^{c}\frac{(c\rho)^n}{n!}\right]^{-1}"),
            ("Probabilidad de rechazo (p_k)", r"p_k = \frac{c^c\rho^k}{c!\,(k-c)!}p_0"),
            ("Tasa efectiva (λ_eff)", r"\lambda_{ef} = \lambda(1 - p_k)"),
            ("Número medio en sistema (L)", r"L = \sum_{n=0}^k n\,p_n"),
            ("Tiempo medio en sistema (W)", r"W = \frac{L}{\lambda_{ef}}"),
            ("Número medio en cola (L_q)", r"L_q = \sum_{n=c}^k (n-c)\,p_n"),
            ("Tiempo de espera en cola (W_q)", r"W_q = W - \frac{1}{\mu}")
        ]
        for title, latex in mmck:
            with st.expander(title, expanded=False):
                st.latex(latex)

    elif system == "Erlang B":
        eb = [
            ("Probabilidad de bloqueo (B(c,ρ))", r"B(c,\rho) = \frac{\rho^c/c!}{\sum_{n=0}^c\rho^n/n!}"),
            ("Tasa efectiva de llegada (λ_eff)", r"\lambda_{ef} = \lambda(1 - B(c,\rho))"),
            ("Número medio en sistema (L)", r"L = \sum_{n=0}^c n\frac{\rho^n}{n!}p_0"),
            ("Tiempo medio en sistema (W)", r"W = \frac{L}{\lambda_{ef}}")
        ]
        for title, latex in eb:
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
# Fin modo Estudio
