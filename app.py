import streamlit as st
import random, re

# — Diccionario de sistemas con definiciones y fórmulas —
sistemas = {
    "M/M/1": {
        "definition": "Sistema de colas con llegadas Poisson, servicio exponencial y un solo servidor.",
        "formulas": [
            {"title": "Probabilidad de estado 0", "latex": r"p_0 = 1 - \rho"},
            {"title": "Probabilidad de k clientes", "latex": r"p_k = (1-\rho)\rho^k"},
            {"title": "Longitud promedio en el sistema", "latex": r"L = \frac{\rho}{1-\rho}"},
            {"title": "Tiempo promedio en el sistema", "latex": r"W = \frac{1}{\mu - \lambda}"}
        ]
    },
    "M/M/c": {
        "definition": "Sistema M/M/c con c servidores en paralelo.",
        "formulas": [
            {"title": "p_0", "latex": r"p_0 = \left[\sum_{k=0}^{c-1} \frac{(c\rho)^k}{k!} + \frac{(c\rho)^c}{c!\,(1-\rho)}\right]^{-1}"},
            {"title": "p_n (Erlang C)",
             "variants": [
                 {"cond": r"n < c", "latex": r"p_n = \frac{(c\rho)^n}{n!} p_0"},
                 {"cond": r"n \ge c", "latex": r"p_n = \frac{c^c \rho^n}{c!}\,p_0"}
             ]
            }
        ]
    },
    "M/M/c/k": {
        "definition": "Sistema M/M/c con capacidad máxima k en cola + servicio.",
        "formulas": [
            {"title": "p_n (0≤n≤c)", "latex": r"p_n = \frac{(c\rho)^n}{n!} p_0"},
            {"title": "p_n (c≤n≤k)", "latex": r"p_n = \frac{c^c \rho^n}{c!} p_0"}
        ]
    },
    "Erlang B": {
        "definition": "Probabilidad de bloqueo en sistemas de llamadas sin esperas.",
        "formulas": [
            {"title": "Erlang B", "latex": r"B(c,\rho) = \frac{\frac{\rho^c}{c!}}{\sum_{n=0}^c \frac{\rho^n}{n!}}"}
        ]
    },
    "Erlang C": {
        "definition": "Probabilidad de espera en sistemas con cola infinita.",
        "formulas": [
            {"title": "Erlang C", "latex": r"C(c,\rho) = \frac{\frac{\rho^c}{c!}\frac{c}{c-\rho}}{\sum_{n=0}^{c-1}\frac{\rho^n}{n!} + \frac{\rho^c}{c!}\frac{c}{c-\rho}}"}
        ]
    }
}

greeks = ["α","β","γ","δ","ε","λ","μ","ρ","θ","Σ","∑","∫","∂","∇"]

st.title("Flashcards de Fórmulas Avanzadas")

mode = st.radio("Selecciona modo:", ("Estudio", "Práctica"))

# Selector de sistema
sistema = st.selectbox("Elige un sistema:", list(sistemas.keys()))
info = sistemas[sistema]

if mode == "Estudio":
    st.header(f"📚 Modo Estudio: {sistema}")
    st.write(info["definition"])
    for f in info["formulas"]:
        st.subheader(f["title"])
        if "variants" in f:
            for v in f["variants"]:
                st.markdown(f"**Si {v['cond']}:**")
                st.latex(v["latex"])
        else:
            st.latex(f["latex"])

else:
    st.header(f"✍️ Modo Práctica: {sistema}")
    # Elegir fórmula aleatoria
    if "idx" not in st.session_state or st.button("🔄 Nueva fórmula"):
        st.session_state.idx = random.randrange(len(info["formulas"]))
        st.session_state.resp = ""
        st.session_state.error_count = st.session_state.get("error_count", 0)
    idx = st.session_state.idx
    f = info["formulas"][idx]

    # Mostrar título y latex
    st.subheader(f["title"])
    # Si hay variantes, pide condición al usuario
    if "variants" in f:
        conds = [v["cond"] for v in f["variants"]]
        sel = st.selectbox("Condición:", conds)
        latex = next(v["latex"] for v in f["variants"] if v["cond"] == sel)
    else:
        latex = f["latex"]
    st.latex(latex)

    # Cloze deletion
    def cloze_tokens(text, n=2):
        tokens = re.findall(r"\w+|\S", text)
        idxs = random.sample(range(len(tokens)), min(n, len(tokens)))
        answers = [tokens[i] for i in idxs]
        for i in idxs:
            tokens[i] = "___"
        return " ".join(tokens), answers

    masked, answers = cloze_tokens(latex, n=2)
    st.markdown("**Rellena los huecos:**")
    st.code(masked)

    # Respuesta y teclado griego
    resp = st.text_area("Tu respuesta:", value=st.session_state.resp, height=80)
    cols = st.columns(len(greeks))
    for i, g in enumerate(greeks):
        if cols[i].button(g):
            st.session_state.resp += g
            st.experimental_rerun()

    if st.button("Comprobar"):
        user = [x.strip() for x in st.session_state.resp.split(",")]
        correct = sum(u == a for u, a in zip(user, answers))
        mistakes = len(answers) - correct
        st.session_state.error_count += mistakes
        st.write(f"**Aciertos:** {correct}/{len(answers)} | **Errores ronda:** {mistakes} | **Totales:** {st.session_state.error_count}")
        st.write("Respuestas correctas:", ", ".join(answers))
