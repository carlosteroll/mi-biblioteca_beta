import streamlit as st
import pandas as pd
from groq import Groq

# 1. Configuración de la página
st.set_page_config(
    page_title="Mi Biblioteca Personal", 
    page_icon="📚", 
    layout="wide"
)

# 2. CSS Personalizado para animaciones y diseño
st.markdown("""
    <style>
    /* Estilo general y animaciones de botones */
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
    
    /* Contadores elevados */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #4F46E5;
    }
    
    /* Pestañas estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.title("📚 Mi Biblioteca Personal")

# Cargar la base de datos de libros
@st.cache_data
def cargar_datos():
    df = pd.read_excel("biblioteca.xlsx")
    df.columns = df.columns.str.strip()
    return df

try:
    df = cargar_datos()

    # Métricas destacadas en la parte superior
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total de Libros", len(df))
    col_m2.metric("Autores Únicos", df['Autor'].nunique() if 'Autor' in df.columns else len(df))
    col_m3.metric("Estado IA", "Groq (Llama 3.3) ⚡")

    st.divider()

    # Pestañas de navegación
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

   # --- PESTAÑA 2: CHAT CON IA (Groq API) ---
    with tab2:
        st.header("Pregunta a la IA sobre tu biblioteca")
        
        api_key = st.secrets.get("GROQ_API_KEY", "")
        
        if api_key:
            client = Groq(api_key=api_key)
            
            pregunta = st.text_input("¿Qué libro estás buscando o qué tema te interesa?")
            
            if st.button("✨ Consultar a la IA") and pregunta:
                palabras = pregunta.split()
                mascara = df.astype(str).apply(
                    lambda row: any(p.lower() in str(row).lower() for p in palabras if len(p) > 3)
                , axis=1)
                
                df_filtrado = df[mascara]
                df_contexto = df_filtrado.head(100) if len(df_filtrado) >= 3 else df.head(100)
                contexto_libros = df_contexto.to_csv(index=False)
                
                prompt = f"""
                Eres el bibliotecario virtual de mi biblioteca personal. 
                Esta es la lista seleccionada de mis libros con sus ubicaciones y detalles:
                
                {contexto_libros}
                
                Responde a la consulta del usuario basándote únicamente en la lista de libros. 
                Dile qué libro o libros le recomiendas y especifica exactamente en qué estantería, balda u otra ubicación se encuentran según los datos.
                
                Consulta del usuario: {pregunta}
                """
                
                try:
                    with st.spinner("Buscando en la estantería... 📖"):
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "user", 
                                    "content": prompt
                                }
                            ],
                            model="llama-3.3-70b-versatile",  # <--- Modelo activo y ultra rápido
                        )
                        
                        with st.container(border=True):
                            st.subheader("🤖 Respuesta del Bibliotecario")
                            st.markdown(chat_completion.choices[0].message.content)
                except Exception as err:
                    st.error(f"Error en la consulta a la IA: {err}")
        else:
            st.warning("Por favor, configura tu GROQ_API_KEY en los secretos de Streamlit (Settings > Secrets).")
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
