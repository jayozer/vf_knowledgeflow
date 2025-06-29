from firecrawl import FirecrawlApp
import os
from dotenv import load_dotenv

def initialize_firecrawl(api_key):
    """
    Initialize the FirecrawlApp with the provided API key.
    
    Args:
    api_key (str): The API key for FirecrawlApp.
    
    Returns:
    FirecrawlApp: An instance of FirecrawlApp.
    
    Raises:
    ValueError: If the API key is not provided.
    """
    if not api_key:
        raise ValueError("No API key provided. Please provide a valid FIRECRAWL API key.")
    return FirecrawlApp(api_key=api_key)

def extract_content(app, url, formats=["markdown"], only_main_content=True):
    """
    Extract content from the given URL using the provided FirecrawlApp instance.
    
    Args:
    app (FirecrawlApp): An instance of FirecrawlApp.
    url (str): The URL to scrape.
    formats (list): List of formats to extract. Default is ["markdown"].
    only_main_content (bool): Whether to extract only the main content. Default is True.
    
    Returns:
    str: The scraped content from the URL, formatted as markdown.
    
    """
    
    # Pass parameters directly as keyword arguments according to v1 API
    result = app.scrape_url(url, formats=formats, onlyMainContent=only_main_content)
    
    # Extract markdown content from the data object
    data = result.get('data', {})
    markdown_content = data.get('markdown', '')
    
    # If markdown content is not available, try other formats in data
    if not markdown_content:
        # Try HTML content if markdown is not available
        html_content = data.get('html', '')
        if html_content:
            return html_content.strip()
        
        # Fall back to combining available content
        combined_content = ""
        for key, value in data.items():
            if isinstance(value, str) and key not in ['metadata']:
                combined_content += f"## {key.capitalize()}\n\n{value}\n\n"
        
        if combined_content:
            return combined_content.strip()
        else:
            return "No content extracted from the URL."
    
    return markdown_content.strip()
