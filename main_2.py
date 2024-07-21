import os

import numpy as np
import pandas as pd
import phitter
from llama_index.core.agent.react import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.together import TogetherLLM
import dotenv
import streamlit as st
import requests
import io

# Inicializar el estado de la aplicación
if "page" not in st.session_state:
    st.session_state.page = "main"

dotenv.load_dotenv(dotenv.find_dotenv())
os.environ["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY")


def get_column_data(column_name: str) -> list[float]:
    """
    Gets the data from a specific column of the global DataFrame.
    """
    df = st.session_state.data
    print(df.head())
    return df[column_name].tolist()


def fit_distributions_to_data(data: list[float]) -> float:
    """
    Fit the best probability distribution to a dataset
    """
    print(data)
    phitter_cont = phitter.PHITTER(data=data)
    phitter_cont.fit(n_workers=2)
    id_distribution = phitter_cont.best_distribution["id"]
    parameters = phitter_cont.best_distribution["parameters"]
    parameters_str = ", ".join([f"{k}: {v:.4g}" for k, v in parameters.items()])
    return (
        f"The best distribution is {id_distribution} with parameters {parameters_str}"
    )


def main_backend(query: str):

    get_column_tool = FunctionTool.from_defaults(
        fn=get_column_data,
        name="get_column_data",
        description="Gets the data from a specific column of the global DataFrame.",
    )
    fit_distribution_tool = FunctionTool.from_defaults(
        fn=fit_distributions_to_data,
        name="fit_distribution",
        description="Find the best probability distribution to a dataset and returns the distribution name and parameters.",
    )

    llm = TogetherLLM(model="meta-llama/Llama-3-70b-chat-hf")

    tools = [get_column_tool, fit_distribution_tool]
    agent = ReActAgent.from_tools(tools, llm=llm, verbose=False)

    response = agent.chat(query)

    return response


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
                placeholder = st.empty()
                full_response = main_backend(question)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)


def go_to_page1(df: pd.DataFrame):
    st.session_state.page = "page1"
    st.session_state.data = df


def send_next_page(df: pd.DataFrame):
    # Send to AI Assistant page
    st.markdown(
        "If the above data is correct, click on :green[NEXT] to use the AI assistant for Phitter"
    )
    col5, col6 = st.columns([2, 3])
    with col6:
        st.button("Next", on_click=lambda: go_to_page1(df), type="primary")


def loading_data_page():
    col, col0 = st.columns([1, 5])
    with col0:
        st.title("Welcome to Phitter AI! 👋")
    st.markdown(
        "Load your table with numerical values and discover which distribution they fit or any other statistical question about the data by asking an agent powered by Llama3, using the Phitter library. Obtain detailed analyses and precise answers quickly and easily."
    )
    st.markdown("**Choose the way you want your data to be read (tabular data)**")

    with st.container():

        # Dive into two columns
        col1, col2 = st.columns([5, 1])

        # First Column
        with col1:
            url_input = st.text_input(
                "Write down the :green[***URL***] where we can find your data"
            )

        # Second Column
        with col2:
            st.markdown("")
            # st.markdown("")
            st.markdown("")
            url_button = st.button("Read URL")

        st.markdown("**or**")

        upload_file = st.file_uploader(
            "Upload your :green[***CSV***], :green[***TXT***] or :green[***XLSX***] file"
        )
        # Checkbox to act as the switch
        with_headers = st.checkbox(
            "Does your data have the **First Row** as a **Header**?"
        )
        if upload_file:
            if (
                upload_file.type == "text/csv"
                or upload_file.type == "text/plain"
                and with_headers
            ):
                df = pd.read_csv(upload_file)
                st.dataframe(df.head())
                send_next_page(df)
            elif (
                upload_file.type == "text/csv"
                or upload_file.type == "text/plain"
                and with_headers == False
            ):
                df = pd.read_csv(upload_file, header=None)
                st.dataframe(df.head())
                send_next_page(df)
            elif (
                upload_file.type
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                and with_headers
            ):
                # Dive into two columns
                col1, col2 = st.columns([5, 1])

                # First Column
                with col1:
                    user_input = st.text_input(
                        ":blue[By default we will consider **the First Sheet** in your XLSX file. If you need to use another Sheet, write it down below, then click on ***Update***]"
                    )

                # Second Column
                with col2:
                    st.markdown("")
                    st.markdown("")
                    st.markdown("")
                    submit_button = st.button("Update")

                # Read According to User Choice
                if submit_button == False or (
                    submit_button == True and user_input == ""
                ):
                    df = pd.read_excel(upload_file)
                    st.dataframe(df.head())
                    send_next_page(df)
                else:
                    df = pd.read_excel(upload_file, sheet_name=user_input)
                    st.dataframe(df.head())
                    send_next_page(df)
            elif (
                upload_file.type
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                and with_headers == False
            ):

                # Dive into two columns
                col3, col4 = st.columns([5, 1])

                # First Column
                with col3:
                    user_input = st.text_input(
                        ":blue[By default we will consider **the First Sheet** in your XLSX file. If you need to use another Sheet, write it down below, then click on ***Update***]"
                    )

                # Second Column
                with col4:
                    st.markdown("")
                    st.markdown("")
                    st.markdown("")
                    submit_button = st.button("Update")

                # Read According to User Choice
                if submit_button == False or (
                    submit_button == True and user_input == ""
                ):
                    df = pd.read_excel(upload_file, header=None)
                    st.dataframe(df.head())
                    send_next_page(df)
                else:
                    df = pd.read_excel(upload_file, header=None, sheet_name=user_input)
                    st.dataframe(df.head())
                    send_next_page(df)

            else:
                st.markdown(
                    ":red[File type not recognized. Please upload the correct formats: ] :green[***CSV***] :red[,] :green[***TXT***] :red[or] :green[***XLSX***].\n\n:red[Please try again.]"
                )
        elif url_input != "" and url_button == True:
            # Realizar la solicitud GET
            response = requests.get(url_input)

            if response.status_code == 200:
                # Read file and transform to be readable
                file_data = io.StringIO(response.text)

                if with_headers:
                    # Store in a df
                    df = pd.read_csv(file_data)
                    st.dataframe(df.head())
                else:
                    # Store in a df
                    df = pd.read_csv(file_data, header=None)
                    st.dataframe(df.head())

                send_next_page(df)

            else:
                st.markdown(":red[**Sorry!😭 We were not able to access to your url**]")


# Controlar qué página se muestra
if st.session_state.page == "main":
    loading_data_page()
elif st.session_state.page == "page1":
    chatbot_page()
