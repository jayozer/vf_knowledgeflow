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
    try:
        # Pass parameters as keyword arguments directly to the scrape_url method
        result = app.scrape_url(url, formats=formats, onlyMainContent=only_main_content)
        
        # The result is an object, so we access its attributes directly.
        # Use getattr for safe access.
        markdown_content = getattr(result, 'markdown', None)
        if markdown_content:
            return markdown_content.strip()
        
        # Fallback to HTML content if markdown is not available
        html_content = getattr(result, 'html', None)
        if html_content:
            return html_content.strip()
            
        return "No content extracted from the URL."

    except Exception as e:
        raise Exception(f"Scraping failed: {e}")
