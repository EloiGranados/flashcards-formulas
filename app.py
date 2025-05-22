import streamlit as st
import pdfplumber, re, random

# Configuración de la página
st.set_page_config(page_title="Flashcards Dinámicas", layout="wide")
st.title("📄 Flashcards de Fórmulas Dinámicas")

# %% Carga del PDF
uploaded_file = st.file_uploader("Sube tu PDF de fórmulas", type=["pdf"])
if not uploaded_file:
    st.info("Por favor, sube un PDF con tus fórmulas para comenzar.")
    st.stop()

# %% Extracción de texto
txt = ""
with pdfplumber.open(uploaded_file) as pdf:
    for page in pdf.pages:
        txt += (page.extract_text() or "") + "\n"

# %% Procesamiento de líneas en sistemas
extended_ops = ['=', '+', '-', '*', '/', '^', '√', '∑', 'Σ', '∫', '∂', 'lim', 'd/d', 'dx', 'dy', '∇']
lines = [l.strip() for l in txt.split("\n") if l.strip()]
systems = {}
current = None
pattern_system = re.compile(r'^(Sistema\s+[^:]+)', re.IGNORECASE)
for line in lines:
    m = pattern_system.match(line)
    if m:
        current = m.group(1)
        systems[current] = {"definition": "", "formulas": []}
        continue
    if current:
        # Detectar fórmulas (líneas con operadores)
        if any(op in line for op in extended_ops):
            systems[current]["formulas"].append({"latex": line})
        else:
            systems[current]["definition"] += line + " "

# %% Interfaz de usuario
mode = st.radio("Selecciona modo:", ["Estudio", "Práctica"], horizontal=True)
system = st.selectbox("Elige un sistema:", list(systems.keys()))
info = systems[system]

if mode == "Estudio":
    st.header(f"📚 Modo Estudio: {system}")
    st.write(info["definition"])
    for i, f in enumerate(info["formulas"], 1):
        with st.expander(f"Fórmula {i}"):
            st.latex(f["latex"])
            st.write("_Pasa el cursor para ver más detalles..._")
else:
    st.header(f"✍️ Modo Práctica: {system}")
    # Seleccionar fórmula aleatoria
    if "idx" not in st.session_state or st.button("🔄 Nueva fórmula"):
        st.session_state.idx = random.randrange(len(info["formulas"]))
        st.session_state.resp = ""
        st.session_state.error_count = st.session_state.get("error_count", 0)
    idx = st.session_state.idx
    formulation = info["formulas"][idx]
    latex = formulation["latex"]

    st.subheader(f"Fórmula {idx+1}")
    st.latex(latex)

    # Generar huecos
    def cloze_latex(expr, n=2):
        tokens = re.findall(r"\\w+|\\S", expr)
        idxs = random.sample(range(len(tokens)), min(n, len(tokens)))
        answers = [tokens[i] for i in idxs]
        for i in idxs:
            tokens[i] = "___"
        return " ".join(tokens), answers

    masked, answers = cloze_latex(latex, n=2)
    st.markdown("**Rellena los huecos:**")
    st.code(masked)

    # Entrada y teclado griego
    resp = st.text_area("Tu respuesta:", value=st.session_state.resp, height=80)
    greeks = ["α","β","γ","δ","ε","λ","μ","ρ","θ","Σ","∑","∫","∂","∇"]
    cols = st.columns(len(greeks))
    for i, g in enumerate(greeks):
        if cols[i].button(g):
            st.session_state.resp += g
            st.experimental_rerun()

    # Comprobar
    if st.button("Comprobar"):
        user = [x.strip() for x in st.session_state.resp.split(",")]
        correct = sum(u == a for u, a in zip(user, answers))
        mistakes = len(answers) - correct
        st.session_state.error_count += mistakes
        st.write(f"**Aciertos:** {correct}/{len(answers)} — **Errores ronda:** {mistakes} — **Totales:** {st.session_state.error_count}")
        st.write("Respuestas correctas:", ", ".join(answers))

