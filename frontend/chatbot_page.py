import streamlit as st
import pandas as pd


# Select Page to Go
def go_to_page0():
    st.session_state.page = "main"


def chatbot_page():

    df = st.session_state.data

    with st.container():
        # Send to next page
        col5, col6 = st.columns([2, 3])

        with col6:
            st.button("Return to Load Data", on_click=go_to_page0, type="primary")

    col, col0 = st.columns([1, 5])
    with col0:
        st.title("Phitter AI Assistant👋")

    # Store LLM generated responses
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What do you want to do with Phitter?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            question = prompt

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = "Hola"  # Backend Here
                placeholder = st.empty()
                full_response = df.loc[0, 1]
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
