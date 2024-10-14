import streamlit as st
import pandas as pd
import requests

def table_upload(api_keys, overwrite):
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({
            f"Column {i+1}": [""] * 1 for i in range(3)  # Initial state: 3 columns and 4 rows
        })
    st.subheader("Step 1: Create your table")

    col1, col2, col3 = st.columns([0.3, 0.3, 2])  # Adjust the width of the columns

    with col1:
        if st.button("Add Column", key="add_column_button"):
            new_col_name = f"New Column {len(st.session_state.data.columns) + 1}"
            st.session_state.data[new_col_name] = [""] * len(st.session_state.data)
    with col2:
        if st.button("Remove Column", key="remove_column_button"):
            if len(st.session_state.data.columns) > 1:
                st.session_state.data = st.session_state.data.iloc[:, :-1]
            else:
                st.warning("Cannot remove the last column.")

    # Column name editor
    st.subheader("Step 2: Update Column Names")
    new_column_names = {}
    col1, col2, col3 = st.columns(3)
    for i, col in enumerate(st.session_state.data.columns):
        with [col1, col2, col3][i % 3]:
            new_name = st.text_input(
                f"Rename '{col}'",
                value=col,
                key=f"rename_{col}",
                label_visibility="collapsed",
                help=f"Current name: {col}"
            )
            new_column_names[col] = new_name
    if st.button("Update Column Names"):
        st.session_state.data.rename(columns=new_column_names, inplace=True)
        st.success("Column names updated successfully!")

    # Data editor
    st.subheader("Step 3: Add Data")
    with st.form("data_form"):
        edited_data = st.data_editor(
            st.session_state.data,
            num_rows="dynamic",
            use_container_width=True,
            key="data_editor",
            hide_index=True
        )
        submit_button = st.form_submit_button("Update Table")

    if submit_button:
        st.session_state.data = edited_data

    # Add a text input for the table name
    table_name = st.text_input("Enter a name for your table:", value="Uploaded Table")

    # Button to trigger upload
    if st.button("Upload to Voiceflow", key="upload_button"):
        if not api_keys.get("VOICEFLOW"):
            st.error("Please enter your Voiceflow API key.")
        elif st.session_state.data.empty or st.session_state.data.isna().all().all():
            st.error("Please enter some data.")
        elif not table_name:
            st.error("Please enter a name for your table.")
        else:
            cleaned_data = st.session_state.data.dropna(how='all').dropna(axis=1, how='all')
            items = cleaned_data.to_dict('records')
            searchable_fields = list(cleaned_data.columns)
            payload = {
                "data": {
                    "name": table_name,
                    "schema": {
                        "searchableFields": searchable_fields
                    },
                    "items": items
                }
            }
            # Modify the URL based on the overwrite option
            url = f"https://api.voiceflow.com/v1/knowledge-base/docs/upload/table?overwrite={'true' if overwrite else 'false'}"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": api_keys["VOICEFLOW"]
            }
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                st.success("Data successfully uploaded to Voiceflow!")
                st.json(response.json())
            except requests.exceptions.RequestException as e:
                st.error(f"Error uploading to Voiceflow: {str(e)}")
                if response.text:
                    st.error(f"Response: {response.text}")
