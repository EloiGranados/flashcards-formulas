import streamlit as st
import pdfplumber, re, random, wikipedia

# Página ancha y título
st.set_page_config(page_title="Flashcards Dinámicas", layout="wide")
st.title("📄 Flashcards de Fórmulas Dinámicas")

# —————————————————————— Paso 0: carga del PDF ——————————————————————
uploader = st.file_uploader("1) Sube tu PDF de fórmulas", type=["pdf"])
if not uploader:
    st.info("Por favor, primero sube un PDF con tus fórmulas.")
    st.stop()

# Extraer texto
text = ""
with pdfplumber.open(uploader) as pdf:
    for page in pdf.pages:
        text += (page.extract_text() or "") + "\n"

# —————————————————————— Paso 1: detección preliminar y revisión ——————————————————————
st.header("🔍 Paso 1: Revisión manual de sistemas y fórmulas")

# Detectar encabezados «Sistema X» o líneas sin operadores
extended_ops = ['=', '+', '-', '*', '/', '^', '√', '∑', 'Σ', '∫', '∂', 'lim', 'd/d', 'dx', 'dy', '∇']
lines = [l.strip() for l in text.split("\n") if l.strip()]

systems = {}
current = None
pattern_system = re.compile(r'^(?:Sistema\s+)?([A-Za-z0-9/ ]+)$', re.IGNORECASE)

for ln in lines:
    m = pattern_system.match(ln)
    if m and not any(op in ln for op in extended_ops):
        current = m.group(1).strip()
        systems[current] = {"definition": "", "raw": []}
        continue
    if current:
        if any(op in ln for op in extended_ops):
            systems[current]["raw"].append(ln)
        else:
            systems[current]["definition"] += ln + " "

# Para cada sistema, que el usuario elija qué líneas son fórmulas y corrija su LaTeX:
for sys_name, info in systems.items():
    with st.expander(f"Sistema: {sys_name}", expanded=False):
        # Editar definición
        new_def = st.text_area(f"Definición para {sys_name}:", value=info["definition"], key=f"def_{sys_name}")
        systems[sys_name]["definition"] = new_def
        
        # Seleccionar líneas que realmente son fórmulas
        chosen = st.multiselect(
            "Marca las líneas que son fórmulas:", 
            options=info["raw"], 
            default=info["raw"], 
            key=f"sel_{sys_name}"
        )
        
        # Para cada línea marcada, permite editarla como LaTeX
        clean_list = []
        for i, raw in enumerate(chosen):
            edited = st.text_input(
                f"🎯 Fórmula {i+1} en LaTeX (edítala si es necesario):", 
                value=raw, 
                key=f"lat_{sys_name}_{i}"
            )
            clean_list.append(edited)
        systems[sys_name]["formulas"] = clean_list

# —————————————————————— Paso 2: Estudio / Práctica ——————————————————————
mode = st.radio("2) Selecciona modo:", ["Estudio","Práctica"], horizontal=True)
sys = st.selectbox("3) Elige un sistema:", list(systems.keys()))
info = systems[sys]

# Función que busca en Wikipedia
@st.cache(show_spinner=False)
def fetch_description(query):
    try:
        return wikipedia.summary(query+" formula", sentences=2)
    except:
        return "Descripción no encontrada en Wikipedia."

if mode == "Estudio":
    st.header(f"📚 Modo Estudio: {sys}")
    st.write(info["definition"])
    # Explicación general
    with st.spinner("🔎 Buscando descripción en Wikipedia..."):
        st.info(fetch_description(sys))
    # Mostrar fórmulas limpias
    for idx, latex in enumerate(info["formulas"], 1):
        with st.expander(f"Fórmula {idx}", expanded=False):
            st.latex(latex)
            # Explicación específica
            key = latex.split("=")[0].strip()
            st.write(fetch_description(key))
else:
    st.header(f"✍️ Modo Práctica: {sys}")
    # Elegir fórmula aleatoria
    if "idx" not in st.session_state or st.button("🔄 Nueva fórmula"):
        st.session_state.idx = random.randrange(len(info["formulas"]))
        st.session_state.resp = ""
        st.session_state.error_count = st.session_state.get("error_count", 0)
    idx = st.session_state.idx
    latex = info["formulas"][idx]
    st.subheader(f"Fórmula {idx+1}")
    st.latex(latex)

    # Generar huecos
    tokens = re.findall(r"\w+|\S", latex)
    blanks = random.sample(range(len(tokens)), min(2, len(tokens)))
    answers = [tokens[i] for i in blanks]
    for i in blanks:
        tokens[i] = "___"
    st.markdown("**Rellena los huecos:**")
    st.code(" ".join(tokens))

    # Respuesta y teclado de griegas
    resp = st.text_area("Tu respuesta:", value=st.session_state.resp, height=80)
    greeks = ['α','β','γ','δ','ε','λ','μ','ρ','θ','Σ','∑','∫','∂','∇']
    cols = st.columns(len(greeks))
    for i, g in enumerate(greeks):
        if cols[i].button(g):
            st.session_state.resp += g
            st.experimental_rerun()

    # Comprobar
    if st.button("Comprobar"):
        user = [u.strip() for u in st.session_state.resp.split(",")]
        correct = sum(u==a for u,a in zip(user, answers))
        mistakes = len(answers)-correct
        st.session_state.error_count += mistakes
        st.write(f"**Aciertos:** {correct}/{len(answers)} — **Errores ronda:** {mistakes} — **Totales:** {st.session_state.error_count}")
        st.write("Respuestas correctas:", ", ".join(answers))
