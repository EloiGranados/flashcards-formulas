import streamlit as st
import random, re

# — Datos de ejemplo — sustituye por tu extracción real de fórmulas
sistemas = {
    "M/M/1": ["p = 1 − ρ", "L = λW", "W = 1/(μ−λ)"],
    "M/M/c": ["p0 = (∑_{k=0}^{c−1} (cρ)^k/k!  +  (cρ)^c/(c!*(1−ρ)))**-1"]
}

greeks = ["α","β","γ","δ","ε","λ","μ","ρ","θ","Σ","∑","∫","∂","∇"]

st.title("Flashcards de Fórmulas")

sistema = st.selectbox("Sistema", list(sistemas.keys()))
lista = sistemas[sistema]

if "f" not in st.session_state or st.button("🔄 Nueva fórmula"):
    st.session_state.f = random.choice(lista)
formula = st.session_state.f

def cloze(f, n=2):
    tokens = re.findall(r"\w+|\\S", f)
    for i in random.sample(range(len(tokens)), min(n, len(tokens))):
        tokens[i] = "___"
    return "".join(tokens)

masked = cloze(formula, n=2)
st.markdown("### Rellena los huecos:")
st.code(masked)

if "resp" not in st.session_state:
    st.session_state.resp = ""
resp = st.text_area("Tu respuesta:", st.session_state.resp, height=80)

cols = st.columns(len(greeks))
for i, g in enumerate(greeks):
    if cols[i].button(g):
        st.session_state.resp += g
        st.experimental_rerun()

if st.button("Comprobar"):
    answers = [t for t in re.findall(r"\w+|\\S", formula)
               if t not in re.findall(r"\w+|\\S", masked)]
    user = [x.strip() for x in st.session_state.resp.split(",")]
    aciertos = sum(u==a for u,a in zip(user, answers))
    errores = len(answers) - aciertos
    st.write(f"**Aciertos:** {aciertos}/{len(answers)} — **Errores:** {errores}")
    st.write("Respuestas:", ", ".join(answers))
