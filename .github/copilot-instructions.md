# AI Coding Agent Instructions for RAG Document Chat

## Project Overview
RAG Document Chat is a Streamlit-based web application that enables users to upload PDF documents and ask questions grounded in their content. The system uses Retrieval-Augmented Generation (RAG) to prevent hallucination by retrieving relevant document sections before generating answers.

### Core Architecture
- **Frontend**: `app.py` — Streamlit UI with session state management for chat history and document processing
- **RAG Pipeline**: `rag_pipeline.py` — Document ingestion, embedding, and retrieval logic
- **Dependencies**: LangChain (orchestration), ChromaDB (vector storage), OpenAI (embeddings + LLM)

## Critical Data Flows

### PDF Processing Pipeline (`process_pdf` in rag_pipeline.py)
1. Save uploaded PDF to temporary file (LangChain's PyPDFLoader requires a file path, not file objects)
2. Load with `PyPDFLoader` → returns documents with metadata (page numbers stored in `.metadata['page']`)
3. Split with `RecursiveCharacterTextSplitter`: 500-char chunks, 50-char overlap (overlap preserves context continuity across chunk boundaries)
4. Generate embeddings via `OpenAIEmbeddings()` and store in ChromaDB (in-memory)
5. Return retriever with `search_kwargs={"k": 3}` (always retrieves top 3 chunks)

### Question-Answering Flow (`ask_question` in rag_pipeline.py)
- Uses `RetrievalQA` chain: retriever → context injection → GPT-3.5-turbo (temperature=0 for factual answers)
- Always returns `{"result": answer, "source_documents": sources}` with metadata preserved
- Sources contain `.page_content` (chunk text) and `.metadata['page']` (0-indexed page number)

### Streamlit Session State
- `st.session_state.retriever` — active ChromaDB retriever for current document
- `st.session_state.file_name` — tracks which PDF is loaded (to reset retriever on new upload)
- `st.session_state.messages` — list of dicts with `{"role": "user"|"assistant", "content": str, "sources": []}` (assistant messages only)

## Development Patterns

### Environment Setup
- Virtual env: `python3 -m venv rag-env && source rag-env/bin/activate`
- Install: `pip install -r requirements.txt`
- `.env` file: Store `OPENAI_API_KEY=...` (loaded via `python-dotenv`)
- Run: `streamlit run app.py`

### LangChain Import Strategy
The codebase uses a hybrid import pattern:
- `langchain_community.*` — third-party integrations (OpenAI, ChromaDB, PyPDF)
- `langchain_classic.*` — deprecated but used here (text splitting, chains)
- Reason: These are pinned versions matching the installed `langchain` and `langchain-community` packages

When adding new features, preserve this pattern to avoid compatibility issues.

### Chat UI State Management
- Empty state UI shows different messaging based on `"retriever" not in st.session_state`
- File uploader validation: compare `uploaded_file.name` with `st.session_state.file_name` to detect file changes
- Source citations: Always wrap in `st.expander("📚 View Sources")` and format as styled divs with page numbers (`page + 1` because metadata is 0-indexed)

## Project-Specific Conventions

### Styling
- All CSS uses inline Streamlit markdown with custom style tags (no separate CSS files)
- Color scheme: Purple gradients (#667eea, #764ba2) with light backgrounds
- Components styled via `[data-testid="st*"]` selectors for consistency

### Error Handling
- No explicit error handling in RAG pipeline (assumes valid API keys and PDFs)
- User-facing validation: check `"retriever" not in st.session_state` before `ask_question()`
- Warning shown if user tries to ask without uploading: `st.warning("⚠️ Please upload a PDF first!")`

### Constants & Configuration
- Chunk size: 500 characters (balance between context and token limits)
- Chunk overlap: 50 characters (prevents context loss at boundaries)
- Top-k retrieval: 3 chunks (balance between relevance and context window)
- Model: GPT-3.5-turbo with temperature=0 (factual, no creativity)

## Integration Points & Dependencies

### External APIs
- **OpenAI API**: Embeddings via `OpenAIEmbeddings()` and LLM via `ChatOpenAI(model_name="gpt-3.5-turbo")`
- Requires: Valid `OPENAI_API_KEY` in environment
- Cost driver: Embedding calls on PDF processing + chat completions

### Vector Database
- **ChromaDB**: Ephemeral (in-memory) storage, reset on app restart or new document
- No persistence layer — retriever is recreated per PDF upload
- Implication: Only one document at a time per session

### Document Processing
- **PyPDF**: Used via LangChain's PyPDFLoader; extracts text + page metadata
- Limitation: No OCR for scanned PDFs
- Metadata preserved: `.metadata['page']` available in source documents

## Common Modification Points

### Adding Conversation Features
- To track multi-document conversations: Store multiple retrievers in `st.session_state` with document IDs
- To add regenerate/feedback: Modify message dict structure to include unique IDs and metadata

### Improving Retrieval Quality
- Adjust `chunk_size` and `chunk_overlap` in `process_pdf()` based on document domain
- Modify `search_kwargs={"k": X}` to retrieve more/fewer chunks
- Add re-ranking: Post-process retriever results before sending to LLM

### Customizing LLM Behavior
- Change `temperature` in `ask_question()`: higher (0.7-0.9) for creative responses
- Add `max_tokens` parameter to control response length
- Inject custom system prompts via LangChain's `PromptTemplate`

## Testing & Debugging
- No automated tests currently in codebase
- Manual testing: Upload a multi-page PDF and verify page numbers in citations match content
- Debug embeddings: Check ChromaDB similarity search results before LLM
- API debugging: Use `langchain_debugging=True` or enable OpenAI request logging via `langchain.debug = True`
