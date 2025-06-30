import streamlit as st
import tiktoken
import re
from typing import List, Dict, Tuple, Optional
import anthropic
import nltk
from nltk.tokenize import sent_tokenize
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class ContentProcessor:
    """Enhanced content processing with multiple chunking strategies and contextual embeddings."""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.anthropic_client = None
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        # Token tracking for cost analysis
        self.token_counts = {
            'input': 0,
            'output': 0,
            'cache_read': 0,
            'cache_creation': 0
        }
        self.token_lock = threading.Lock()
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoding.encode(text))
    
    def manual_chunk(self, text: str, max_tokens: int = 1000, overlap_tokens: int = 100) -> List[Dict]:
        """
        Manual chunking with token-based splitting and overlap.
        
        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of overlapping tokens between chunks
        
        Returns:
            List of chunk dictionaries with text and metadata
        """
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                # Create chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'tokens': current_tokens,
                    'start_sentence': current_chunk[0][:50] + '...' if len(current_chunk[0]) > 50 else current_chunk[0],
                    'type': 'manual'
                })
                chunk_id += 1
                
                # Handle overlap
                if overlap_tokens > 0:
                    # Keep last sentences that fit in overlap window
                    overlap_chunk = []
                    overlap_token_count = 0
                    for sent in reversed(current_chunk):
                        sent_tokens = self.count_tokens(sent)
                        if overlap_token_count + sent_tokens <= overlap_tokens:
                            overlap_chunk.insert(0, sent)
                            overlap_token_count += sent_tokens
                        else:
                            break
                    current_chunk = overlap_chunk
                    current_tokens = overlap_token_count
                else:
                    current_chunk = []
                    current_tokens = 0
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'tokens': current_tokens,
                'start_sentence': current_chunk[0][:50] + '...' if len(current_chunk[0]) > 50 else current_chunk[0],
                'type': 'manual'
            })
        
        return chunks
    
    def semantic_chunk(self, text: str, max_tokens: int = 1000, similarity_threshold: float = 0.5) -> List[Dict]:
        """
        Semantic chunking using topic boundaries.
        Uses simple heuristics for topic detection without requiring embeddings.
        
        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk
            similarity_threshold: Not used in simple version
        
        Returns:
            List of chunk dictionaries
        """
        # Split by common section markers
        section_patterns = [
            r'\n#{1,6}\s+.*\n',  # Markdown headers
            r'\n\n',  # Double newlines
            r'\n[A-Z][^.!?]*:\n',  # Section titles
            r'\n\d+\.\s+',  # Numbered lists
        ]
        
        combined_pattern = '|'.join(section_patterns)
        sections = re.split(f'({combined_pattern})', text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_id = 0
        
        for section in sections:
            if not section.strip():
                continue
                
            section_tokens = self.count_tokens(section)
            
            if current_tokens + section_tokens > max_tokens and current_chunk:
                # Create chunk
                chunk_text = ''.join(current_chunk)
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text.strip(),
                    'tokens': current_tokens,
                    'start_sentence': chunk_text[:50] + '...' if len(chunk_text) > 50 else chunk_text,
                    'type': 'semantic'
                })
                chunk_id += 1
                current_chunk = [section]
                current_tokens = section_tokens
            else:
                current_chunk.append(section)
                current_tokens += section_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = ''.join(current_chunk)
            chunks.append({
                'id': chunk_id,
                'text': chunk_text.strip(),
                'tokens': current_tokens,
                'start_sentence': chunk_text[:50] + '...' if len(chunk_text) > 50 else chunk_text,
                'type': 'semantic'
            })
        
        return chunks
    
    def paragraph_chunk(self, text: str, max_tokens: int = 1000) -> List[Dict]:
        """
        Chunk by paragraphs, combining small paragraphs.
        
        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk
        
        Returns:
            List of chunk dictionaries
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_id = 0
        
        for para in paragraphs:
            para_tokens = self.count_tokens(para)
            
            if current_tokens + para_tokens > max_tokens and current_chunk:
                # Create chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'tokens': current_tokens,
                    'start_sentence': current_chunk[0][:50] + '...' if len(current_chunk[0]) > 50 else current_chunk[0],
                    'type': 'paragraph'
                })
                chunk_id += 1
                current_chunk = [para]
                current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'tokens': current_tokens,
                'start_sentence': current_chunk[0][:50] + '...' if len(current_chunk[0]) > 50 else current_chunk[0],
                'type': 'paragraph'
            })
        
        return chunks
    
    def generate_contextual_embedding(self, document_text: str, chunk_text: str) -> Tuple[str, Dict]:
        """
        Generate contextual information for a chunk using Claude Sonnet 3.5.
        Uses prompt caching for efficiency when processing multiple chunks from the same document.
        
        Args:
            document_text: The full document text
            chunk_text: The chunk to contextualize
        
        Returns:
            Tuple of (contextual_text, usage_stats)
        """
        if not self.anthropic_client:
            return "No context available", {}
        
        DOCUMENT_CONTEXT_PROMPT = """<document>
{doc_content}
</document>"""

        CHUNK_CONTEXT_PROMPT = """Here is the chunk we want to situate within the whole document:
