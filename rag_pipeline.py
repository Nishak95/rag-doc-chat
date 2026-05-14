from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import tempfile
import os

# Load API key from .env file
load_dotenv()

def process_pdf(uploaded_file):
    """
    Takes an uploaded PDF, splits it into chunks,
    converts to embeddings, stores in ChromaDB.
    Returns a retriever we can query later.
    """

    # Save uploaded file temporarily to disk
    # (LangChain needs a file path, not a file object)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Step 1 — Load the PDF
    loader = PyPDFLoader(tmp_path)
    documents = loader.load()

    # Step 2 — Split into chunks
    # chunk_size = how many characters per chunk
    # chunk_overlap = how many characters shared between chunks (for context continuity)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)

    # Step 3 — Convert chunks to embeddings + store in ChromaDB
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(chunks, embeddings)

    # Clean up temp file
    os.unlink(tmp_path)

    # Step 4 — Return a retriever
    return vectorstore.as_retriever(search_kwargs={"k": 3})


def ask_question(retriever, question):
    """
    Takes a question and the retriever.
    Finds relevant chunks, sends to LLM, returns answer + sources.
    """

    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0  # 0 = factual, no creativity
    )

    # RetrievalQA chains together: retrieve → prompt → LLM → answer
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True  # so we can show citations
    )

    result = qa_chain.invoke({"query": question})

    answer = result["result"]
    sources = result["source_documents"]

    return answer, sources