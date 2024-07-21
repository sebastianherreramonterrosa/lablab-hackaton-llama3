import streamlit as st
import pandas as pd
import requests
import io

global df


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