<chunk>
{chunk_content}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                temperature=0.0,
                system=[
                    {
                        "type": "text",
                        "text": DOCUMENT_CONTEXT_PROMPT.format(doc_content=document_text),
                        "cache_control": {"type": "ephemeral"}  # Cache the full document
                    }
                ],
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": CHUNK_CONTEXT_PROMPT.format(chunk_content=chunk_text),
                            }
                        ]
                    }
                ],
            )
            
            # Track token usage
            with self.token_lock:
                self.token_counts['input'] += getattr(response.usage, 'input_tokens', 0)
                self.token_counts['output'] += getattr(response.usage, 'output_tokens', 0)
                self.token_counts['cache_read'] += getattr(response.usage, 'cache_read_input_tokens', 0)
                self.token_counts['cache_creation'] += getattr(response.usage, 'cache_creation_input_tokens', 0)
            
            return response.content[0].text, response.usage
            
        except Exception as e:
            st.error(f"Error generating contextual embedding: {e}")
            return "Error generating context", {}
    
    def generate_chunk_metadata(self, chunk_text: str, context: str = "") -> Dict:
        """
        Generate metadata for a chunk using Claude Sonnet 3.5.
        
        Args:
            chunk_text: The chunk text to analyze
            context: Optional contextual information about the chunk
        
        Returns:
            Dictionary with summary, questions, and keywords
        """
        if not self.anthropic_client:
            return {
                'summary': 'No summary available',
                'questions': [],
                'keywords': []
            }
        
        try:
            full_text = f"{chunk_text}\n\nContext: {context}" if context else chunk_text
            
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Analyze this text chunk and provide:
1. A brief summary (2-3 sentences)
2. 2-3 questions this chunk can answer
3. 3-5 key topics/keywords

Text: {full_text[:2000]}...

