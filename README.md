# Voiceflow - KnowledgeFlow

## Project Description

Voiceflow - KnowledgeFlow is a comprehensive tool for processing, managing content, and handling knowledge base tags from various sources. It provides a streamlined workflow for extracting, processing, and utilizing content for Voiceflow projects.

### Key Features

1. **Content Input**
   - File Upload: Support for .txt and .pdf files
   - Website Link: Extract content from URLs
   - Table Upload
   - Knowledge Base Tag Management

2. **API Key Management**
   - Manages keys for FIRECRAWL, OPENAI, VOICEFLOW, and LLAMAPARSE
   - Secure input and storage of API keys

3. **PDF Parsing**
   - Utilizes LlamaParse for efficient PDF content extraction
   - Customizable parsing instructions for tailored results

4. **Web Scraping**
   - Implements Firecrawl for accurate website content extraction

5. **Content Processing**
   - Markdown processing
   - Content cleaning using OpenAI's LLM
   - Automatic summarization

6. **Title Extraction**
   - Intelligent title extraction from processed content
   - Fallback methods ensure a title is always generated

7. **Content Display and Editing**
   - Interactive display of processed content
   - Editable document titles, main content

8. **Table formatting and Upload**
   - Create a tabular table 
   - Add and edit content

9. **Knowledge Base Tag Management**
   - Create and delete KB tags
   - Attach/detach tags to/from documents
   - Easy to use functionality with filtering and search

10. **Download Functionality**
    - Option to download processed content as .txt files
    - Content split into summary and main sections

11. **Voiceflow Upload**
    - Direct upload of processed content to Voiceflow
    - Configurable options for overwriting and chunk size
    - Tag management integration with Voiceflow KB

12. **Error Handling**
    - Robust error management for various scenarios

13. **Session Management and User Interface**
    - Reset app
    - Clean, interactive layout built with Streamlit
    - Intuitive buttons for main actions (process, download, upload)
    - Tag management interface

## How It Works

1. Users can:
   - Input content via file upload or web URL
   - Conversion to Markdown 
   - Summary with Sections, Key Topics, Tags
   - Edit content before upload to VF KB
   - Format and upload tables to KB
   - Manage KB tags
2. The app processes the content using various APIs and algorithms
3. Processed content is displayed for review and editing
4. Users can:
   - Download the processed content
   - Upload directly to Voiceflow
   - Manage document tags

## Technologies Used

- VF Query API
- VF Document API
- VF Tags API
- OpenAI
- LlamaParse
- Firecrawl

## Known Issues:
- Max Chunk is set to 1000 tokens. It is an issue with Voiceflow API. A support ticket is created. 

## Getting Started

Streamlit app link: [Open the Streamlit app](https://voiceflow-knowledgeflow.streamlit.app/)

## Suggestions

Drop me a line at jay.ozer@poppydentaltech.com

