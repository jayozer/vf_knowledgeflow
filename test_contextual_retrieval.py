import streamlit as st
import os
from dotenv import load_dotenv
from content_processor import ContentProcessor
from contextual_vector_db import ContextualVectorDB
import pandas as pd

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Contextual Retrieval Test", layout="wide")

st.title("🚀 Contextual Retrieval Testing")
st.markdown("Test the complete contextual retrieval pipeline with Claude + Gemini + Cohere")

# Initialize session state
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'chunks' not in st.session_state:
    st.session_state.chunks = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'document_content' not in st.session_state:
    st.session_state.document_content = ""

# Sidebar for API configuration
with st.sidebar:
    st.header("🔑 API Configuration")
    
    # Check for API keys in environment
    anthropic_key = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        help="For Claude context generation"
    )
    
    # Debug: Show if key is loaded from env
    if os.getenv("ANTHROPIC_API_KEY") and not anthropic_key:
        st.warning("API key found in .env but not loaded in the input field")
    
    gemini_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="For embeddings"
    )
    
    cohere_key = st.text_input(
        "Cohere API Key (Optional)",
        type="password",
        value=os.getenv("COHERE_API_KEY", ""),
        help="For reranking results"
    )
    
    # API Status
    st.divider()
    st.subheader("API Status")
    
    col1, col2 = st.columns(2)
    with col1:
        if anthropic_key:
            st.success("✅ Anthropic")
        else:
            st.error("❌ Anthropic")
            
        if gemini_key:
            st.success("✅ Gemini")
        else:
            st.error("❌ Gemini")
    
    with col2:
        if cohere_key:
            st.success("✅ Cohere")
        else:
            st.warning("⚠️ Cohere (Optional)")
    
    if anthropic_key and gemini_key:
        if not st.session_state.processor:
            st.session_state.processor = ContentProcessor(anthropic_key)
        if not st.session_state.vector_db:
            st.session_state.vector_db = ContextualVectorDB(
                "test_db",
                gemini_api_key=gemini_key,
                anthropic_api_key=anthropic_key,
                cohere_api_key=cohere_key
            )

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["1️⃣ Input & Process", "2️⃣ Build Vector DB", "3️⃣ Search & Retrieve", "4️⃣ Results Analysis"])

with tab1:
    st.header("Step 1: Input and Process Content")
    
    st.info("ℹ️ In this step, we only chunk the content. Context and summaries are generated in Step 2 when building the vector database.")
    
    # Input method
    input_method = st.radio("Choose input method:", ["Sample Text", "Custom Text", "Upload File"])
    
    if input_method == "Sample Text":
        content = """# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence (AI) that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. Machine learning focuses on the development of computer programs that can access data and use it to learn for themselves.

## Types of Machine Learning

### Supervised Learning
In supervised learning, the algorithm learns from labeled training data, helping you to predict outcomes for unforeseen data. It requires a known dataset (called the training dataset) that includes input data and response values. From it, the supervised learning algorithm seeks to build a model that can predict the response values for a new dataset.

### Unsupervised Learning
Unsupervised learning is used against data that has no historical labels. The system is not told the "right answer." The algorithm must figure out what is being shown. The goal is to explore the data and find some structure within. This type of learning works well on transactional data.

### Reinforcement Learning
Reinforcement learning is about taking suitable action to maximize reward in a particular situation. It is employed by various software and machines to find the best possible behavior or path it should take in a specific situation. This type of learning differs from supervised learning in that the training data has the answer key with it.

## Applications of Machine Learning

Machine learning is being used in a wide range of applications today. Some of the most common include:

1. **Image Recognition**: Used in facial recognition, object detection, and medical imaging
2. **Natural Language Processing**: Powers chatbots, translation services, and sentiment analysis
3. **Recommendation Systems**: Used by Netflix, Amazon, and Spotify to suggest content
4. **Fraud Detection**: Banks use ML to identify unusual patterns in transactions
5. **Autonomous Vehicles**: Self-driving cars use ML to navigate and make decisions"""
        
        st.text_area("Sample content:", content, height=200, disabled=True)
    
    elif input_method == "Custom Text":
        content = st.text_area(
            "Enter your content:",
            height=300,
            placeholder="Paste your document here..."
        )
    
    else:  # Upload File
        uploaded_file = st.file_uploader("Choose a file", type=['txt', 'md'])
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            st.text_area("File preview:", content[:500] + "...", height=150)
        else:
            content = ""
    
    # Chunking settings
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        strategy = st.selectbox(
            "Chunking Strategy",
            ["semantic", "manual", "paragraph"],
            help="How to split the content"
        )
    
    with col2:
        max_tokens = st.number_input(
            "Max Tokens per Chunk",
            min_value=100,
            max_value=1500,
            value=500,
            step=100
        )
    
    with col3:
        if strategy == "manual":
            overlap = st.number_input("Overlap Tokens", 0, 200, 50)
        else:
            overlap = 0
    
    # Process button
    if st.button("🔄 Process Content into Chunks", type="primary", 
                 disabled=not content or not st.session_state.processor):
        with st.spinner("Processing content..."):
            # Reset token counts
            st.session_state.processor.reset_token_counts()
            
            # Process content
            chunks = st.session_state.processor.process_content(
                text=content,
                strategy=strategy,
                max_tokens=max_tokens,
                overlap_tokens=overlap,
                generate_metadata=False,  # We'll generate context in next step
                generate_context=False    # Context generated in vector DB
            )
            
            st.session_state.chunks = chunks
            st.session_state.document_content = content  # Store for Step 2
            st.success(f"✅ Created {len(chunks)} chunks!")
            
            # Show chunk preview
            df = st.session_state.processor.preview_chunks_dataframe(chunks)
            st.dataframe(df, use_container_width=True)

