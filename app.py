import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from rapidfuzz import process, fuzz
import time
import re

# -------------------------------------------------------------
# CONFIGURACIÓN BÁSICA
# -------------------------------------------------------------
st.set_page_config(
    page_title="Prompt SAC",
    page_icon="💬",
    layout="centered"
)

# -------------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------------
if "busqueda_realizada" not in st.session_state:
    st.session_state.busqueda_realizada = False

if "categoria_actual" not in st.session_state:
    st.session_state.categoria_actual = None

# -------------------------------------------------------------
# ESTILOS
# -------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;700&display=swap');
body, input, textarea { font-family: 'Nunito', sans-serif; }
.main { background: linear-gradient(135deg, #ffe6f2, #e8f2ff); }

.title-box {
    background: #ffb6da;
    padding: 20px;
    border-radius: 25px;
    text-align: center;
    font-size: 34px;
    font-weight: 700;
    color: white;
    margin-bottom: 15px;
    box-shadow: 0 0 20px rgba(255, 100, 150, 0.4);
}

.big-input textarea {
    background: #fff8fc !important;
    border: 2px solid #ffb6da !important;
    border-radius: 18px !important;
    padding: 14px !important;
    font-size: 18px !important;
    box-shadow: 0px 4px 15px rgba(255, 170, 220, 0.4) !important;
    height: 60px !important;
}

.ios-blue {
    background: #4da3ff;
    color: white;
    padding: 14px 18px;
    border-radius: 18px;
    max-width: 90%;
    margin: 10px 0 10px auto;
}

.ios-gray {
    background: #e5e5ea;
    color: #000;
    padding: 14px 18px;
    border-radius: 18px;
    max-width: 90%;
    margin: 10px auto 10px 0;
}

.typing {
    background: #ffffffa8;
    padding: 10px 16px;
    border-radius: 14px;
    font-size: 15px;
    color: #555;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# TÍTULO
# -------------------------------------------------------------
st.markdown("<div class='title-box'>💬 PROMPT SAC</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# GOOGLE SHEETS (STREAMLIT CLOUD SAFE)
# -------------------------------------------------------------
try:
    # Scope actualizado
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(
        "12EPBC-PCL4IjAGuLuBISJ7S93weBGYMQrmzG3VP2ywg"
    ).sheet1

    data = sheet.get_all_records()

except Exception as e:
    st.error("❌ Error al conectar con Google Sheets")
    st.error(str(e))
    st.stop()

# -------------------------------------------------------------
# CAJA DE TEXTO
# -------------------------------------------------------------
with st.form(key="user_form"):
    st.markdown("<div class='big-input'>", unsafe_allow_html=True)
    user_input = st.text_area(
        "",
        placeholder="Escribe aquí tu consulta… ✨"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    submit_button = st.form_submit_button("Enviar 💌")

# -------------------------------------------------------------
# PROCESAMIENTO DE BÚSQUEDA
# -------------------------------------------------------------
if submit_button and user_input.strip():

    typing = st.empty()
    typing.markdown("<div class='typing'>💭 Escribiendo…</div>", unsafe_allow_html=True)
    time.sleep(1)
    typing.empty()

    categorias = [row["categoria"] for row in data]
    resultado = process.extractOne(
        user_input,
        categorias,
        scorer=fuzz.WRatio
    )

    if resultado:
        best_match, score, _ = resultado
    else:
        st.warning("No encontré una categoría relacionada 😥")
        st.stop()

    st.session_state.busqueda_realizada = True
    st.session_state.categoria_actual = best_match

    st.markdown(
        f"<div class='ios-gray'>📌 Categoría sugerida:<br><b>{best_match}</b><br>"
        f"<small>Similaridad: {score}%</small></div>",
        unsafe_allow_html=True
    )

# -------------------------------------------------------------
# MOSTRAR RESULTADOS
# -------------------------------------------------------------
if st.session_state.busqueda_realizada and st.session_state.categoria_actual:

    match = next(
        (row for row in data if row["categoria"] == st.session_state.categoria_actual),
        None
    )

    if match:
        partes = [p.strip() for p in match["prompt_recomendado"].split('"') if p.strip()]
        for p in partes:
            st.markdown(f"<div class='ios-blue'>{p}</div>", unsafe_allow_html=True)

        texto = match["respuesta_recomendada"]
        bloques = re.findall(r'"([^"]+)"', texto)
        if bloques:
            for b in bloques:
                st.markdown(f"<div class='ios-gray'>{b}</div>", unsafe_allow_html=True)
        else:
            for r in texto.split("\n"):
                if r.strip():
                    st.markdown(f"<div class='ios-gray'>{r}</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# SELECTOR DE CATEGORÍAS
# -------------------------------------------------------------
if st.session_state.busqueda_realizada:

    categorias = sorted(set(row["categoria"] for row in data))

    if st.session_state.categoria_actual not in categorias:
        st.session_state.categoria_actual = categorias[0]

    st.selectbox(
        "📂 Cambiar categoría:",
        categorias,
        index=categorias.index(st.session_state.categoria_actual),
        key="categoria_actual"
    )

