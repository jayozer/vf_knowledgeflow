# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VoiceFlow KnowledgeFlow is a Streamlit-based web application that streamlines content workflow management for Voiceflow projects. It provides a comprehensive pipeline for processing, managing, and uploading content to Voiceflow's knowledge base system.

## Environment Setup

Use UV for Python package management:
```bash
# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## Running the Application

```bash
# Start the Streamlit app
streamlit run app.py
```

## Core Architecture

The application follows a modular functional architecture with these key components:

### Main Entry Point
- `app.py` - Primary Streamlit application that orchestrates the entire workflow

### Processing Pipeline Modules
- `extract4kb.py` - Web content extraction using Firecrawl API
- `format4kb.py` - Content formatting and cleaning with OpenAI (246 lines, core logic)
- `summary4kb.py` - Content summarization functionality
- `llama_parse_pdf.py` - PDF parsing using LlamaParse
- `write2file4kb.py` - File preparation and download utilities

### Integration Modules
- `upload2vf.py` - Voiceflow API integration for document uploads
- `kb_tags.py` - Knowledge base tag management (370 lines, comprehensive CRUD operations)
- `table_upload.py` - Custom table creation and management

### Data Flow
1. **Input Layer**: Handles PDFs, URLs, and custom tables
2. **Processing Layer**: Extract → Clean → Format → Summarize
3. **Integration Layer**: Upload to Voiceflow knowledge base with tag management
4. **UI Layer**: Streamlit interface for user interaction

## API Dependencies

The application requires these API keys (managed via `.env` file):
- `VOICEFLOW_API_KEY` - For knowledge base operations
- `OPENAI_API_KEY` - For content processing and summarization
- `FIRECRAWL_API_KEY` - For web content extraction
- `LLAMA_CLOUD_API_KEY` - For PDF parsing

## Key Technical Details

### Content Processing
- Max chunk size for uploads: 1000 tokens (currently non-adjustable)
- Supports multiple input formats: PDF, web URLs, custom tables
- OpenAI integration for content cleaning and summarization

### Voiceflow Integration
- Full tag management system with CRUD operations
- Document upload with status tracking
- Knowledge base organization and categorization

### File Structure
- Flat modular structure with clear separation of concerns
- Each module handles a specific aspect of the content pipeline
- Comprehensive error handling and API key validation

## Development Notes

- No testing framework currently implemented
- Uses Streamlit Cloud for deployment (live at: https://voiceflow-knowledgeflow.streamlit.app/)
- Environment variables managed through `.env` file (gitignored)
- Consider implementing type hints and testing framework for future development

## Git Commit Guidelines

- Do not mention Claude in git commit messages
- Do not add anything related to Claude contributed or Claude made this to the commit messages