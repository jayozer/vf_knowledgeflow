import streamlit as st
import requests

def get_voiceflow_tags(api_key):
    url = "https://api.voiceflow.com/v3alpha/knowledge-base/tags"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    try:
        st.write("Fetching tags...")  # Debug message
        response = requests.get(url, headers=headers)
        
        # Print response details for debugging
        st.write(f"Response status code: {response.status_code}")
        st.write(f"Response content: {response.text}")
        
        response.raise_for_status()
        tags_data = response.json()
        
        # Print parsed data
        st.write(f"Parsed tags data: {tags_data}")
        
        tags = [tag["label"] for tag in tags_data["data"]]
        st.write(f"Extracted tags: {tags}")  # Debug message
        return tags
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Error: {str(e)}")
        return []
    except KeyError as e:
        st.error(f"Data parsing error: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return []

def create_voiceflow_tag(api_key, tag_name):
    url = "https://api.voiceflow.com/v3alpha/knowledge-base/tags"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    payload = {
        "data": {
            "label": tag_name
        }
    }
    
    try:
        st.write("Creating tag...")  # Debug message
        response = requests.post(url, json=payload, headers=headers)
        
        # Print response details for debugging
        st.write(f"Response status code: {response.status_code}")
        st.write(f"Response content: {response.text}")
        
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return False

def get_voiceflow_documents(api_key, document_limit=100):
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs?page=1&limit={document_limit}"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        documents_list = response.json()
        
        # Extract relevant fields
        documents = [
            {
                "name": doc["data"]["name"],
                "documentID": doc["documentID"],
                "tags": doc.get("tags", [])  # Use get() with default empty list
            }
            for doc in documents_list["data"]
        ]
        return documents
    except Exception as e:
        st.error(f"Error fetching documents: {str(e)}")
        return []

def attach_tags_to_document(api_key, document_id, tags):
    """Attach tags to a specific document"""
    url = f"https://api.voiceflow.com/v3alpha/knowledge-base/docs/{document_id}/tags/attach"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    payload = {
        "data": {
            "tags": tags
        }
    }
    
    try:
        st.write(f"Attaching tags to document {document_id}...")  # Debug message
        response = requests.post(url, json=payload, headers=headers)
        
        # Print response details for debugging
        st.write(f"Response status code: {response.status_code}")
        st.write(f"Response content: {response.text}")
        
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return False

def get_tag_id_by_label(api_key, tag_label):
    """Get tag ID from its label"""
    url = "https://api.voiceflow.com/v3alpha/knowledge-base/tags"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tags_data = response.json()
        
        # Find the tag ID that matches the label
        for tag in tags_data["data"]:
            if tag["label"] == tag_label:
                return tag["tagID"]
        return None
    except Exception as e:
        st.error(f"Error getting tag ID: {str(e)}")
        return None

def delete_tag(api_key, tag_id):
    """Delete a tag using its ID"""
    url = f"https://api.voiceflow.com/v3alpha/knowledge-base/tags/{tag_id}"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error deleting tag: {str(e)}")
        return False

def detach_tags_from_document(api_key, document_id, tags_to_detach):
    """Detach tags from a specific document"""
    url = f"https://api.voiceflow.com/v3alpha/knowledge-base/docs/{document_id}/tags/detach"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }
    payload = {
        "data": {
            "tags": tags_to_detach
        }
    }
    
    try:
        st.write(f"Detaching tags from document {document_id}...")  # Debug message
        response = requests.post(url, json=payload, headers=headers)
        
        # Print response details for debugging
        st.write(f"Response status code: {response.status_code}")
        st.write(f"Response content: {response.text}")
        
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error detaching tags: {str(e)}")
        return False

def update_document_tags(api_key, doc_id, new_tags, current_tags):
    """Update document tags by handling both attachments and detachments"""
    success = True
    
    # Find tags to remove (tags in current_tags but not in new_tags)
    tags_to_detach = list(set(current_tags) - set(new_tags))
    
    # Find tags to add (tags in new_tags but not in current_tags)
    tags_to_attach = list(set(new_tags) - set(current_tags))
    
    # Detach removed tags
    if tags_to_detach:
        if not detach_tags_from_document(api_key, doc_id, tags_to_detach):
            success = False
            st.error(f"Failed to detach tags: {tags_to_detach}")
    
    # Attach new tags
    if tags_to_attach:
        if not attach_tags_to_document(api_key, doc_id, tags_to_attach):
            success = False
            st.error(f"Failed to attach tags: {tags_to_attach}")
    
    return success

