# 📄 RAG Document Chat

An AI-powered web app that lets you chat with any PDF document.
Upload a document, ask questions, and get answers grounded in 
the actual content — with source citations.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.57-red)
![LangChain](https://img.shields.io/badge/LangChain-1.3-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT3.5-orange)

## 🚀 Features
- Upload any PDF document
- Semantic search using OpenAI embeddings
- Answers grounded in document content — no hallucination
- Source citations with page numbers
- Conversation memory within a session

## 🧠 How It Works
1. PDF is split into chunks (500 chars with 50 overlap)
2. Each chunk is converted to a vector embedding via OpenAI
3. Embeddings stored in ChromaDB (local vector database)
4. User question is embedded and matched against chunks
5. Top 3 matching chunks sent to GPT-3.5 as context
6. Answer generated strictly from retrieved content

## 🛠 Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| LLM | OpenAI GPT-3.5-turbo |
| Embeddings | OpenAI Embeddings |
| Vector DB | ChromaDB |
| Framework | LangChain |
| PDF Parsing | PyPDF |

## ⚙️ Run Locally

```bash
# Clone the repo
git clone https://github.com/Nishak95/rag-doc-chat.git
cd rag-doc-chat

# Create virtual environment
python3 -m venv rag-env
source rag-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your API keys
echo "OPENAI_API_KEY=your_key_here" > .env

# Run the app
streamlit run app.py
```

## 📁 Project Structure
```
rag-doc-chat/
├── app.py              # Streamlit UI
├── rag_pipeline.py     # RAG logic (embed, retrieve, answer)
├── requirements.txt    # Dependencies
├── .env                # API key (not committed)
└── .gitignore
```