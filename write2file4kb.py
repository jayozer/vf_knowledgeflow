import io

def prepare_download_content(summary_section, final_cleaned_markdown):
    """
    Prepare the content for download by combining the summary and cleaned markdown.
    
    Args:
    summary_section (str): The generated summary section.
    final_cleaned_markdown (str): The cleaned markdown content.
    
    Returns:
    str: The prepared content for download.
    """
    # Remove the summary tags if present
    summary_section = summary_section.replace("---START_SUMMARY---", "").replace("---END_SUMMARY---", "").strip()
    
    # Combine summary and cleaned markdown
    final_document = f"{summary_section}\n\n{final_cleaned_markdown}"
    return final_document

def get_download_object(content, filename):
    """
    Create a BytesIO object for file download.
    
    Args:
    content (str): The content to be downloaded.
    filename (str): The name of the file.
    
    Returns:
    tuple: A tuple containing the BytesIO object and the filename.
    """
    # Create a BytesIO object
    buffer = io.BytesIO()
    buffer.write(content.encode('utf-8'))
    buffer.seek(0)
    
    return buffer, filename

# The main execution block is removed as it will be handled in the Streamlit app