Format your response as:
SUMMARY: [summary]
QUESTIONS: [question1] | [question2] | [question3]
KEYWORDS: [keyword1] | [keyword2] | [keyword3]"""
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Parse response
            summary = re.search(r'SUMMARY:\s*(.+?)(?=QUESTIONS:|$)', content, re.DOTALL)
            questions = re.search(r'QUESTIONS:\s*(.+?)(?=KEYWORDS:|$)', content, re.DOTALL)
            keywords = re.search(r'KEYWORDS:\s*(.+?)$', content, re.DOTALL)
            
            return {
                'summary': summary.group(1).strip() if summary else 'No summary available',
                'questions': [q.strip() for q in questions.group(1).split('|')] if questions else [],
                'keywords': [k.strip() for k in keywords.group(1).split('|')] if keywords else []
            }
            
        except Exception as e:
            st.error(f"Error generating metadata: {e}")
            return {
                'summary': 'Error generating summary',
                'questions': [],
                'keywords': []
            }
    
    def process_content(self, text: str, strategy: str = 'manual', max_tokens: int = 1000, 
                       overlap_tokens: int = 100, generate_metadata: bool = False,
                       generate_context: bool = False, parallel_threads: int = 1) -> List[Dict]:
        """
        Process content with selected chunking strategy and optional contextual embeddings.
        
        Args:
            text: Text to process
            strategy: Chunking strategy ('manual', 'semantic', 'paragraph')
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Overlap for manual strategy
            generate_metadata: Whether to generate AI metadata for chunks
            generate_context: Whether to generate contextual embeddings
            parallel_threads: Number of threads for parallel processing
        
        Returns:
            List of processed chunks with metadata
        """
        # Select chunking strategy
        if strategy == 'manual':
            chunks = self.manual_chunk(text, max_tokens, overlap_tokens)
        elif strategy == 'semantic':
            chunks = self.semantic_chunk(text, max_tokens)
        elif strategy == 'paragraph':
            chunks = self.paragraph_chunk(text, max_tokens)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Generate contextual embeddings if requested
        if generate_context and self.anthropic_client:
            def process_chunk_context(chunk):
                context_text, usage = self.generate_contextual_embedding(text, chunk['text'])
                chunk['context'] = context_text
                chunk['contextualized_text'] = f"{chunk['text']}\n\nContext: {context_text}"
                return chunk
            
            # Disable parallel processing if using cache to ensure sequential calls
            if generate_context:
                for i, chunk in enumerate(chunks):
                    # Update the first chunk with cache_control
                    if i == 0:
                        # This is a placeholder, as the actual cache control is in generate_contextual_embedding
                        pass
                    chunks[i] = process_chunk_context(chunk)
            elif parallel_threads > 1:
                with ThreadPoolExecutor(max_workers=parallel_threads) as executor:
                    futures = [executor.submit(process_chunk_context, chunk) for chunk in chunks]
                    chunks = [future.result() for future in as_completed(futures)]
            else:
                for chunk in chunks:
                    process_chunk_context(chunk)
        
        # Generate metadata if requested
        if generate_metadata and self.anthropic_client:
            for chunk in chunks:
                context = chunk.get('context', '')
                metadata = self.generate_chunk_metadata(chunk['text'], context)
                chunk.update(metadata)
        
        return chunks
    
    def preview_chunks_dataframe(self, chunks: List[Dict]) -> pd.DataFrame:
        """Convert chunks to a DataFrame for preview."""
        df_data = []
        for chunk in chunks:
            df_data.append({
                'Chunk ID': chunk['id'],
                'Preview': chunk['start_sentence'],
                'Tokens': chunk['tokens'],
                'Type': chunk['type'],
                'Has Context': 'Yes' if chunk.get('context') else 'No',
                'Summary': chunk.get('summary', 'N/A')[:100] + '...' if chunk.get('summary', 'N/A') and len(chunk.get('summary', '')) > 100 else chunk.get('summary', 'N/A')
            })
        return pd.DataFrame(df_data)
    
    def get_token_usage_stats(self) -> Dict:
        """Get token usage statistics for cost analysis."""
        total_tokens = (self.token_counts['input'] + 
                       self.token_counts['cache_read'] + 
                       self.token_counts['cache_creation'])
        
        savings_percentage = 0
        if total_tokens > 0:
            savings_percentage = (self.token_counts['cache_read'] / total_tokens) * 100
        
        return {
            'total_input_tokens': self.token_counts['input'],
            'total_output_tokens': self.token_counts['output'],
            'cache_creation_tokens': self.token_counts['cache_creation'],
            'cache_read_tokens': self.token_counts['cache_read'],
            'total_tokens': total_tokens,
            'cache_savings_percentage': savings_percentage
        }
    
    def reset_token_counts(self):
        """Reset token usage counters."""
        with self.token_lock:
            self.token_counts = {
                'input': 0,
                'output': 0,
                'cache_read': 0,
                'cache_creation': 0
            }