import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configuración de la página
st.set_page_config(page_title="Mi Biblioteca Personal", page_icon="📚")
st.title("📚 Mi Biblioteca Personal")

# 1. Cargar la base de datos
@st.cache_data
def cargar_datos():
    df = pd.read_excel("biblioteca.xlsx")
    df.columns = df.columns.str.strip()
    return df

try:
    df = cargar_datos()

    # Pestañas
    tab1, tab2, tab3 = st.tabs(["🔍 Buscador", "🤖 Asistente IA", "📋 Préstamos"])

    # --- PESTAÑA 1: BUSCADOR ---
    with tab1:
        st.header("Buscador de Libros")
        busqueda = st.text_input("Buscar por cualquier campo (título, autor, tema...):")
        
        if busqueda:
            mascara = df.astype(str).apply(lambda row: row.str.contains(busqueda, case=False, na=False)).any(axis=1)
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
            # Modelo actualizado de Gemini exigido por la API
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            pregunta = st.text_input("¿Qué libro estás buscando o qué tema te interesa?")
            
            if st.button("Consultar") and pregunta:
                # Filtrado ligero para no sobrepasar el límite de tokens por consulta
                palabras = pregunta.split()
                mascara = df.astype(str).apply(
                    lambda row: any(p.lower() in str(row).lower() for p in palabras if len(p) > 3)
                , axis=1)
                
                df_filtrado = df[mascara]
                
                if len(df_filtrado) < 3:
                    df_contexto = df.head(80)
                else:
                    df_contexto = df_filtrado.head(80)
                
                contexto_libros = df_contexto.to_csv(index=False)
                
                prompt = f"""
                Eres el bibliotecario virtual de mi biblioteca personal. 
                Esta es una lista seleccionada de mis libros con sus ubicaciones y detalles:
                
                {contexto_libros}
                
                Responde a la siguiente consulta del usuario basándote en la lista de libros anterior. 
                Dile qué libro o libros le recomiendas de la lista y especifica en qué estantería, balda u otra ubicación se encuentran según los datos.
                
                Consulta del usuario: {pregunta}
                """
                
                try:
                    with st.spinner("Consultando a la IA..."):
                        response = model.generate_content(prompt)
                        st.write(response.text)
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
