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

def clean_markdown_with_llm(client, markdown_text):
    """
    Use OpenAI's GPT model to clean up markdown content.
    the prompt focuses on tasks that aren't already handled by process_markdown function, avoiding unnecessary duplication while still leveraging the AI's capabilities to improve the markdown content. 
    Use gpt-4o model for this task since tasks outlined are relatively straightforward and don't require deep understanding or complex reasoning. Switched from GPT4o-mini to GPT4o because of table preservation. Mini eats up the tables. Also changed return full cleaned markdown content to only cleaned content as it was causing issues with additional markdown text. 
    
    Args:
    client (OpenAI): An instance of OpenAI client.
    markdown_text (str): The markdown text to clean.
    
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

    response = client.chat.completions.create(
        model='gpt-4o', 
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=16384,
        temperature=0,
    )

    cleaned_markdown = response.choices[0].message.content.strip()

    return cleaned_markdown

def format_content(api_key, raw_markdown):
    """
    Format the raw markdown content using both regex processing and LLM cleaning.
    
    Args:
    api_key (str): The OpenAI API key.
    raw_markdown (str): The raw markdown content to format.
    
    Returns:
    str: Formatted and cleaned markdown content.
    """
    client = initialize_openai(api_key)
    processed_markdown = process_markdown(raw_markdown)
    final_cleaned_markdown = clean_markdown_with_llm(client, processed_markdown)
    return final_cleaned_markdown
    #return processed_markdown # to check the processing markdown function. 

#testing the functions

# if __name__ == "__main__":
#     # Load the API key from an environment variable or .env file
#     load_dotenv()
#     api_key = os.getenv('OPENAI_API_KEY')
    
#     if not api_key:
#         print("Error: OpenAI API key not found. Please set it in an environment variable or .env file.")
#         sys.exit(1)


# markdown_text = """# Chapter 1 Naturopathic case taking

# # Modifying effects on health and vitality

# - Constitutional strength—familial, genetic, congenital
# - Diet—excess and deficiency
# - Exposure to fresh air, clean water, sunlight and nature
# - Lifestyle—work, education, exercise, rest and recreation
# - Injury or disease
# - Toxaemia—external (such as pollution, pesticides and drugs) and internal (such as metabolic by-products and cell waste)
# - Health of organs of detoxification—liver, kidney and lymph
# - Health of organs of elimination—bowel, gallbladder, bladder, respiratory, skin
# - Emotions and relationships
# - Exposure to culture and creativity
# - Philosophy, religion and an ethical life
# - Community, environment and ecology
# - Social, economic and political factors

# interaction. This vital force is capable of interactions with material matter, such as a person’s biochemistry, and these interactions of the vital force are necessary for life to exist. The vital force is non-material and occurs only in living things. It is the guiding force that accounts not only for the maintenance of life but for the development and activities of living organisms such as the progression from seed to plant, or the development of an embryo to a living being.

# The vital force is seen to be different from all the other forces recognised by physics and chemistry. And, most importantly, living organisms are more than just the effects of physics and chemistry. Vitalists agree with the value of biochemistry and physics in physiology but claim that such sciences will never fully comprehend the nature of life. Conversely, vitalism is not the same as a traditional religious view of life. Vitalists do not necessarily attribute the vital force to a creator, a god or a supernatural being, although vitalism can be compatible with such views. This is considered a ‘strong’ interpretation of vitalism. Naturopaths use a ‘moderate’ form of vitalism: vis medicatrix naturae, or the healing power of nature.

# Vis medicatrix naturae defines health as good vitality where the vital force flows energetically through a person’s being, sustaining and replenishing us, whereas ill health is a disturbance of vital energy. While naturopaths agree with modern pathology about the concepts of disease (cellular dysfunction, genetics, accidents, toxins and microbes), naturopathic philosophy further believes that a person’s vital force determines their susceptibility to illness, the amount of treatment necessary, the vigour of treatment and the speed of recovery. Those with poor vitality will succumb more quickly, require more treatment, need gentler treatments and take longer to recover.

# # Vitality and disease

# Vitalistic theory merges with naturopathy in the understanding of how disease progresses (Table 1.1). The acute stages of disease have active, heightened responses to challenges within the body systems. When the vital force is strong it reacts to an acute crisis by mobilising forces within the body to ‘throw off’ the disease. The effect on vitality is usually only temporary as the body reacts with pain, redness, heat and swelling. If this stage is not dealt with appropriately where suppressive medicines are used, the vital force is weakened and acute illnesses begin to become subacute. This is where there is less activity, less pain and less reaction within the body, accompanied by a lingering loss of vitality, mild toxicity and
# ---
# # CLINICAL NATUROPATHY 3E

# # Table 1.1

# |Stage|Acute|Subacute|Chronic|Degenerative|
# |---|---|---|---|---|
# |Symptoms|Pain, heat, redness, swelling, high activity, discharges, sensitivities|Lowered activity, relapsing symptoms|Persistent symptoms, constant discomfort, accumulation of cellular debris|Overwhelmed with toxicity, cellular destruction, physical and mental decay|
# |Toxicity|Toxic discharges|Toxic absorption|Toxic encumbrance|Toxic necrosis|
# |Vitality|Temporarily weak vitality|Variable vitality, ill at ease, feeling ‘not quite right’, sluggish|Poor vitality, malaise, susceptible to other physical or mental distress|Very low vitality, pernicious disruption of life processes at all levels|

# Sluggishness. The patient begins to feel more persistently ‘not quite right’ but nothing will show up on medical tests and, in the absence of disease, the patient will be declared ‘healthy’ in biomedical terms. If the patient continues without addressing their health and lifestyle in a holistic way they can begin to experience chronic diseases where there are long-term, persistent health problems. This is highlighted by weakened vitality, poor immune responses, toxicity and metabolic sluggishness, and the relationships between systems both within and outside the patient become dysfunctional. The final stage of disease is destructive where there is tissue breakdown, cellular dysfunction, low vitality and high toxicity. 21

# In traditional naturopathic theory the above concepts emphasise the connections between lowered vitality and ill health. Traditional naturopathic philosophy also emphasises that the return of vitality through naturopathic treatment will bring about healing. The stages of this healing are succinctly summarised by Dr Constantine Hering, a 19th-century doctor, and these principles of healing are known as Hering’s law of cure. 21,22

# # Hering’s law of cure

# - Healing begins on the inside in the vital organs first, from the most important organs to the least important organs. The outer surfaces are healed last.
# - Healing begins from the middle of the body out to the extremities.
# - Healing begins from the top and goes down the body.
# - Retracing—healing begins on the most recent problems back to the original problems.
# - Healing crisis—as retracing and healing take place the body will re-experience any prior illness where the vital force was inappropriately treated. In re-experiencing the symptoms the patient will awaken their vitality and have an inner sense that the cleansing is ‘doing them good’. A healing crisis is usually of a brief duration.

# # Holism

# Another essential tenet of naturopathy developed from its eclectic history is the importance of a holistic perspective to explore, understand and treat the patient. Holism comes from the Greek word *holos*, meaning whole. 23,24 The concept of holism has a more formal description in general philosophy and has three main beliefs. 25 First, it is important to consider an organism as a whole. The best way to study the behaviour of a complex system is to treat it as a whole and not merely to analyse the structure and"""

# # Run the formatting functions
# formatted_markdown = format_content(api_key, markdown_text)
    
#     # Output the result
# print(formatted_markdown)


