import tempfile
import os
import re
import pandas as pd
import streamlit as st

from extract4kb import initialize_firecrawl, extract_content
from format4kb import process_markdown, clean_markdown_with_llm, initialize_openai
from summary4kb import summarize_content
from upload2vf import upload_to_voiceflow
from write2file4kb import prepare_download_content, get_download_object
from llama_parse_pdf import parse_pdf
from table_upload import table_upload
from kb_tags import kb_tags_page, get_voiceflow_tags

# Set page config
st.set_page_config(page_title="Voiceflow - KnowledgeFlow")

# Title and instructions
st.title("Voiceflow - KnowledgeFlow")
st.markdown("##### Streamline your content workflow with Voiceflow - KnowledgeFlow. Process diverse inputs, from **PDFs**, **weblinks** to **custom tables**, with advanced features like parsing, auto-summarization, and KB tag management. Edit, download, and organize your content with tags, then upload directly to Voiceflow through an intuitive interface, making content management effortless.")

# Sidebar for configuration
st.sidebar.markdown("# 🔧 CONFIGURATION")
st.sidebar.markdown("---")

# AI Processing Section  
st.sidebar.markdown("### 🤖 AI Processing")
api_keys = {}
missing_keys = []

# OpenAI API Key
openai_key = st.sidebar.text_input(
    "OpenAI API Key:",
    type="password",
    key="openai_api_key",
    help="Enter your OpenAI API Key for content processing.",
    placeholder="❌ API Key not entered"
)
if openai_key:
    api_keys["OPENAI"] = openai_key
    st.sidebar.markdown("✅ **OPENAI API Key entered.**", unsafe_allow_html=True)
else:
    missing_keys.append("OPENAI")

# Model Selection (right after OpenAI key)
selected_model = st.sidebar.selectbox(
    "Model Selection:",
    options=["gpt-4.1", "gpt-4.1-mini", "o3", "o4-mini"],
    index=0,
    help="Choose the AI model for content processing."
)

# Model behavior info
if selected_model.startswith('o'):
    st.sidebar.info("💡 O models don't use temperature parameter")
else:
    st.sidebar.info("💡 GPT models use temperature=0")

st.sidebar.markdown("---")

# Content Extraction Section
st.sidebar.markdown("### 📥 Content Extraction")

# Firecrawl API Key
firecrawl_key = st.sidebar.text_input(
    "Firecrawl API Key:",
    type="password",
    key="firecrawl_api_key",
    help="Enter your Firecrawl API Key for web content extraction.",
    placeholder="❌ API Key not entered"
)
if firecrawl_key:
    api_keys["FIRECRAWL"] = firecrawl_key
    st.sidebar.markdown("✅ **FIRECRAWL API Key entered.**", unsafe_allow_html=True)
else:
    missing_keys.append("FIRECRAWL")

# LlamaCloud API Key
llama_key = st.sidebar.text_input(
    "LlamaCloud API Key:",
    type="password",
    key="llama_cloud_api_key",
    help="Enter your LlamaCloud API Key for PDF parsing.",
    placeholder="❌ API Key not entered"
)
if llama_key:
    api_keys["LLAMA_CLOUD"] = llama_key
    st.sidebar.markdown("✅ **LLAMA_CLOUD API Key entered.**", unsafe_allow_html=True)
else:
    missing_keys.append("LLAMA_CLOUD")

st.sidebar.markdown("---")

# Voiceflow Upload Section
st.sidebar.markdown("### 📤 Voiceflow Upload")

# Voiceflow API Key
voiceflow_key = st.sidebar.text_input(
    "Voiceflow API Key:",
    type="password",
    key="voiceflow_api_key",
    help="Enter your Voiceflow API Key for knowledge base uploads.",
    placeholder="❌ API Key not entered"
)
if voiceflow_key:
    api_keys["VOICEFLOW"] = voiceflow_key
    st.sidebar.markdown("✅ **VOICEFLOW API Key entered.**", unsafe_allow_html=True)
else:
    missing_keys.append("VOICEFLOW")

# Upload settings
overwrite = st.sidebar.radio("Overwrite existing:", ["False", "True"], index=0) == "True"
max_chunk_size = st.sidebar.slider("Max chunk size:", min_value=500, max_value=1500, step=100, value=1000)
st.sidebar.caption(f"📏 {max_chunk_size} tokens per chunk")

st.sidebar.markdown("---")

# Session Management
st.sidebar.markdown("### 🔄 SESSION")
if st.sidebar.button("Reset App", type="secondary"):
    # Clear all session state variables
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Remove uploaded files
    if 'file_uploader' in st.session_state:
        del st.session_state['file_uploader']
    
    # Reset the content input method to default
    st.session_state['input_method'] = "Enter Website URL"
    
    # Clear any stored website URL
    if 'website_link' in st.session_state:
        del st.session_state['website_link']
    
    st.rerun()