with tab2:
    st.header("Step 2: Build Contextual Vector Database")
    
    if not st.session_state.chunks:
        st.info("👈 First, process some content in Step 1")
    else:
        st.write(f"Ready to process {len(st.session_state.chunks)} chunks")
        
        col1, col2 = st.columns(2)
        with col1:
            generate_context = st.checkbox(
                "Generate Contextual Embeddings",
                value=True,
                help="Add context to each chunk using Claude"
            )
            
            generate_metadata = st.checkbox(
                "Generate Questions & Summaries",
                value=True,
                help="Generate questions, summaries, and keywords for each chunk"
            )
        
        with col2:
            if generate_context:
                threads = st.slider("Parallel Threads", 1, 10, 5)
            else:
                threads = 1
        
        if st.button("🏗️ Build Vector Database", type="primary"):
            # Get the full document content from session state
            full_content = st.session_state.document_content
            
            # Load chunks into vector database
            st.session_state.vector_db.load_chunks(
                chunks=st.session_state.chunks,
                doc_content=full_content,
                parallel_threads=threads,
                generate_context=generate_context,
                generate_metadata=generate_metadata
            )
            
            st.success("✅ Vector database built successfully!")
            
            # Show token usage stats
            if generate_context:
                stats = st.session_state.vector_db.get_token_stats()
                st.metric("Cache Savings", f"{stats['savings_percentage']:.1f}%")

with tab3:
    st.header("Step 3: Search and Retrieve")
    
    if not st.session_state.vector_db or not st.session_state.vector_db.embeddings:
        st.info("👈 First, build the vector database in Step 2")
    else:
        # Search interface
        query = st.text_input(
            "Enter your search query:",
            placeholder="e.g., 'How does supervised learning work?'"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            num_results = st.slider("Number of results", 1, 20, 5)
        with col2:
            use_rerank = st.checkbox(
                "Use Cohere Reranking",
                value=bool(st.session_state.vector_db.cohere_client)
            )
        with col3:
            search_method = st.radio("Search Method", ["Hybrid", "Semantic Only"])
        
        if st.button("🔍 Search", type="primary", disabled=not query):
            with st.spinner("Searching..."):
                if search_method == "Hybrid" and use_rerank:
                    results = st.session_state.vector_db.hybrid_search(
                        query=query,
                        k=num_results,
                        rerank=True
                    )
                else:
                    results = st.session_state.vector_db.search(
                        query=query,
                        k=num_results
                    )
                    if use_rerank and st.session_state.vector_db.cohere_client:
                        results = st.session_state.vector_db.rerank_results(
                            query=query,
                            results=results,
                            top_n=num_results
                        )
                
                st.session_state.search_results = results
                st.success(f"Found {len(results)} results!")

with tab4:
    st.header("Step 4: Results Analysis")
    
    if not st.session_state.search_results:
        st.info("👈 First, perform a search in Step 3")
    else:
        results = st.session_state.search_results
        
        # Results summary
        st.subheader(f"Top {len(results)} Results")
        
        for i, result in enumerate(results):
            with st.expander(f"Result {i+1} - Score: {result.get('similarity', result.get('rerank_score', 0)):.3f}"):
                metadata = result['metadata']
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**Original Chunk:**")
                    st.text_area("Chunk content", metadata['original_content'], height=150, key=f"orig_{i}", label_visibility="collapsed")
                    
                    if metadata.get('context'):
                        st.markdown("**Generated Context:**")
                        st.info(metadata['context'])
                
                with col2:
                    if metadata.get('summary'):
                        st.markdown("**Summary:**")
                        st.write(metadata['summary'])
                    
                    if metadata.get('questions'):
                        st.markdown("**Questions this chunk can answer:**")
                        for q in metadata['questions']:
                            st.write(f"• {q}")
                    
                    if metadata.get('keywords'):
                        st.markdown("**Keywords:**")
                        st.write(", ".join(metadata['keywords']))
                    
                    st.markdown("**Scores:**")
                    st.json({
                        'similarity_score': f"{result.get('similarity', 0):.3f}",
                        'rerank_score': f"{result.get('rerank_score', 0):.3f}" if 'rerank_score' in result else "N/A"
                    })
        
        # Export results
        st.divider()
        if st.button("📥 Export Results as JSON"):
            import json
            results_json = json.dumps(results, indent=2)
            st.download_button(
                "Download Results",
                results_json,
                "search_results.json",
                "application/json"
            )

# Footer with instructions
st.divider()
st.markdown("""
### 📖 How to Test Contextual Retrieval:

1. **Step 1**: Input your content and chunk it using different strategies
2. **Step 2**: Build a vector database with contextual embeddings (uses Claude + Gemini)
3. **Step 3**: Search the database with natural language queries
4. **Step 4**: Analyze results to see how context improves retrieval

### 🔑 Required API Keys:
- **Anthropic**: For generating contextual descriptions
- **Google Gemini**: For creating embeddings
- **Cohere** (Optional): For reranking results

### 💡 Tips:
- Try different chunking strategies to see their impact
- Compare results with and without contextual embeddings
- Use Cohere reranking for better precision
""")

# Display current token usage
if st.session_state.vector_db and hasattr(st.session_state.vector_db, 'token_counts'):
    if st.session_state.vector_db.token_counts.get('input', 0) > 0:
        with st.sidebar:
            st.divider()
            st.subheader("💰 Token Usage")
            stats = st.session_state.vector_db.get_token_stats()
            st.metric("Total Tokens", f"{stats['total_input']:,}")
            st.metric("From Cache", f"{stats['cache_read_tokens']:,}")
            st.metric("Savings", f"{stats['savings_percentage']:.1f}%")