def kb_tags_page(api_keys):
    st.header("📑 Knowledge Base Document Tags")
    
    # Make "Manage Tags" larger and centered
    st.subheader("🏷️ Manage Tag")
    
    # Create two columns with equal width (instead of three)
    col1, col2 = st.columns(2)
    
    # Existing Tags section in its own container
    with col1:
        with st.container(border=True):
            st.markdown("#### Existing Tags")
            
            if st.session_state.existing_tags:
                cols = st.columns(2)
                for idx, tag in enumerate(st.session_state.existing_tags):
                    with cols[idx % 2]:
                        st.button(
                            f"🏷️ {tag}",
                            key=f"tag_{idx}",
                            help="Click to view documents with this tag"
                        )
            else:
                st.info("No tags exist yet. Create your first tag below.")
            
            # Add Tag List button
            if st.button("List Tags"):
                if "VOICEFLOW" not in api_keys:
                    st.error("Voiceflow API key not found!")
                else:
                    tags = get_voiceflow_tags(api_keys["VOICEFLOW"])
                    if tags:
                        st.session_state.existing_tags = tags
                        st.rerun()
                    else:
                        st.warning("No tags found or error fetching tags.")
    
    # Create New Tag section in its own container
    with col2:
        with st.container(border=True):
            st.markdown("#### Create New Tag")
            new_tag = st.text_input(
                "Tag name",
                key="new_tag_input",
                help="Enter a new tag name and click Create"
            )
            if st.button("Create Tag"):
                if new_tag:
                    if "VOICEFLOW" not in api_keys:
                        st.error("Voiceflow API key not found!")
                    else:
                        if create_voiceflow_tag(api_keys["VOICEFLOW"], new_tag):
                            st.success(f"Tag '{new_tag}' created successfully!")
                            tags = get_voiceflow_tags(api_keys["VOICEFLOW"])
                            if tags:
                                st.session_state.existing_tags = tags
                                st.rerun()
                        else:
                            st.error("Failed to create tag.")
                else:
                    st.warning("Please enter a tag name.")

    # Section 2: Document Tagging Interface
    st.markdown("---")
    st.subheader("📄 Document Tagging")
    
    # Filters
    col1, col2 = st.columns([2, 2])
    with col1:
        search_term = st.text_input(
            "🔍 Search documents",
            placeholder="Enter document name..."
        )
    with col2:
        filter_tags = st.multiselect(
            "🏷️ Filter by existing tags",
            options=st.session_state.existing_tags
        )

    # Replace the hardcoded documents list with API call
    documents = get_voiceflow_documents(api_keys["VOICEFLOW"])
    
    # Apply filters if any
    filtered_docs = documents
    if search_term:
        filtered_docs = [
            doc for doc in filtered_docs 
            if search_term.lower() in doc['name'].lower()
        ]
    if filter_tags:
        filtered_docs = [
            doc for doc in filtered_docs 
            if any(tag in doc['tags'] for tag in filter_tags)
        ]

    # Display documents with tagging interface
    for doc in filtered_docs:
        with st.expander(f"📄 {doc['name']}", expanded=False):
            # Current tags
            st.markdown("**Current tags:**")
            if doc['tags']:
                cols = st.columns(4)
                for idx, tag in enumerate(doc['tags']):
                    with cols[idx % 4]:
                        st.markdown(f"🏷️ {tag}")
            else:
                st.info("No tags assigned")
            
            # Tag selection
            selected_tags = st.multiselect(
                "Add or remove tags",
                options=st.session_state.existing_tags,
                default=doc['tags'],
                key=f"tag_select_{doc['documentID']}"
            )
            
            # Update button
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Update Tags", key=f"update_{doc['documentID']}"):
                    if update_document_tags(api_keys["VOICEFLOW"], 
                                         doc['documentID'], 
                                         selected_tags, 
                                         doc['tags']):
                        st.success("Tags updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update tags.")

    # Move Delete Tag section here, before Statistics
    st.markdown("---")
    st.subheader("🗑️ Delete Tag")
    with st.container(border=True):
        # Create dropdown for tag selection
        tag_to_delete = st.selectbox(
            "Select tag to delete",
            options=st.session_state.existing_tags if st.session_state.existing_tags else [],
            key="delete_tag_select"
        )
        
        # Delete button
        if st.button("Delete Tag", type="primary"):
            if tag_to_delete:
                tag_id = get_tag_id_by_label(api_keys["VOICEFLOW"], tag_to_delete)
                if tag_id:
                    if delete_tag(api_keys["VOICEFLOW"], tag_id):
                        st.success(f"Tag '{tag_to_delete}' deleted successfully!")
                        # Refresh tag list
                        tags = get_voiceflow_tags(api_keys["VOICEFLOW"])
                        if tags:
                            st.session_state.existing_tags = tags
                            st.rerun()
                    else:
                        st.error("Failed to delete tag.")
                else:
                    st.error("Could not find tag ID.")
            else:
                st.warning("Please select a tag to delete.")

    # Statistics
    st.markdown("---")
    st.markdown(f"📊 **Statistics:** {len(filtered_docs)} documents displayed | {len(st.session_state.existing_tags)} total tags")