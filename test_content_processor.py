import streamlit as st
import pandas as pd
from content_processor import ContentProcessor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Enhanced Content Processor", layout="wide")

st.title("🔬 Enhanced Content Processor")
st.markdown("Test the new chunking strategies with contextual embeddings using Claude Sonnet 3.5")

# Initialize session state
if 'chunks' not in st.session_state:
    st.session_state.chunks = []
if 'processor' not in st.session_state:
    st.session_state.processor = None

# Sidebar for API key and settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    anthropic_key = st.text_input(
        "Anthropic API Key", 
        type="password",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        help="Required for contextual embeddings and metadata generation"
    )
    
    if anthropic_key:
        if not st.session_state.processor:
            st.session_state.processor = ContentProcessor(anthropic_key)
        st.success("✅ API Key configured")
    
    st.divider()
    
    st.subheader("Chunking Settings")
    
    strategy = st.selectbox(
        "Chunking Strategy",
        ["manual", "semantic", "paragraph"],
        help="Choose how to split the content into chunks"
    )
    
    max_tokens = st.slider(
        "Max Tokens per Chunk",
        min_value=100,
        max_value=2000,
        value=1000,
        step=100,
        help="Maximum number of tokens per chunk"
    )
    
    if strategy == "manual":
        overlap_tokens = st.slider(
            "Overlap Tokens",
            min_value=0,
            max_value=200,
            value=100,
            step=20,
            help="Number of overlapping tokens between chunks"
        )
    else:
        overlap_tokens = 0
    
    st.divider()
    
    st.subheader("Enhancement Options")
    
    generate_context = st.checkbox(
        "Generate Contextual Embeddings",
        value=True,
        help="Add context to each chunk using Claude Sonnet 3.5"
    )
    
    generate_metadata = st.checkbox(
        "Generate Chunk Metadata",
        value=True,
        help="Generate summaries, questions, and keywords for each chunk"
    )
    
    if generate_context:
        parallel_threads = st.slider(
            "Parallel Processing Threads",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of threads for parallel context generation"
        )
    else:
        parallel_threads = 1

# Main content area
tab1, tab2, tab3 = st.tabs(["📝 Input", "🔍 Preview Chunks", "📊 Token Usage"])

with tab1:
    st.header("Input Content")
    
    input_method = st.radio("Choose input method:", ["Text Input", "Upload File"])
    
    if input_method == "Text Input":
        content = st.text_area(
            "Paste your content here",
            height=400,
            placeholder="Enter the text you want to process..."
        )
    else:
        uploaded_file = st.file_uploader(
            "Choose a text file",
            type=['txt', 'md'],
            help="Upload a text or markdown file"
        )
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            st.text_area("File content preview:", content[:1000] + "...", height=200, disabled=True)
        else:
            content = ""
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Process Content", type="primary", disabled=not content or not anthropic_key):
            with st.spinner("Processing content..."):
                processor = st.session_state.processor
                processor.reset_token_counts()
                
                chunks = processor.process_content(
                    text=content,
                    strategy=strategy,
                    max_tokens=max_tokens,
                    overlap_tokens=overlap_tokens,
                    generate_metadata=generate_metadata,
                    generate_context=generate_context,
                    parallel_threads=parallel_threads if generate_context else 1
                )
                
                st.session_state.chunks = chunks
                st.success(f"✅ Processed {len(chunks)} chunks!")
                
                # Display token usage if context was generated
                if generate_context:
                    stats = processor.get_token_usage_stats()
                    st.info(f"💰 Cache savings: {stats['cache_savings_percentage']:.1f}% of tokens read from cache (90% discount)")
    
    with col2:
        if st.button("🗑️ Clear Results"):
            st.session_state.chunks = []
            st.rerun()

