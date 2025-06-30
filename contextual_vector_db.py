"""
Contextual Vector Database implementation using Google Gemini for embeddings
and Anthropic Claude for context generation.
"""

import os
import json
import numpy as np
import google.generativeai as genai
import anthropic
import cohere
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import streamlit as st
import pickle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ContextualVectorDB:
    """
    Vector database with contextual embeddings for improved retrieval.
    Uses Claude to generate context and Google Gemini for embeddings.
    """
    
    def __init__(self, name: str, gemini_api_key: Optional[str] = None, 
                 anthropic_api_key: Optional[str] = None, cohere_api_key: Optional[str] = None):
        # Initialize API clients
        if gemini_api_key is None:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
        if anthropic_api_key is None:
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if cohere_api_key is None:
            cohere_api_key = os.getenv("COHERE_API_KEY")
        
        # Configure Gemini
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.embedding_model = 'models/embedding-001'  # Gemini embedding model
        else:
            self.embedding_model = None
            
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.cohere_client = cohere.Client(cohere_api_key) if cohere_api_key else None
        
        self.name = name
        self.embeddings = []
        self.metadata = []
        self.query_cache = {}
        self.db_path = f"./data/{name}/contextual_vector_db.pkl"
        
        # Token tracking for cost analysis
        self.token_counts = {
            'input': 0,
            'output': 0,
            'cache_read': 0,
            'cache_creation': 0
        }
        self.token_lock = threading.Lock()
    
    def generate_chunk_context(self, doc_content: str, chunk_content: str) -> Tuple[str, Any]:
        """
        Generate contextual information for a chunk using Claude.
        
        Args:
            doc_content: Full document content
            chunk_content: The chunk to contextualize
            
        Returns:
            Tuple of (context_text, usage_stats)
        """
        if not self.anthropic_client:
            return "", None
        
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
                        "text": DOCUMENT_CONTEXT_PROMPT.format(doc_content=doc_content),
                        "cache_control": {"type": "ephemeral"}  # Cache the document
                    }
                ],
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": CHUNK_CONTEXT_PROMPT.format(chunk_content=chunk_content),
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
            print(f"Error generating context: {e}")
            return "", None
    
    def generate_chunk_metadata(self, chunk_text: str, context: str = "") -> Dict:
        """
        Generate metadata (summary, questions, keywords) for a chunk using Claude.
        
        Args:
            chunk_text: The chunk text to analyze
            context: Optional contextual information
            
        Returns:
            Dictionary with summary, questions, and keywords
        """
        if not self.anthropic_client:
            return {}
        
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
            import re
            summary = re.search(r'SUMMARY:\s*(.+?)(?=QUESTIONS:|$)', content, re.DOTALL)
            questions = re.search(r'QUESTIONS:\s*(.+?)(?=KEYWORDS:|$)', content, re.DOTALL)
            keywords = re.search(r'KEYWORDS:\s*(.+?)$', content, re.DOTALL)
            
            return {
                'summary': summary.group(1).strip() if summary else '',
                'questions': [q.strip() for q in questions.group(1).split('|')] if questions else [],
                'keywords': [k.strip() for k in keywords.group(1).split('|')] if keywords else []
            }
            
        except Exception as e:
            print(f"Error generating metadata: {e}")
            return {}
    
    def embed_texts(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Embed texts using Google Gemini.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for embedding (Gemini has a limit of 100)
            
        Returns:
            List of embedding vectors
        """
        if not self.embedding_model:
            raise ValueError("Gemini API not configured")
        
        embeddings = []
        
        # Process in batches (Gemini has a batch limit)
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Generate embeddings for the batch
            result = genai.embed_content(
                model=self.embedding_model,
                content=batch,
                task_type="retrieval_document"
            )
            
            # Extract embedding vectors
            for embedding in result['embedding']:
                embeddings.append(embedding)
        
        return embeddings
    
    def load_chunks(self, chunks: List[Dict[str, Any]], doc_content: str, 
                    parallel_threads: int = 5, generate_context: bool = True,
                    generate_metadata: bool = False):
        """
        Load chunks into the vector database with contextual embeddings.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and metadata
            doc_content: Full document content for context generation
            parallel_threads: Number of threads for parallel processing
            generate_context: Whether to generate contextual embeddings
            generate_metadata: Whether to generate questions, summary, keywords
        """
        texts_to_embed = []
        metadata = []
        
        if generate_context and self.anthropic_client:
            # Process chunks in parallel to generate context
            def process_chunk(chunk):
                context_text, usage = self.generate_chunk_context(doc_content, chunk['text'])
                
                # Create contextualized text (original + context)
                if context_text:
                    contextualized_text = f"{chunk['text']}\n\nContext: {context_text}"
                else:
                    contextualized_text = chunk['text']
                
                # Generate metadata if requested
                chunk_metadata = {}
                if generate_metadata:
                    chunk_metadata = self.generate_chunk_metadata(chunk['text'], context_text)
                
                return {
                    'text_to_embed': contextualized_text,
                    'metadata': {
                        **chunk,  # Include all original chunk metadata
                        'original_content': chunk['text'],
                        'context': context_text,
                        'contextualized_content': contextualized_text,
                        **chunk_metadata  # Add summary, questions, keywords
                    }
                }
            
            # Process chunks with progress bar
            with st.spinner(f"Generating context for {len(chunks)} chunks..."):
                with ThreadPoolExecutor(max_workers=parallel_threads) as executor:
                    futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
                    
                    progress_bar = st.progress(0)
                    completed = 0
                    
                    for future in as_completed(futures):
                        result = future.result()
                        texts_to_embed.append(result['text_to_embed'])
                        metadata.append(result['metadata'])
                        
                        completed += 1
                        progress_bar.progress(completed / len(chunks))
                    
                    progress_bar.empty()
        else:
            # No context generation - just use original chunks
            for chunk in chunks:
                texts_to_embed.append(chunk['text'])
                metadata.append({
                    **chunk,
                    'original_content': chunk['text'],
                    'context': '',
                    'contextualized_content': chunk['text']
                })
        
        # Generate embeddings
        with st.spinner("Creating embeddings with Voyage AI..."):
            embeddings = self.embed_texts(texts_to_embed)
        
        self.embeddings = embeddings
        self.metadata = metadata
        
        # Save to disk
        self.save_db()
        
        # Display token usage stats
        if generate_context:
            self._display_token_stats(len(chunks))
    
    def search(self, query: str, k: int = 20) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using cosine similarity.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of search results with metadata and similarity scores
        """
        if not self.embeddings:
            raise ValueError("No data loaded in the vector database")
        
        # Check cache first
        if query in self.query_cache:
            query_embedding = self.query_cache[query]
        else:
            # Generate query embedding using Gemini
            result = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query"
            )
            query_embedding = result['embedding']
            self.query_cache[query] = query_embedding
        
        # Calculate similarities
        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[::-1][:k]
        
        # Prepare results
        results = []
        for idx in top_indices:
            results.append({
                "metadata": self.metadata[idx],
                "similarity": float(similarities[idx])
            })
        
        return results
    
    def rerank_results(self, query: str, results: List[Dict[str, Any]], 
                      top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Rerank search results using Cohere.
        
        Args:
            query: Original search query
            results: Search results to rerank
            top_n: Number of results to return after reranking
            
        Returns:
            Reranked results
        """
        if not self.cohere_client:
            return results[:top_n]
        
        # Extract documents for reranking
        documents = [
            result['metadata'].get('contextualized_content', result['metadata']['original_content'])
            for result in results
        ]
        
        # Rerank using Cohere
        try:
            response = self.cohere_client.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=documents,
                top_n=min(top_n, len(documents))
            )
            
            # Reorder results based on reranking
            reranked_results = []
            for item in response.results:
                original_result = results[item.index]
                reranked_results.append({
                    **original_result,
                    "rerank_score": item.relevance_score
                })
            
            return reranked_results
            
        except Exception as e:
            st.error(f"Reranking error: {e}")
            return results[:top_n]
    
    def hybrid_search(self, query: str, k: int = 20, rerank: bool = True) -> List[Dict[str, Any]]:
        """
        Perform hybrid search with optional reranking.
        
        Args:
            query: Search query
            k: Number of results
            rerank: Whether to use Cohere reranking
            
        Returns:
            Search results
        """
        # Get initial results (we fetch more if reranking)
        initial_k = k * 3 if rerank else k
        results = self.search(query, k=initial_k)
        
        # Rerank if requested
        if rerank and self.cohere_client:
            results = self.rerank_results(query, results, top_n=k)
        else:
            results = results[:k]
        
        return results
    
    def save_db(self):
        """Save the vector database to disk."""
        data = {
            "embeddings": self.embeddings,
            "metadata": self.metadata,
            "query_cache": self.query_cache,
            "token_counts": self.token_counts
        }
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "wb") as f:
            pickle.dump(data, f)
    
    def load_db(self):
        """Load the vector database from disk."""
        if not os.path.exists(self.db_path):
            raise ValueError(f"Database file not found: {self.db_path}")
        
        with open(self.db_path, "rb") as f:
            data = pickle.load(f)
        
        self.embeddings = data.get("embeddings", [])
        self.metadata = data.get("metadata", [])
        self.query_cache = data.get("query_cache", {})
        self.token_counts = data.get("token_counts", self.token_counts)
    
    def _display_token_stats(self, num_chunks: int):
        """Display token usage statistics."""
        total_input = self.token_counts['input'] + self.token_counts['cache_read'] + self.token_counts['cache_creation']
        
        if total_input > 0:
            savings_pct = (self.token_counts['cache_read'] / total_input) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Chunks Processed", num_chunks)
            with col2:
                st.metric("Cache Savings", f"{savings_pct:.1f}%")
            with col3:
                st.metric("Tokens from Cache", f"{self.token_counts['cache_read']:,}")
            
            st.info(f"""
            💰 **Token Usage Summary:**
            - Input tokens: {self.token_counts['input']:,}
            - Cache creation: {self.token_counts['cache_creation']:,}
            - Cache read: {self.token_counts['cache_read']:,} (90% discount!)
            - Total output: {self.token_counts['output']:,}
            """)
    
    def get_token_stats(self) -> Dict[str, Any]:
        """Get token usage statistics."""
        total_input = self.token_counts['input'] + self.token_counts['cache_read'] + self.token_counts['cache_creation']
        savings_pct = (self.token_counts['cache_read'] / total_input * 100) if total_input > 0 else 0
        
        return {
            **self.token_counts,
            'total_input': total_input,
            'savings_percentage': savings_pct
        }