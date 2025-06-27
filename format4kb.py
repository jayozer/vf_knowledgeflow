import re
from openai import OpenAI
import os
from dotenv import load_dotenv
import sys


def initialize_openai(api_key):
    """
    Initialize the OpenAI client with the provided API key.
    
    Args:
    api_key (str): The API key for OpenAI.
    
    Returns:
    OpenAI: An instance of OpenAI client.
    
    Raises:
    ValueError: If the API key is not provided.
    """
    if not api_key:
        raise ValueError("No API key provided. Please provide a valid OpenAI API key.")
    return OpenAI(api_key=api_key)

def process_markdown(markdown_text):
    """
    Remove images from markdown content and clean up unwanted artifacts.
    
    Args:
    markdown_text (str): The markdown text to process.
    
    Returns:
    str: Processed markdown text.
    """
    # Remove image markdown: ![Alt text](image_url)
    markdown_text = re.sub(r'!\[.*?\]\(.*?\)', '', markdown_text)
    
    # Remove images within links: [![Alt text](image_url)](link)
    markdown_text = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', markdown_text)
    
    # Remove backslashes
    markdown_text = re.sub(r'\\+', '', markdown_text)
    
    # Remove 'keyboard_arrow_down'
    markdown_text = markdown_text.replace('keyboard_arrow_down', '')
    
    # Remove leftover image file extensions like '.webp)', '.svg)', etc.
    markdown_text = re.sub(r'\.\w+\)\.?\w*\)?', '', markdown_text)
    
    # Remove zero-width spaces and other hidden characters
    markdown_text = markdown_text.replace('\u200d', '')  # Zero-width joiner
    markdown_text = markdown_text.replace('\u200b', '')  # Zero-width space
    
    # Remove any remaining HTML tags
    markdown_text = re.sub(r'<[^>]+>', '', markdown_text)
    
    # Convert common HTML entities
    html_entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
    }
    for entity, char in html_entities.items():
        markdown_text = markdown_text.replace(entity, char)
    
    # Normalize whitespace
    markdown_text = re.sub(r'\s+', ' ', markdown_text)
    
    # Remove or replace non-printable characters
    markdown_text = ''.join(char for char in markdown_text if char.isprintable() or char in ['\n', '\t'])
    
    # Standardize line endings
    markdown_text = markdown_text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove empty links
    markdown_text = re.sub(r'\[([^\]]*)\]\(\s*\)', r'\1', markdown_text)
    
    # Ensure proper spacing for headers
    markdown_text = re.sub(r'(#+)(\w)', r'\1 \2', markdown_text)
    
    # Ensure proper spacing for list items
    #markdown_text = re.sub(r'^(-|\*|\+)(\w)', r'\1 \2', markdown_text, flags=re.MULTILINE)  # this line was removing the Tables in markdown. 
    markdown_text = re.sub(r'^[\-\*]\s+', '', markdown_text, flags=re.MULTILINE)

    
    # Remove duplicate headers
    lines = markdown_text.split('\n')
    new_lines = []
    prev_header = None
    for line in lines:
        if line.startswith('#'):
            if line != prev_header:
                new_lines.append(line)
                prev_header = line
        else:
            new_lines.append(line)
    markdown_text = '\n'.join(new_lines)
    
    # Remove extra whitespace at the beginning and end of lines
    markdown_text = '\n'.join(line.strip() for line in markdown_text.splitlines())
    
    # Remove multiple consecutive empty lines
    markdown_text = re.sub(r'\n{2,}', '\n\n', markdown_text)
    
    # Strip leading/trailing whitespace
    markdown_text = markdown_text.strip()
    
    return markdown_text

def get_model_params(model_name):
    """
    Get model parameters based on model type.
    
    Args:
    model_name (str): The name of the model.
    
    Returns:
    dict: Dictionary containing model parameters.
    """
    if model_name.startswith('o'):
        # O models don't support temperature parameter
        return {"model": model_name}
    else:
        # GPT models use temperature=0
        return {"model": model_name, "temperature": 0}

def clean_markdown_with_llm(client, markdown_text, model_name="gpt-4.1"):
    """
    Use OpenAI's GPT model to clean up markdown content.
    the prompt focuses on tasks that aren't already handled by process_markdown function, avoiding unnecessary duplication while still leveraging the AI's capabilities to improve the markdown content. 
    Use gpt-4o model for this task since tasks outlined are relatively straightforward and don't require deep understanding or complex reasoning. Switched from GPT4o-mini to GPT4o because of table preservation. Mini eats up the tables. Also changed return full cleaned markdown content to only cleaned content as it was causing issues with additional markdown text. 
    
    Args:
    client (OpenAI): An instance of OpenAI client.
    markdown_text (str): The markdown text to clean.
    model_name (str): The name of the model to use.
    
    Returns:
    str: Cleaned markdown text.
    """
    prompt = f"""Please clean up the following markdown content. Do NOT summarize or shorten the content in any way. Preserve all original information and text. Only make the following changes:

- Preserve all tables in their original format, including headers and content.
- Remove all hyperlinks, keeping only the visible text (e.g., change `[text](link)` to just `text`).
- Remove any email addresses or phone numbers.
- Remove any URLs or web addresses.
- Remove any social media handles or hashtags.
- Ensure that headings are properly formatted with the correct number of `#` symbols.
- Ensure that list items are properly formatted with consistent indentation.
- Remove any remaining special characters that are not part of standard markdown syntax.
- Ensure that the markdown formatting is consistent and correct, without changing the existing structure.
- Improve overall readability of the content without altering the existing structure or header levels.

Return the full, cleaned content without any additional text or summaries.

Here's the content to clean:

{markdown_text}
"""

    # Get model parameters based on model type
    model_params = get_model_params(model_name)
    
    response = client.chat.completions.create(
        messages=[{'role': 'user', 'content': prompt}],
        **model_params
    )

    cleaned_markdown = response.choices[0].message.content.strip()

    return cleaned_markdown

def format_content(api_key, raw_markdown, model_name="gpt-4.1"):
    """
    Format the raw markdown content using both regex processing and LLM cleaning.
    
    Args:
    api_key (str): The OpenAI API key.
    raw_markdown (str): The raw markdown content to format.
    model_name (str): The name of the model to use.
    
    Returns:
    str: Formatted and cleaned markdown content.
    """
    client = initialize_openai(api_key)
    processed_markdown = process_markdown(raw_markdown)
    final_cleaned_markdown = clean_markdown_with_llm(client, processed_markdown, model_name)
    return final_cleaned_markdown