with tab2:
    st.header("Chunk Preview")
    
    if st.session_state.chunks:
        # Display summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Chunks", len(st.session_state.chunks))
        with col2:
            avg_tokens = sum(c['tokens'] for c in st.session_state.chunks) / len(st.session_state.chunks)
            st.metric("Avg Tokens/Chunk", f"{avg_tokens:.0f}")
        with col3:
            has_context = sum(1 for c in st.session_state.chunks if c.get('context'))
            st.metric("Chunks with Context", has_context)
        with col4:
            has_metadata = sum(1 for c in st.session_state.chunks if c.get('summary'))
            st.metric("Chunks with Metadata", has_metadata)
        
        st.divider()
        
        # Chunk table
        df = st.session_state.processor.preview_chunks_dataframe(st.session_state.chunks)
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        
        # Detailed chunk viewer
        st.subheader("Detailed Chunk View")
        chunk_id = st.selectbox(
            "Select a chunk to view details:",
            range(len(st.session_state.chunks)),
            format_func=lambda x: f"Chunk {x}: {st.session_state.chunks[x]['start_sentence'][:50]}..."
        )
        
        if chunk_id is not None:
            chunk = st.session_state.chunks[chunk_id]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Chunk Text:**")
                st.text_area("Chunk text", chunk['text'], height=300, key=f"text_{chunk_id}", label_visibility="collapsed")
                
                if chunk.get('context'):
                    st.markdown("**Generated Context:**")
                    st.info(chunk['context'])
            
            with col2:
                if chunk.get('summary'):
                    st.markdown("**Summary:**")
                    st.write(chunk['summary'])
                
                if chunk.get('questions'):
                    st.markdown("**Questions this chunk can answer:**")
                    for q in chunk['questions']:
                        st.write(f"• {q}")
                
                if chunk.get('keywords'):
                    st.markdown("**Keywords:**")
                    st.write(", ".join(chunk['keywords']))
                
                st.markdown("**Metadata:**")
                st.json({
                    'chunk_id': chunk['id'],
                    'tokens': chunk['tokens'],
                    'type': chunk['type']
                })
        
        # Export options
        st.divider()
        st.subheader("Export Options")
        
        col1, col2 = st.columns(2)
        with col1:
            # Export as JSON
            import json
            chunks_json = json.dumps(st.session_state.chunks, indent=2)
            st.download_button(
                label="📥 Download Chunks as JSON",
                data=chunks_json,
                file_name="processed_chunks.json",
                mime="application/json"
            )
        
        with col2:
            # Export as text file with contextual embeddings
            if any(c.get('contextualized_text') for c in st.session_state.chunks):
                export_text = "\n\n---CHUNK_SEPARATOR---\n\n".join(
                    c.get('contextualized_text', c['text']) for c in st.session_state.chunks
                )
                st.download_button(
                    label="📥 Download Contextualized Text",
                    data=export_text,
                    file_name="contextualized_chunks.txt",
                    mime="text/plain"
                )
    else:
        st.info("👈 Process some content to see the chunks here")

with tab3:
    st.header("Token Usage Statistics")
    
    if st.session_state.processor and st.session_state.chunks:
        stats = st.session_state.processor.get_token_usage_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Input Tokens", f"{stats['total_input_tokens']:,}")
            st.metric("Cache Creation Tokens", f"{stats['cache_creation_tokens']:,}")
            st.metric("Cache Read Tokens", f"{stats['cache_read_tokens']:,}")
        
        with col2:
            st.metric("Total Output Tokens", f"{stats['total_output_tokens']:,}")
            st.metric("Total Tokens Used", f"{stats['total_tokens']:,}")
            st.metric("Cache Savings", f"{stats['cache_savings_percentage']:.1f}%")
        
        st.divider()
        
        st.info("""
        **💡 Token Usage Explained:**
        - **Cache Creation**: First time document is sent to Claude (slightly more expensive)
        - **Cache Read**: Subsequent chunks from same document (90% discount)
        - **Cache Savings**: Percentage of input tokens that were read from cache
        
        Prompt caching makes contextual embeddings much more cost-effective!
        """)
    else:
        st.info("👈 Process some content with contextual embeddings to see token usage")