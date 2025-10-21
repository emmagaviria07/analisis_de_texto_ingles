import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator

# ===============================
# 🌈 CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="Analizador Emocional de Texto",
    page_icon="💬",
    layout="wide"
)

# ===============================
# 🎨 ENCABEZADO
# ===============================
st.title("💬 Analizador Emocional de Texto con TextBlob")
st.markdown("""
Explora la **emoción, tono y enfoque** detrás de tus palabras 🌟  
Esta herramienta analiza tu texto en español y traduce internamente al inglés  
para obtener una lectura más precisa del **sentimiento** y la **subjetividad**.
""")

st.divider()

# ===============================
# 🔧 OPCIONES LATERALES
# ===============================
st.sidebar.title("⚙️ Configuración")
modo = st.sidebar.radio(
    "Selecciona cómo ingresar el texto:",
    ["✏️ Escribir texto", "📁 Subir archivo"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Consejo: entre más largo sea el texto, más preciso será el análisis.")

# ===============================
# 🧩 FUNCIONES BASE
# ===============================
def contar_palabras(texto):
    stop_words = set([
        "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con", "contra",
        "cual", "cuando", "de", "del", "desde", "donde", "durante", "el", "ella", "ellos", "en",
        "entre", "era", "es", "esta", "este", "ha", "había", "han", "hasta", "la", "las", "lo",
        "los", "me", "mi", "muy", "no", "nos", "o", "para", "pero", "por", "que", "se", "sin",
        "sobre", "su", "sus", "te", "tu", "un", "una", "uno", "y", "ya", "yo"
    ])
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    conteo = {}
    for palabra in palabras_filtradas:
        conteo[palabra] = conteo.get(palabra, 0) + 1
    conteo_ordenado = dict(sorted(conteo.items(), key=lambda x: x[1], reverse=True))
    return conteo_ordenado, palabras_filtradas

translator = Translator()

def traducir_texto(texto):
    try:
        return translator.translate(texto, src='es', dest='en').text
    except Exception as e:
        st.error(f"❌ Error al traducir: {e}")
        return texto

def procesar_texto(texto):
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity

    frases_es = [f.strip() for f in re.split(r'[.!?]+', texto) if f.strip()]
    frases_en = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]

    frases_combinadas = []
    for i in range(min(len(frases_es), len(frases_en))):
        frases_combinadas.append({"original": frases_es[i], "traducido": frases_en[i]})
    
    contador_palabras, palabras = contar_palabras(texto_ingles)

    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "texto_original": texto,
        "texto_traducido": texto_ingles
    }

# ===============================
# 📊 VISUALIZACIONES
# ===============================
def mostrar_resultados(r):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💖 Sentimiento y Subjetividad")
        st.write("**Nivel de Sentimiento:**")
        st.progress((r["sentimiento"] + 1) / 2)
        if r["sentimiento"] > 0.05:
            st.success(f"Positivo ({r['sentimiento']:.2f}) 🌞")
        elif r["sentimiento"] < -0.05:
            st.error(f"Negativo ({r['sentimiento']:.2f}) 🌧️")
        else:
            st.info(f"Neutral ({r['sentimiento']:.2f}) 🌤️")

        st.write("**Grado de Subjetividad:**")
        st.progress(r["subjetividad"])
        if r["subjetividad"] > 0.5:
            st.warning(f"Alta subjetividad ({r['subjetividad']:.2f}) 💭")
        else:
            st.info(f"Baja subjetividad ({r['subjetividad']:.2f}) 🧠")

    with col2:
        st.subheader("🔠 Palabras Más Frecuentes")
        if r["contador_palabras"]:
            top10 = dict(list(r["contador_palabras"].items())[:10])
            st.bar_chart(top10)
        else:
            st.write("No se encontraron palabras relevantes.")

    st.divider()
    st.subheader("🌍 Texto Original y Traducción")
    with st.expander("Ver comparación completa"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Texto Original (Español):**")
            st.text(r["texto_original"])
        with c2:
            st.markdown("**Texto Traducido (Inglés):**")
            st.text(r["texto_traducido"])

    st.divider()
    st.subheader("🪶 Frases Analizadas")
    if r["frases"]:
        for i, f in enumerate(r["frases"][:8], 1):
            blob_frase = TextBlob(f["traducido"])
            s = blob_frase.sentiment.polarity
            if s > 0.05:
                emoji = "😊"
            elif s < -0.05:
                emoji = "😟"
            else:
                emoji = "😐"
            st.write(f"{i}. {emoji} **Original:** *\"{f['original']}\"*")
            st.write(f"   **Traducción:** *\"{f['traducido']}\"* (Sentimiento: {s:.2f})")
            st.markdown("---")
    else:
        st.write("No se detectaron frases en el texto.")

# ===============================
# 💬 ENTRADA DE TEXTO / ARCHIVO
# ===============================
if modo == "✏️ Escribir texto":
    st.subheader("✍️ Escribe tu texto para analizar:")
    texto = st.text_area("", height=180, placeholder="Escribe o pega aquí tu texto...")
    if st.button("🚀 Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando sentimientos... 💭"):
                resultados = procesar_texto(texto)
                mostrar_resultados(resultados)
        else:
            st.warning("Por favor, ingresa algún texto para analizar.")

else:
    st.subheader("📂 Sube un archivo de texto (.txt, .csv o .md)")
    archivo = st.file_uploader("", type=["txt", "csv", "md"])
    if archivo is not None:
        contenido = archivo.getvalue().decode("utf-8")
        with st.expander("Ver contenido del archivo"):
            st.text(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))
        if st.button("📈 Analizar archivo"):
            with st.spinner("Procesando archivo... 🔍"):
                resultados = procesar_texto(contenido)
                mostrar_resultados(resultados)

# ===============================
# 📘 SECCIÓN DE INFORMACIÓN
# ===============================
with st.expander("ℹ️ Sobre el análisis"):
    st.markdown("""
    ### Explicación del modelo:
    - **Sentimiento:** mide si el tono del texto es positivo, negativo o neutral.
    - **Subjetividad:** refleja si el texto expresa opinión (subjetivo) o hechos (objetivo).

    ### Tecnologías utilizadas:
    - 🧠 **TextBlob:** para análisis lingüístico y polaridad.
    - 🌐 **Googletrans:** para traducir al inglés y mejorar precisión.
    - 🧩 **Streamlit:** para interfaz interactiva.
    """)

# ===============================
# 🪄 PIE DE PÁGINA
# ===============================
st.markdown("---")
st.markdown("Creado con ❤️ por un desarrollador curioso — versión estética renovada ✨")
