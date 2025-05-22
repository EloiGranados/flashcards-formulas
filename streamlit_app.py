import streamlit as st
from io import BytesIO
from pdfminer.high_level import extract_text
import re
import json
import datetime

from sm2 import SM2Scheduler
from tracker import MetricsTracker

def extraer_ecuaciones(pdf_bytes: BytesIO) -> dict:
    texto = extract_text(pdf_bytes)
    patrones = {
        "M/M/1": r"L\s*=\s*λ\s*/\s*\(μ\s*-\s*λ\)|W\s*=\s*1\s*/\s*(μ\s*-\s*λ)",
        "Erlang C": r"P_0\s*=.*?P_n\s*=.*?",
        "M/M/c/k": r"\rho=\s*λ\s*/\s*(cμ)\s*.*?P_0\s*=",
        "Erlang B": r"B(c,ρ)\s*=.*?",
    }
    resultados = {}
    for sistema, pat in patrones.items():
        matches = re.findall(pat, texto, flags=re.DOTALL)
        resultados[sistema] = list(set(matches))
    return resultados

def convertir_a_latex(expresion: str) -> str:
    latex = expresion.replace("λ", "\\lambda").replace("μ", "\\mu")
    frac_pat = r"([A-Za-z]+)\s*=\s*([^\s]+)/\s*\(([^\)]+)\)"
    def repl(m):
        return f"{m.group(1)} = \\frac{{{m.group(2)}}}{{{m.group(3)}}}"
    return re.sub(frac_pat, repl, latex)

def generar_huecos(formulas: list, nivel: str):
    import random
    dificultad_map = {"Fácil":1, "Medio":2, "Difícil":3, "Avanzado":4}
    n_ocultos = dificultad_map[nivel]
    expresion = random.choice(formulas)
    latex = convertir_a_latex(expresion)
    tokens = re.findall(r"(\\[a-zA-Z]+|[λμρc\d\^\{\}])", latex)
    ocultar = random.sample(tokens, min(n_ocultos, len(tokens)-1))
    respuestas = ocultar.copy()
    for tok in ocultar:
        latex = latex.replace(tok, "___", 1)
    return latex, respuestas

def evaluar_respuestas(correctas, dadas):
    # Simple: cuenta cuántas coinciden exactamente
    return sum(1 for c,u in zip(correctas, dadas) if c.strip()==u.strip())

def main():
    st.set_page_config(page_title="Memoriza Teoría de Colas", layout="wide")
    st.title("📚 Memoriza tus fórmulas de Teoría de Colas")

    pdf_file = st.file_uploader("Sube tu PDF con fórmulas", type=["pdf"])
    if not pdf_file:
        return

    formulas_por_sistema = extraer_ecuaciones(pdf_file)
    sistema = st.selectbox("Elige un sistema", list(formulas_por_sistema.keys()))
    nivel = st.selectbox("Nivel de dificultad", ["Fácil","Medio","Difícil","Avanzado"])

    if st.button("Generar ejercicio"):
        latex_blancos, respuestas = generar_huecos(formulas_por_sistema[sistema], nivel)
        st.markdown(f"**Fórmula (Nivel {nivel}):**")
        st.latex(latex_blancos)

        user_answers = []
        for i in range(len(respuestas)):
            ans = st.text_input(f"Respuesta hueco #{i+1}", key=f"r{i}")
            user_answers.append(ans)

        if st.button("Enviar respuestas"):
            quality = evaluar_respuestas(respuestas, user_answers)
            scheduler = SM2Scheduler()
            next_interval = scheduler.update_interval(sistema, nivel, quality)
            st.info(f"Siguiente repaso en {next_interval} días")
            tracker = MetricsTracker()
            tracker.log_attempt(sistema, nivel, quality, time_spent=0)
            st.success(f"Tu calidad de respuesta: {quality}/{len(respuestas)}")

    tracker = MetricsTracker()
    if st.button("Exportar métricas a CSV"):
        df = tracker.get_dataframe()
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV", data=csv, file_name="metricas.csv")

    if st.checkbox("Mostrar estadísticas"):
        st.json(tracker.get_stats())

if __name__ == "__main__":
    main()
