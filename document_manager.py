
import streamlit as st
import requests
import pandas as pd
import json

# --- Helper Functions ---

# --- API Functions ---

def get_all_documents(api_key):
    """Fetches all documents from the Voiceflow Knowledge Base with pagination."""
    all_documents = []
    page = 1
    with st.spinner("Fetching documents from Voiceflow..."):
        while True:
            try:
                url = f"https://api.voiceflow.com/v1/knowledge-base/docs?page={page}&limit=100"
                headers = {"accept": "application/json", "Authorization": api_key}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                documents = data.get('data', [])
                if not documents:
                    break
                all_documents.extend(documents)
                if not data.get('pagination', {}).get('hasNext', False):
                    break
                page += 1
            except requests.exceptions.RequestException as e:
                st.error(f"API Error: Failed to fetch documents. {e}")
                return []
    return all_documents

def delete_document(api_key, document_id):
    """Deletes a specific document by its ID."""
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{document_id}"
    headers = {"Authorization": api_key}
    try:
        response = requests.delete(url, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: Failed to delete document {document_id}. {e}")
        return False

def update_document_metadata(api_key, document_id, metadata):
    """Updates metadata for a specific document."""
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{document_id}"
    headers = {"accept": "application/json", "content-type": "application/json", "Authorization": api_key}
    payload = {"metadata": metadata}
    try:
        response = requests.patch(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        # Check if the response has JSON and a message
        try:
            error_message = response.json().get("message", str(e))
        except json.JSONDecodeError:
            error_message = str(e)
        st.error(f"API Error for doc {document_id}: {error_message}")
        return False

# --- Main App Logic ---

st.title("📋 Document Manager")

# Use session state to store documents and avoid re-fetching
if 'documents' not in st.session_state:
    st.session_state.documents = []

api_key = st.text_input("Enter your Voiceflow API Key", type="password", key="api_key_input")

if api_key:
    if st.button("🔄 Refresh Document List"):
        st.session_state.documents = get_all_documents(api_key)

    # --- Filtering ---
    search_term = st.text_input("Search by Doc Name, ID, or Tags", key="search_term_input")

    # --- Document Display ---
    if not st.session_state.documents:
        st.info("Click 'Refresh Document List' to load your documents.")
    else:
        # Filter documents based on search term (client-side)
        filtered_docs = st.session_state.documents
        if search_term:
            term = search_term.lower()
            filtered_docs = [doc for doc in filtered_docs if
                           term in doc.get("data", {}).get("name", "").lower() or
                           term in doc.get("documentID", "").lower() or
                           any(term in tag.lower() for tag in doc.get("tags", []))]

        if not filtered_docs:
            st.warning("No documents match your search.")
        else:
            # Format for display
            display_data = []
            for doc in filtered_docs:
                display_data.append({
                    "Doc ID": doc['documentID'],
                    "Doc Name": doc.get("data", {}).get("name", "N/A"),
                    "Added/Updated At": doc.get("updatedAt", "").split("T")[0],
                    "Tags": ", ".join(doc.get("tags", [])),
                })

            df = pd.DataFrame(display_data)
            # Add the selection column to the DataFrame
            df.insert(0, "Select", False)

            # Use st.data_editor to display the table and handle selections
            edited_df = st.data_editor(
                df,
                hide_index=True,
                use_container_width=True,
                column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                disabled=df.columns.drop("Select"),
                key="document_editor" # A single, stable key for the data_editor
            )

            selected_rows = edited_df[edited_df.Select]
            selected_doc_ids = selected_rows["Doc ID"].tolist()

            st.markdown("---")

            # --- Bulk Deletion ---
            if st.button("Delete Selected", disabled=not selected_doc_ids):
                with st.spinner(f"Deleting {len(selected_doc_ids)} documents..."):
                    for doc_id in selected_doc_ids:
                        delete_document(api_key, doc_id)
                st.success("Deletion complete.")
                st.session_state.documents = get_all_documents(api_key)
                st.rerun()
