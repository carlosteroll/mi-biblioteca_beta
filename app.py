import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(
    page_title="Mi Biblioteca Personal", 
    page_icon="📚", 
    layout="wide"
)

# 2. Estilos visuales
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
        background-color: #4F46E5;
        color: white;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #4F46E5;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📚 Mi Biblioteca Personal")

@st.cache_data
def cargar_datos():
    df = pd.read_excel("biblioteca.xlsx")
    df.columns = df.columns.str.strip()
    return df

try:
    df = cargar_datos()

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total de Libros", len(df))
    col_m2.metric("Autores Únicos", df['Autor'].nunique() if 'Autor' in df.columns else len(df))
    col_m3.metric("Estado IA", "Gemini 2.0 Flash 🤖")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["🔍 Buscador", "🤖 Asistente IA", "📋 Préstamos"])

    # --- PESTAÑA 1: BUSCADOR ---
    with tab1:
        st.header("Buscador de Libros")
        busqueda = st.text_input("Buscar por cualquier campo (título, autor, tema...):")
        
        if busqueda:
            mascara = df.astype(str).apply(
                lambda row: row.str.contains(busqueda, case=False, na=False)
            ).any(axis=1)
            resultado = df[mascara]
            st.dataframe(resultado, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

    # --- PESTAÑA 2: CHAT CON IA ---
    with tab2:
        st.header("Pregunta a la IA sobre tu biblioteca")
        
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        
        if api_key:
            genai.configure(api_key=api_key)
            
            # Modelo activo oficial de la API de Google
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            pregunta = st.text_input("¿Qué libro estás buscando o qué tema te interesa?")
            
            if st.button("✨ Consultar a la IA") and pregunta:
                columnas_utiles = [c for c in df.columns if any(k in c.lower() for k in ['títu', 'titu', 'autor', 'tema', 'estant', 'fila', 'balda', 'ubic'])]
                df_resumen = df[columnas_utiles] if len(columnas_utiles) > 0 else df
                contexto_libros = df_resumen.to_csv(index=False)
                
                prompt = f"""
                Eres el bibliotecario virtual de mi biblioteca personal. 
                Esta es la lista completa de mis libros con sus ubicaciones (formato CSV):
                
                {contexto_libros}
                
                Responde a la consulta del usuario basándote en la lista de libros. 
                Dile qué libro o libros le recomiendas y especifica en qué estantería, balda u otra ubicación se encuentran según los datos.
                
                Consulta del usuario: {pregunta}
                """
                
                try:
                    with st.spinner("Buscando en la estantería... 📖"):
                        response = model.generate_content(prompt)
                        
                        with st.container(border=True):
                            st.subheader("🤖 Respuesta del Bibliotecario")
                            st.markdown(response.text)
                except Exception as err:
                    st.error(f"Error en la consulta a la IA: {err}")
        else:
            st.warning("Por favor, configura tu GEMINI_API_KEY en los secretos de Streamlit (Settings > Secrets).")

    # --- PESTAÑA 3: CONTROL DE PRÉSTAMOS ---
    with tab3:
        st.header("Gestión de Préstamos")
        columna_titulo = df.columns[0]
        libro_seleccionado = st.selectbox("Selecciona un libro:", df[columna_titulo].values)
        persona = st.text_input("¿A quién se lo prestas?")
        
        if st.button("Registrar Préstamo"):
            st.success(f"Registrado: '{libro_seleccionado}' prestado a {persona}.")

except Exception as e:
    st.error(f"Error al cargar el archivo Excel: {e}")