# Initialize session state variables
if 'processed_content' not in st.session_state:
    st.session_state.processed_content = None
if 'extracted_title' not in st.session_state:
    st.session_state.extracted_title = "Untitled Document"
if 'upload_status' not in st.session_state:
    st.session_state.upload_status = None
if 'input_method' not in st.session_state:
    st.session_state.input_method = "Upload File"
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0
if 'selected_docs' not in st.session_state:
    st.session_state.selected_docs = []
if 'existing_tags' not in st.session_state:
    st.session_state.existing_tags = []

# Content Input Section
#st.header("📥 Content Input")
st.header("📚 Content & 🏷️ Tag Management")

input_method = st.radio(
    "Select an option:",
    ["Upload File", "Enter Website URL", "Create + Upload Table", "Manage KB Tags"],
    key="input_method"
)

if input_method == "Manage KB Tags":
    if "VOICEFLOW" not in api_keys or not api_keys["VOICEFLOW"]:
        st.error("⚠️ Voiceflow API key is required for tag management. Please enter your Voiceflow API key in the sidebar configuration.")
        # Add helpful instructions
        with st.expander("ℹ️ How to add your Voiceflow API key"):
            st.markdown("""
                1. Look for the '🔑 API Keys' section in the sidebar
                2. Enter your Voiceflow API key in the 'VOICEFLOW API Key' field
                3. Once entered, you'll be able to manage your knowledge base tags
            """)
        st.stop()  # Stop execution here to prevent the KeyError
    
    # Only proceed with tag management if we have the API key
    if input_method != st.session_state.get('previous_input_method'):
        st.session_state.previous_input_method = input_method
        tags = get_voiceflow_tags(api_keys["VOICEFLOW"])
        if tags:
            st.session_state.existing_tags = tags
            st.rerun()

