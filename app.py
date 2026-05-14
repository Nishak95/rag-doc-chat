import streamlit as st
from rag_pipeline import process_pdf, ask_question

# --- Page Config ---
st.set_page_config(
    page_title="RAG Doc Chat",
    page_icon="📄",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    * { font-family: 'Poppins', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        color: #1a1a2e;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-right: none;
    }

    /* Sidebar text */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Sidebar button */
    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: transform 0.2s ease !important;
    }

    [data-testid="stSidebar"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4) !important;
    }

    /* File uploader in sidebar */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(255, 255, 255, 0.4);
        border-radius: 12px;
        padding: 12px;
    }

    /* Expander in sidebar */
    [data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }

    /* Main chat messages */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #e8e8f0;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.08);
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background-color: #ffffff;
        border: 1.5px solid #667eea;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #667eea; border-radius: 3px; }

    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }

    .main-header h1 {
        font-size: 32px;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #ffffff 0%, #f0f0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 15px;
        margin-top: 8px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Header with Gradient ---
st.markdown("""
<div class="main-header">
    <h1>📄 Chat with Your Documents</h1>
    <p>Upload a PDF and get instant answers to your questions</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <h3 style="color:#ffffff; font-weight:600; margin-bottom:12px; display: flex; align-items: center;">
        📁 Upload Document
    </h3>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Max 200MB file size"
    )

    if uploaded_file:
        with st.spinner("🔍 Processing your document..."):
            if "retriever" not in st.session_state or \
               st.session_state.get("file_name") != uploaded_file.name:

                st.session_state.retriever = process_pdf(uploaded_file)
                st.session_state.file_name = uploaded_file.name
                st.session_state.messages = []

        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin-top: 12px;">
            <p style="color: #fff; margin: 0; font-weight: 600;">✅ Document Ready!</p>
            <p style="color: rgba(255,255,255,0.8); margin: 4px 0 0 0; font-size: 12px;">📄 {}</p>
        </div>
        """.format(uploaded_file.name), unsafe_allow_html=True)

    st.divider()

    # Stats
    if "messages" in st.session_state and st.session_state.messages:
        questions = len(st.session_state.messages) // 2
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Questions", questions, delta=None)
        with col2:
            st.metric("Messages", len(st.session_state.messages), delta=None)
        st.divider()

    # How it works
    with st.expander("⚙️ How RAG Works"):
        st.markdown("""
        <div style="color: #fff; font-size: 13px;">
        
        **1. Upload** 📤
        Upload your PDF document
        
        **2. Split** ✂️
        Document split into chunks
        
        **3. Embed** 🔢
        Convert chunks to embeddings
        
        **4. Index** 🗂️
        Store in vector database
        
        **5. Retrieve** 🔍
        Find relevant chunks for query
        
        **6. Answer** 💡
        GPT-3.5 generates response
        </div>
        """, unsafe_allow_html=True)

    st.markdown(" ")

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat cleared!")
        st.rerun()

# --- Main Chat Area ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Empty state
if not st.session_state.messages:
    if "retriever" not in st.session_state:
        st.markdown("""
        <div style="text-align:center; padding: 80px 20px;">
            <div style="font-size:64px; margin-bottom: 16px;">📄</div>
            <h2 style="color:#667eea; margin:0;">Welcome!</h2>
            <p style="color:#888; font-size: 16px; margin-top: 12px;">Upload a PDF from the sidebar to get started</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding: 80px 20px;">
            <div style="font-size:64px; margin-bottom: 16px;">💬</div>
            <h2 style="color:#667eea; margin:0;">Ready to Chat!</h2>
            <p style="color:#888; font-size: 16px; margin-top: 12px;">Ask anything about your document below</p>
        </div>
        """, unsafe_allow_html=True)

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 View Sources"):
                for i, source in enumerate(msg["sources"]):
                    page = source.metadata.get('page', '?')
                    st.markdown(f"""
                    <div style="padding: 10px; background: #f8f9ff; border-left: 3px solid #667eea; border-radius: 4px; margin-bottom: 8px;">
                        <p style="margin: 0; font-weight: 600; color: #667eea; font-size: 12px;">📄 PAGE {page + 1}</p>
                        <p style="margin: 6px 0 0 0; font-size: 13px; color: #555;">{source.page_content[:250]}...</p>
                    </div>
                    """, unsafe_allow_html=True)

# Chat input
if question := st.chat_input("Ask something about your document..."):
    if "retriever" not in st.session_state:
        st.warning("⚠️ Please upload a PDF first!")
    else:
        # User message
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })
        with st.chat_message("user"):
            st.write(question)

        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, sources = ask_question(
                    st.session_state.retriever,
                    question
                )
            st.write(answer)
            with st.expander("📚 View Sources"):
                for i, source in enumerate(sources):
                    page = source.metadata.get('page', '?')
                    st.markdown(f"""
                    <div style="padding: 10px; background: #f8f9ff; border-left: 3px solid #667eea; border-radius: 4px; margin-bottom: 8px;">
                        <p style="margin: 0; font-weight: 600; color: #667eea; font-size: 12px;">📄 PAGE {page + 1}</p>
                        <p style="margin: 6px 0 0 0; font-size: 13px; color: #555;">{source.page_content[:250]}...</p>
                    </div>
                    """, unsafe_allow_html=True)

        # Save to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })