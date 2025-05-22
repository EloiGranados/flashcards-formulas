import streamlit as st
import pdfplumber, re, random, wikipedia

# Configuración
st.set_page_config(page_title="Flashcards Dinámicas", layout="wide")
st.title("📄 Flashcards de Fórmulas Dinámicas")

# Carga del PDF
uploader = st.file_uploader("Sube tu PDF de fórmulas", type=["pdf"])
if not uploader:
    st.info("Primero, sube un PDF con tus fórmulas para comenzar.")
    st.stop()

# Extraer texto completo
text = ''
with pdfplumber.open(uploader) as pdf:
    for page in pdf.pages:
        text += (page.extract_text() or '') + '\n'

# Procesar líneas y detectar sistemas
extended_ops = ['=', '+', '-', '*', '/', '^', '√', '∑', 'Σ', '∫', '∂', 'lim', 'd/d', 'dx', 'dy', '∇']
lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
systems = {}
current = None
# Detectar encabezados como "M/M/1", "Erlang B", etc.
pattern_system = re.compile(r'^(?:Sistema\s+)?([A-Za-z0-9/ ]+)$', re.IGNORECASE)
for ln in lines:
    m = pattern_system.match(ln)
    if m and not any(op in ln for op in extended_ops):
        current = m.group(1).strip()
        systems[current] = {"definition": '', "formulas": []}
        continue
    if current:
        # Acumular definiciones (líneas sin operadores)
        if not any(op in ln for op in extended_ops):
            systems[current]["definition"] += ln + ' '
        else:
            # Línea con operadores = fórmula
            systems[current]["formulas"].append(ln)

# UI: elección de modo y sistema
mode = st.radio("Selecciona modo:", ["Estudio", "Práctica"], horizontal=True)
sys = st.selectbox("Elige un sistema:", list(systems.keys()))
info = systems[sys]

# Función para buscar descripción en Wikipedia
@st.cache(show_spinner=False)
def fetch_description(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except:
        return "Descripción no disponible en Wikipedia."

if mode == 'Estudio':
    st.header(f"📚 Modo Estudio: {sys}")
    # Mostrar definición general (del PDF + Wiki)
    st.write(info['definition'])
    with st.spinner('Buscando descripción en Wikipedia...'):
        desc = fetch_description(sys + ' formula')
    st.info(desc)
    # Mostrar cada fórmula con explicación extraída
    for idx, f in enumerate(info['formulas'], 1):
        with st.expander(f"Fórmula {idx}"):
            st.latex(f)
            # Obtener título antes del '=' si existe
            key = f.split('=')[0].strip()
            desc_f = fetch_description(key + ' formula')
            st.write(desc_f)

else:
    st.header(f"✍️ Modo Práctica: {sys}")
    # Elegir fórmula aleatoria
    if 'idx' not in st.session_state or st.button('🔄 Nueva fórmula'):
        st.session_state.idx = random.randrange(len(info['formulas']))
        st.session_state.resp = ''
        st.session_state.error_count = st.session_state.get('error_count', 0)
    idx = st.session_state.idx
    formula = info['formulas'][idx]
    st.subheader(f"Fórmula {idx+1}")
    st.latex(formula)
    # Cloze
    tokens = re.findall(r"\w+|\S", formula)
    blanks = random.sample(range(len(tokens)), min(2, len(tokens)))
    answers = [tokens[i] for i in blanks]
    for i in blanks:
        tokens[i] = '___'
    masked = ' '.join(tokens)
    st.markdown("**Rellena los huecos:**")
    st.code(masked)
    # Respuesta + teclado griego
    resp = st.text_area('Tu respuesta:', st.session_state.resp, height=80)
    greeks = ['α','β','γ','δ','ε','λ','μ','ρ','θ','Σ','∑','∫','∂','∇']
    cols = st.columns(len(greeks))
    for i, g in enumerate(greeks):
        if cols[i].button(g):
            st.session_state.resp += g
            st.experimental_rerun()
    # Comprobar
    if st.button('Comprobar'):
        user = [u.strip() for u in st.session_state.resp.split(',')]
        correct = sum(u == a for u, a in zip(user, answers))
        mistakes = len(answers) - correct
        st.session_state.error_count += mistakes
        st.write(f"**Aciertos:** {correct}/{len(answers)} — **Errores ronda:** {mistakes} — **Totales:** {st.session_state.error_count}")
        st.write('Respuestas correctas:', ', '.join(answers))
