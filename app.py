import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from rapidfuzz import process, fuzz
import time
import re

# -------------------------------------------------------------
# CONFIGURACIÓN BÁSICA
# -------------------------------------------------------------
st.set_page_config(page_title="Prompt SAC", page_icon="💬", layout="centered")

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
    width: fit-content;
    max-width: 90%;
    margin: 10px 0;
    margin-left: auto;
    position: relative;
    box-shadow: 0px 4px 12px rgba(77, 163, 255, 0.45);
    animation: fadeIn 0.4s ease;
}
.ios-blue::after {
    content: "";
    position: absolute;
    right: -6px;
    bottom: 0px;
    width: 12px;
    height: 12px;
    background: #4da3ff;
    border-bottom-left-radius: 10px;
}

.ios-gray {
    background: #e5e5ea;
    color: #000;
    padding: 14px 18px;
    border-radius: 18px;
    width: fit-content;
    max-width: 90%;
    margin: 10px 0;
    margin-right: auto;
    position: relative;
    box-shadow: 0px 4px 12px rgba(150, 150, 150, 0.35);
    animation: fadeIn 0.4s ease;
}
.ios-gray::after {
    content: "";
    position: absolute;
    left: -6px;
    bottom: 0px;
    width: 12px;
    height: 12px;
    background: #e5e5ea;
    border-bottom-right-radius: 10px;
}

.typing {
    background: #ffffffa8;
    padding: 10px 16px;
    border-radius: 14px;
    width: fit-content;
    font-size: 15px;
    color: #555;
    margin: 8px 0;
    box-shadow: 0 0 12px #b9d3ff99;
    animation: blink 1.2s infinite;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes blink { 0% { opacity: 0.3; } 50% { opacity: 1; } 100% { opacity: 0.3; } }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# TÍTULO
# -------------------------------------------------------------
st.markdown("<div class='title-box'>💬 PROMPT SAC</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# GOOGLE SHEETS
# -------------------------------------------------------------
try:
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets, scopecambio credenciales

)

    client = gspread.authorize(creds)
    sheet = client.open_by_key("12EPBC-PCL4IjAGuLuBISJ7S93weBGYMQrmzG3VP2ywg").sheet1
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
        placeholder="Escribe aquí tu consulta… ✨",
        height=60
    )
    st.markdown("</div>", unsafe_allow_html=True)
    submit_button = st.form_submit_button(label="Enviar 💌")

# -------------------------------------------------------------
# PROCESAMIENTO
# -------------------------------------------------------------
if submit_button and user_input:
    st.markdown(f"<div class='user-bubble'>🙂 {user_input}</div>", unsafe_allow_html=True)

    typing_placeholder = st.empty()
    typing_placeholder.markdown("<div class='typing'>💭 Escribiendo…</div>", unsafe_allow_html=True)
    time.sleep(1.2)
    typing_placeholder.empty()

    todas_categorias = [row["categoria"] for row in data]
    best_match, score, idx = process.extractOne(user_input, todas_categorias, scorer=fuzz.WRatio)

    st.markdown(
        f"<div class='bot-bubble'>📌 Categoría sugerida: <b>{best_match}</b><br><span style='opacity:0.7'>Similaridad: {score}%</span></div>",
        unsafe_allow_html=True
    )

    categoria_final = best_match
    match = next((row for row in data if row["categoria"] == categoria_final), None)

    if match:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # ----- PROMPTS -----
        st.markdown("<div class='card-title'>✨ Prompt sugerido:</div>", unsafe_allow_html=True)
        partes = [p.strip() for p in match["prompt_recomendado"].split('"') if p.strip()]
        for p in partes:
            st.markdown(f"<div class='ios-blue'>{p}</div>", unsafe_allow_html=True)

        # ----- RESPUESTAS -----
        st.markdown("<div class='card-title' style='margin-top:15px;'>📝 Respuesta recomendada:</div>", unsafe_allow_html=True)

        # Mostrar como UN solo mensaje todo lo que esté entre comillas
        texto = match["respuesta_recomendada"]
        bloques = re.findall(r'"([^"]+)"', texto)
        if bloques:
            for b in bloques:
                st.markdown(f"<div class='ios-gray'>{b}</div>", unsafe_allow_html=True)
        else:
            respuestas = texto.split("\n")
            for r in respuestas:
                if r.strip():
                    st.markdown(f"<div class='ios-gray'>{r.strip()}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # OPCIÓN DE CATEGORÍA POST-BÚSQUEDA
        # -------------------------------------------------------------
        choices = sorted(list(set([row["categoria"] for row in data])))
        categoria_seleccionada = st.selectbox(
            "📂 Selecciona otra categoría (opcional):",
            [""] + choices,
            index=0
        )

        if categoria_seleccionada != "":
            match = next((row for row in data if row["categoria"] == categoria_seleccionada), None)
            if match:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>✨ Prompt sugerido:</div>", unsafe_allow_html=True)
                partes = [p.strip() for p in match["prompt_recomendado"].split('"') if p.strip()]
                for p in partes:
                    st.markdown(f"<div class='ios-blue'>{p}</div>", unsafe_allow_html=True)

                st.markdown("<div class='card-title' style='margin-top:15px;'>📝 Respuesta recomendada:</div>", unsafe_allow_html=True)

                texto = match["respuesta_recomendada"]
                bloques = re.findall(r'"([^"]+)"', texto)
                if bloques:
                    for b in bloques:
                        st.markdown(f"<div class='ios-gray'>{b}</div>", unsafe_allow_html=True)
                else:
                    respuestas = texto.split("\n")
                    for r in respuestas:
                        if r.strip():
                            st.markdown(f"<div class='ios-gray'>{r.strip()}</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
