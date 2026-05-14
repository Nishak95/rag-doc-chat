# 📄 RAG Document Chat

Chat with any PDF using AI. Upload a document and ask questions — 
answers are grounded in the actual content with source citations.

## Features
- Upload any PDF
- Semantic search using embeddings
- Source citations with page numbers
- Conversation memory

## Tech Stack
- LangChain
- ChromaDB
- OpenAI GPT-3.5
- Streamlit

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Add your `OPENAI_API_KEY` in a `.env` file.