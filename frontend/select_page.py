import streamlit as st
import initial_page
import chatbot_page

# Inicializar el estado de la aplicación
if "page" not in st.session_state:
    st.session_state.page = "main"


# Controlar qué página se muestra
if st.session_state.page == "main":
    initial_page.loading_data_page()
elif st.session_state.page == "page1":
    chatbot_page.chatbot_page()
