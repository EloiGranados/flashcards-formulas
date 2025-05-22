import streamlit as st
import random, re

# — Sustituye estas fórmulas de ejemplo por tus propias fórmulas extraídas del PDF —
sistemas = {
    "M/M/1": [
        r"p = 1 - \rho", 
        r"L = \lambda W", 
        r"W = \frac{1}{\mu - \lambda}"
    ],
    "M/M/c": [
        r"p_0 = \left(\sum_{k=0}^{c-1} \frac{(c\rho)^k}{k!} + \frac{(c\rho)^c}{c!\,(1-\rho)}\right)^{-1}"
    ]
}

greeks = ["α","β","γ","δ","ε","λ","μ","ρ","θ","Σ","∑","∫","∂","∇"]

st.title("Flashcards de Fórmulas")

# Modo de uso: Estudio o Práctica
mode = st.radio("Selecciona modo:", ("Estudio", "Práctica"))

# Selección de sistema
system = st.selectbox("Elige un sistema", list(sistemas.keys()))
lista = sistemas[system]

if mode == "Estudio":
    st.header(f"📚 Modo Estudio: {system}")
    for i, f in enumerate(lista, 1):
        st.subheader(f"Fórmula {i}")
        st.latex(f)

else:
    st.header(f"✍️ Modo Práctica: {system}")
    # Elegir o refrescar fórmula
    if "idx" not in st.session_state or st.button("🔄 Nueva fórmula"):
        st.session_state.idx = random.randrange(len(lista))
        st.session_state.resp = ""
        st.session_state.error_count = st.session_state.get("error_count", 0)
    idx = st.session_state.idx
    formula = lista[idx]

    # Mostrar título y fórmula completa
    st.subheader(f"Fórmula {idx+1}")
    st.latex(formula)

    # Función cloze (espacios en blanco)
    def cloze(f, n=2):
        tokens = re.findall(r"\\w+|\\S", f)
        idxs = random.sample(range(len(tokens)), min(n, len(tokens)))
        masked = tokens.copy()
        answers = []
        for i in sorted(idxs):
            answers.append(tokens[i])
            masked[i] = "___"
        return " ".join(masked), answers

    masked, answers = cloze(formula, n=2)
    st.markdown("**Rellena los huecos:**")
    st.code(masked)

    # Área de respuesta y teclado griego
    resp = st.text_area("Tu respuesta:", value=st.session_state.resp, height=80)
    cols = st.columns(len(greeks))
    for i, g in enumerate(greeks):
        if cols[i].button(g):
            st.session_state.resp += g
            st.experimental_rerun()

    # Comprobar respuesta
    if st.button("Comprobar"):
        user = [x.strip() for x in st.session_state.resp.split(",")]
        correct = sum(u == a for u, a in zip(user, answers))
        mistakes = len(answers) - correct
        st.session_state.error_count += mistakes
        st.write(f"**Aciertos:** {correct}/{len(answers)} | **Errores ronda:** {mistakes} | **Totales:** {st.session_state.error_count}")
        st.write("Respuestas correctas:", ", ".join(answers))
