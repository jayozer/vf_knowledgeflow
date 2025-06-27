from openai import OpenAI

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

def generate_summary(client, final_cleaned_markdown, model_name="gpt-4.1"):
    """
    Generate a summary section for the given markdown document using OpenAI's GPT model.
    
    Args:
    client (OpenAI): An instance of OpenAI client.
    final_cleaned_markdown (str): The cleaned markdown content to summarize.
    model_name (str): The name of the model to use.
    
    Returns:
    str: A summary section including title, sections, and keywords.
    
    Raises:
    Exception: If there's an error in generating the summary.
    """
    prompt = f"""Analyze the following content and generate a structured summary:

{final_cleaned_markdown}

Provide your response in the following markdown format with clear separators:

---START_SUMMARY---
# Title:[Concise title for the content]

## Sections:
- [Section 1]
- [Section 2]
- [Section 3]
- [Section 4]
- [Section 5]


## Key Topics:
- [Topic 1]
- [Topic 2]
- [Topic 3]

## Tags:
[Tag 1], [Tag 2], [Tag 3], [Tag 4], [Tag 5]
---END_SUMMARY---

Ensure all parts are present and properly formatted between the START and END separators.
"""

    try:
        # Get model parameters based on model type
        model_params = get_model_params(model_name)
        
        response = client.chat.completions.create(
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=16384,  # max token output
            **model_params
        )

        summary_section = response.choices[0].message.content.strip()
        return summary_section
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}")

def summarize_content(api_key, markdown_content, model_name="gpt-4.1"):
    """
    Main function to initialize OpenAI client and generate summary.
    
    Args:
    api_key (str): The OpenAI API key.
    markdown_content (str): The markdown content to summarize.
    model_name (str): The name of the model to use.
    
    Returns:
    str: The generated summary section.
    """
    client = initialize_openai(api_key)
    return generate_summary(client, markdown_content, model_name)

