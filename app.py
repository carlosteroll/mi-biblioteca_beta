import streamlit as st
import pandas as pd
from google import genai

# Configuración de la página
st.set_page_config(page_title="Mi Biblioteca Personal", page_icon="📚")
st.title("📚 Mi Biblioteca Personal")

# 1. Cargar la base de datos
@st.cache_data
def cargar_datos():
    return pd.read_excel("biblioteca.xlsx")

df = cargar_datos()

# Pestañas
tab1, tab2, tab3 = st.tabs(["🔍 Buscador", "🤖 Asistente IA", "📋 Préstamos"])

# --- PESTAÑA 1: BUSCADOR ---
with tab1:
    st.header("Buscador de Libros")
    busqueda = st.text_input("Buscar por título, autor o temática:")
    
    if busqueda:
        resultado = df[
            df['Título'].str.contains(busqueda, case=False, na=False) |
            df['Autor'].str.contains(busqueda, case=False, na=False) |
            df['Temática'].str.contains(busqueda, case=False, na=False)
        ]
        st.dataframe(resultado[['Título', 'Autor', 'Temática', 'Estantería', 'Fila', 'Estado']])
    else:
        st.dataframe(df[['Título', 'Autor', 'Temática', 'Estantería', 'Fila', 'Estado']])

# --- PESTAÑA 2: CHAT CON IA ---
with tab2:
    st.header("Pregunta a la IA sobre tu biblioteca")
    
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    
    if api_key:
        client = genai.Client(api_key=api_key)
        contexto_libros = df.to_string(index=False)
        
        pregunta = st.text_input("¿Qué libro estás buscando o qué tema te interesa?")
        
        if st.button("Consultar"):
            prompt = f"""
            Eres el bibliotecario virtual de mi biblioteca personal. 
            Esta es la lista completa de mis libros y su ubicación:
            
            {contexto_libros}
            
            Responde a la consulta del usuario basándote en la lista de libros. 
            Dile qué libro o libros le recomiendas y especifica en qué Estantería y Fila/Balda se encuentran.
            
            Consulta: {pregunta}
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            st.write(response.text)
    else:
        st.warning("Por favor, configura tu GEMINI_API_KEY en los secretos de Streamlit.")

# --- PESTAÑA 3: CONTROL DE PRÉSTAMOS ---
with tab3:
    st.header("Gestión de Préstamos")
    libro_seleccionado = st.selectbox("Selecciona un libro:", df['Título'].values)
    persona = st.text_input("¿A quién se lo prestas?")
    
    if st.button("Registrar Préstamo"):
        st.success(f"Registrado: '{libro_seleccionado}' prestado a {persona}.")