# Then continue with your existing code
if input_method == "Upload File" or input_method == "Enter Website URL":
    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"], key="file_uploader")
        if uploaded_file is not None:
            st.success(f"File '{uploaded_file.name}' uploaded successfully.")
        else:
            st.info("Please upload a .txt or .pdf file.")
        
        # Parsing Instructions for PDF files (only shown for "Upload File" option)
        with st.expander("📄 Parsing Instructions (for PDF files)"):
            target_pages = st.text_input(
                "Target Pages (optional, page numbering starts from page 0):",
                value="",
                help="Page numbering starts from page 0. Add each page number separated by commas (e.g., 1,2,5,10). Leave empty to parse all pages.",
                placeholder="0,1,2,5,10"
            )

            default_parsing_instruction = """The provided document is a PDF that may encompass various types of content such as text, images, headings, subheadings, bullet points, numbered lists, tables, and figures. Reconstruct the information in a clear and organized manner, preserving the original structure and logical flow presented in the document, unless stated otherwise in the 'exception/modification' section below. Maintain all technical terms, definitions, and descriptions as accurately as possible without altering the intended meaning. Avoid adding personal opinions, interpretations, or any additional commentary outside of the provided content.

With the following exception/modification: """

            parsing_instruction = st.text_area("Edit the parsing instructions as needed:", value=default_parsing_instruction, height=250)

    elif input_method == "Enter Website URL":
        website_link = st.text_input("Enter the website URL:", key="website_link")
        if website_link:
            st.success(f"URL '{website_link}' entered.")
        else:
            st.info("Please Enter Website URL.")

    # Content Processing
    st.header("⚙️ Content Processing")

    if st.button("Process Content"):
        if missing_keys:
            st.error(f"Missing API Keys: {', '.join(missing_keys)}")
            st.stop()
        
        with st.spinner("Processing content..."):
            try:
                # Handle content input
                if input_method == "Upload File" and uploaded_file is not None:
                    if uploaded_file.type == "text/plain":
                        content = uploaded_file.getvalue().decode("utf-8")
                    elif uploaded_file.type == "application/pdf":
                        # Save the uploaded file to a temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name

                        # Parse the PDF using the parsing instructions
                        content = parse_pdf(api_keys["LLAMA_CLOUD"], tmp_file_path, parsing_instruction, target_pages)

                        # Remove the temporary file
                        os.unlink(tmp_file_path)
                    else:
                        st.error("Unsupported file type.")
                        st.stop()
                elif input_method == "Enter Website URL" and website_link:
                    firecrawl_app = initialize_firecrawl(api_keys["FIRECRAWL"])
                    content = extract_content(firecrawl_app, website_link)
                else:
                    st.warning("Please provide content input.")
                    st.stop()
                
                # Process the content
                processed_content = process_markdown(content)
                openai_client = initialize_openai(api_keys["OPENAI"])
                final_cleaned_content = clean_markdown_with_llm(openai_client, processed_content, selected_model)
                
                # Generate summary
                summary = summarize_content(api_keys["OPENAI"], final_cleaned_content, selected_model)
                
                # Extract title from summary or processed content
                content_to_search = summary + "\n\n" + final_cleaned_content

                # Use a more robust regex pattern to find the title
                title_match = re.search(r'# Title:\s*(.*?)(?:\n|$)', content_to_search, re.IGNORECASE)
                if title_match:
                    extracted_title = title_match.group(1).strip()
                else:
                    # Fallback: Use the first line or first heading as the title
                    lines = content_to_search.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            extracted_title = line
                            break
                    else:
                        extracted_title = "Untitled Document"

                # Sanitize the extracted title
                extracted_title = re.sub(r'[^\w\-\s]', '', extracted_title)  # Allow spaces temporarily
                extracted_title = extracted_title.replace(' ', '_')
                if not extracted_title:
                    extracted_title = "untitled"

                # Extract summary content
                summary_match = re.search(r'---START_SUMMARY---(.*?)---END_SUMMARY---', content_to_search, re.DOTALL)
                if summary_match:
                    summary = f"---START_SUMMARY---{summary_match.group(1).strip()}---END_SUMMARY---"
                else:
                    summary = "---START_SUMMARY---No summary available.---END_SUMMARY---"

                # Extract main content (everything after ---END_SUMMARY---)
                main_content_match = re.search(r'---END_SUMMARY---\s*(.*)', content_to_search, re.DOTALL)
                if main_content_match:
                    main_content = main_content_match.group(1).strip()
                else:
                    main_content = "No main content available."

                # Combine summary and cleaned content
                final_content_with_summary = f"{summary}\n\n{main_content}"

                # Store the processed content and extracted title in session state
                st.session_state.processed_content = final_content_with_summary
                st.session_state.extracted_title = extracted_title

                st.success("Content processed successfully!")

            except Exception as e:
                st.error(f"Error processing content: {str(e)}")
                st.stop()

    # Display processed content if available
    if st.session_state.processed_content is not None:
        st.header("📝 Processed Content")

        # Editable title
        st.subheader("Document Title")
        st.session_state.edited_title = st.text_input("Edit the document title:", value=st.session_state.extracted_title)
        
        # Content display in tabs
        summary_match = re.search(r'---START_SUMMARY---(.*?)---END_SUMMARY---', st.session_state.processed_content, re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip()
            main_content = st.session_state.processed_content.split("---END_SUMMARY---", 1)[-1].strip()
        else:
            summary = "No summary available."
            main_content = st.session_state.processed_content

        # Initialize session state for edited content if not present
        if 'edited_summary' not in st.session_state:
            st.session_state.edited_summary = summary
        if 'edited_main_content' not in st.session_state:
            st.session_state.edited_main_content = main_content

        tabs = st.tabs(["Summary", "Main Content"])
        
        with tabs[0]:
            st.markdown("### Summary")
            st.session_state.edited_summary = st.text_area("Summary:", value=st.session_state.edited_summary, height=200)
        
        with tabs[1]:
            st.markdown("### Main Content")
            st.session_state.edited_main_content = st.text_area("Content:", value=st.session_state.edited_main_content, height=400)
        
        # Action buttons
        st.header("💾 Upload and Download")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Upload to Voiceflow"):
                if st.session_state.processed_content:
                    try:
                        filename = f"{st.session_state.edited_title}.txt"  # Create a filename
                        # Combine edited summary and main content
                        edited_content = f"---START_SUMMARY---\n{st.session_state.edited_summary}\n---END_SUMMARY---\n\n{st.session_state.edited_main_content}"
                        upload_to_voiceflow(api_keys["VOICEFLOW"], edited_content, filename, overwrite, max_chunk_size)
                        st.success("Successfully uploaded to Voiceflow")
                    except Exception as e:
                        st.error(f"Error uploading to Voiceflow: {str(e)}")
                else:
                    st.warning("No processed content available for upload.")

        with col2:
            # Use edited content for download
            final_document = prepare_download_content(st.session_state.edited_summary, st.session_state.edited_main_content)
            buffer, filename = get_download_object(final_document, f"{st.session_state.edited_title}.txt")
            
            st.download_button(
                label="Download Content",
                data=buffer,
                file_name=filename,
                mime="text/plain"
            )

        if st.session_state.processed_content is None:
            st.info("Please process content to proceed to download or upload.")

elif input_method == "Create + Upload Table":
    table_upload(api_keys, overwrite)

elif input_method == "Manage KB Tags":
    kb_tags_page(api_keys)
