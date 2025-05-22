# -*- coding: utf-8 -*-
import streamlit as st
import pdfplumber, re, random, wikipedia

# Configuración de la página
st.set_page_config(page_title="Flashcards Dinámicas", layout="wide")
st.title("📄 Flashcards de Fórmulas Dinámicas")

# Paso 0: Subida de PDF
uploader = st.file_uploader("1) Sube tu PDF de fórmulas", type=["pdf"])
if not uploader:
    st.info("Por favor, sube un PDF con fórmulas para comenzar.")
    st.stop()

# Extraer texto completo
txt = ''
with pdfplumber.open(uploader) as pdf:
    for page in pdf.pages:
        txt += (page.extract_text() or '') + '\n'

# Paso 1: Detección preliminar y revisión manual
st.header("🔍 Paso 1: Revisión y edición de fórmulas")
extended_ops = ['=', '+', '-', '*', '/', '^', '√', '∑', 'Σ', '∫', '∂', 'lim', 'd/d', 'dx', 'dy', '∇']
lines = [l.strip() for l in txt.split('\n') if l.strip()]
systems = {}
current = None
pattern_system = re.compile(r'^(?:Sistema\s+)?([A-Za-z0-9/ ]+)$', re.IGNORECASE)

for ln in lines:
    m = pattern_system.match(ln)
    if m and not any(op in ln for op in extended_ops):
        current = m.group(1).strip()
        systems[current] = {"definition": "", "raw": [], "formulas": []}
        continue
    if current:
        if any(op in ln for op in extended_ops):
            systems[current]["raw"].append(ln)
        else:
            systems[current]["definition"] += ln + ' '

# Mostrar cada sistema para revisión
default_title = lambda idx: f"Fórmula {idx+1}"
for sys_name, info in systems.items():
    with st.expander(f"Sistema: {sys_name}", expanded=False):
        # Editar definición formal
        info['definition'] = st.text_area(
            f"Definición formal de {sys_name}:",
            value=info['definition'], key=f"def_{sys_name}")
        # Seleccionar cuáles raw son fórmulas
        chosen = st.multiselect(
            f"Selecciona líneas de fórmulas en {sys_name}:",
            options=info['raw'],
            default=info['raw'],
            key=f"sel_{sys_name}")
        # Para cada línea, editar título, LaTeX y explicación
        info['formulas'] = []
        for idx, raw in enumerate(chosen):
            st.markdown(f"---\n**Fórmula {idx+1}:** línea original: `{raw}`")
            title = st.text_input(
                f"Título de la fórmula {idx+1}:",
                value=default_title(idx), key=f"title_{sys_name}_{idx}")
            latex = st.text_input(
                f"Expresión en LaTeX {idx+1}:",
                value=raw, key=f"latex_{sys_name}_{idx}")
            description = st.text_area(
                f"Descripción formal de la fórmula {idx+1}:",
                value="", key=f"desc_{sys_name}_{idx}", height=100)
            info['formulas'].append({
                'title': title,
                'latex': latex,
                'description': description
            })

# Paso 2: Estudio / Práctica
tab = st.radio("2) Selecciona modo:", ["Estudio", "Práctica"], horizontal=True)
sys = st.selectbox("3) Elige un sistema:", list(systems.keys()))
info = systems[sys]

# Función para resumen en Wikipedia
@st.cache(show_spinner=False)
def fetch_wiki_summary(query):
    try:
        return wikipedia.summary(query + ' formula', sentences=2)
    except:
        return "No se encontró descripción en Wikipedia."

if tab == "Estudio":
    st.header(f"📚 Modo Estudio: {sys}")
    # Mostrar definición general
    st.subheader("Definición del sistema")
    st.write(info['definition'])
    wiki_sys = fetch_wiki_summary(sys)
    st.info(wiki_sys)
    # Mostrar cada fórmula con título y recuadro
    for f in info['formulas']:
        with st.expander(f"🔹 {f['title']}", expanded=False):
            st.markdown("**Descripción formal:**")
            st.write(f['description'] or "Sin descripción.")
            st.markdown("**Fórmula (LaTeX):**")
            st.latex(f['latex'])
elif tab == "Práctica":
    st.header(f"✍️ Modo Práctica: {sys}")
    # Seleccionar fórmula aleatoria o por título
    titles = [f['title'] for f in info['formulas']]
    choice = st.selectbox("Selecciona la fórmula para practicar:", titles)
    selected = next(f for f in info['formulas'] if f['title'] == choice)
    st.subheader(choice)
    st.latex(selected['latex'])
    # Generar huecos automáticos
    tokens = re.findall(r"\w+|\S", selected['latex'])
    blanks = random.sample(range(len(tokens)), min(2, len(tokens)))
    answers = [tokens[i] for i in blanks]
    for i in blanks:
        tokens[i] = "___"
    st.markdown("**Rellena los huecos:**")
    st.code(" ".join(tokens))
    # Área de respuesta y teclado griego
    resp = st.text_area("Tu respuesta:", height=80)
    greeks = ['α','β','γ','δ','ε','λ','μ','ρ','θ','Σ','∑','∫','∂','∇']
    cols = st.columns(len(greeks))
    for i, g in enumerate(greeks):
        if cols[i].button(g):
            resp += g
            st.experimental_rerun()
    # Comprobar respuesta
    if st.button("Comprobar respuesta"):
        user = [u.strip() for u in resp.split(",")]
        correct = sum(u == a for u, a in zip(user, answers))
        mistakes = len(answers) - correct
        st.write(f"Aciertos: {correct}/{len(answers)} — Errores: {mistakes}")
        st.write("Respuestas correctas:", ", ".join(answers))
