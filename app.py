import streamlit as st
from rag_pipeline import process_pdf, ask_question

# Page config
st.set_page_config(
    page_title="RAG Doc Chat",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Chat with your PDF")
st.caption("Upload a PDF and ask questions about it")

# --- Sidebar: File Upload ---
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file:
        with st.spinner("Reading and indexing your PDF..."):
            # Store retriever in session so we don't reprocess on every question
            if "retriever" not in st.session_state or \
               st.session_state.get("file_name") != uploaded_file.name:

                st.session_state.retriever = process_pdf(uploaded_file)
                st.session_state.file_name = uploaded_file.name
                st.session_state.messages = []  # reset chat on new file

        st.success(f"✅ {uploaded_file.name} is ready!")

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 Sources"):
                for i, source in enumerate(msg["sources"]):
                    st.caption(f"Page {source.metadata.get('page', '?') + 1}: {source.page_content[:200]}...")

# Chat input
if question := st.chat_input("Ask something about your PDF..."):

    if "retriever" not in st.session_state:
        st.warning("Please upload a PDF first!")
    else:
        # Show user message
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        # Get answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, sources = ask_question(st.session_state.retriever, question)
            st.write(answer)
            with st.expander("📚 Sources"):
                for source in sources:
                    st.caption(f"Page {source.metadata.get('page', '?') + 1}: {source.page_content[:200]}...")

        # Save to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })