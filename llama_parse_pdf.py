from llama_parse import LlamaParse

def parse_pdf(api_key, file_path, parsing_instruction=None, target_pages=""):
    default_instruction = """The provided document is a PDF that may encompass various types of content such as text, images, headings, subheadings, bullet points, numbered lists, tables, and figures. Reconstruct the information in a clear and organized manner, preserving the original structure and logical flow presented in the document, unless stated otherwise in the 'exception/modification' section below. Maintain all technical terms, definitions, and descriptions as accurately as possible without altering the intended meaning. Avoid adding personal opinions, interpretations, or any additional commentary outside of the provided content.

With the following exception/modification: """

    instruction = parsing_instruction if parsing_instruction else default_instruction

    parser = LlamaParse(
        api_key=api_key,
        result_type="markdown",
        parsing_instruction=instruction,
        target_pages=target_pages,
        invalidate_cache=True,  # Ensure the cache is invalidated
        do_not_cache=True  # Ensure the cache is not used. LlamaCloud keeps results cached for 48 hrs after upload. 
    )
    
    documents = parser.load_data(file_path)
    return "\n\n".join([doc.text for doc in documents])

