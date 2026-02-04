import streamlit as st
import pandas as pd
from utils.excel_analyzer import ExcelAnalyzer
from utils.rag_engine import RAGEngine
import os
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Cement Expert v2",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Login Credentials from .env
LOGIN_ID = os.getenv("LOGIN_ID", "sampyo")
LOGIN_PW = os.getenv("LOGIN_PASSWORD", "1q2w3e4r")

# Custom CSS for NotebookLM-like Premium UI
st.markdown("""
<style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&display=swap');

    * {
        font-family: 'Pretendard', sans-serif;
    }

    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #f8f9ff 0%, #eef2ff 50%, #e0e7ff 180%);
    }

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Glassmorphism Cards */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 12px !important;
        margin-bottom: 1rem;
        padding: 1.25rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }

    /* User Message Style */
    [data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(235, 245, 255, 0.7) !important;
    }

    /* Header Styling */
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 700;
    }

    /* Login Box */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: flex-start; /* Align to top */
        padding-top: 5vh;        /* Offset from very top */
        height: 80vh;
    }
    
    .login-box {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        padding: 3rem;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 400px;
    }

    /* Chat Input Styling */
    .stChatInputContainer {
        padding-bottom: 1rem !important;
    }
    
    div[data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Login Page function
def login_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 1rem;'>🏗️ Cement Expert AI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>로그인하여 전문가 시스템을 시작하세요</p>", unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            user_id = st.text_input("ID", placeholder="아이디를 입력하세요")
            user_pw = st.text_input("Password", type="password", placeholder="비밀번호를 입력하세요")
            submit = st.form_submit_button("로그인", use_container_width=True)
            
            if submit:
                if user_id == LOGIN_ID and user_pw == LOGIN_PW:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Main Application Logic
def main_app():
    # Initialization
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = ExcelAnalyzer()
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = RAGEngine()
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar Content
    with st.sidebar:
        st.title("🏗️ Sources")
        st.markdown("### 📊 Excel/CSV Analysis")
        uploaded_file = st.file_uploader("Upload process data", type=["xlsx", "xls", "csv"], label_visibility="collapsed")
        
        if uploaded_file:
            success, message = st.session_state.analyzer.load_file(uploaded_file)
            if success:
                st.success("File uploaded successfully!")
                with st.expander("Preview Data"):
                    st.dataframe(st.session_state.analyzer.df.head(10), use_container_width=True)
                
                # Show basic info
                info = st.session_state.analyzer.get_summary()
                st.info(f"Loaded {info['total_rows']} rows across {len(info['columns'])} columns.")
            else:
                st.error(message)
        
        st.divider()
        st.markdown("### 📚 Knowledge Base (RAG)")
        if st.session_state.rag_engine.index:
            st.success("Connected to Pinecone: " + st.session_state.rag_engine.index_name)
        else:
            st.warning("Pinecone Index not found. Running in Excel-only mode.")
        
        st.divider()
        if st.button("Logout", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.rerun()

    # Main Interface (Chat UI)
    st.title("Cement Expert AI v2")
    st.markdown("##### Cement Manufacturing Process & Quality QnA Assistant")

    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask about process or data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data and knowledge base..."):
                # Prepare excel context if available
                excel_context = ""
                if st.session_state.analyzer.df is not None:
                    excel_context = st.session_state.analyzer.get_data_context()
                
                # Get response from RAG Engine
                try:
                    response = st.session_state.rag_engine.generate_response(
                        user_query=prompt,
                        excel_context=excel_context,
                        chat_history=st.session_state.messages[:-1]
                    )
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"응답 생성 중 오류가 발생했습니다: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Route to proper page
if st.session_state.authenticated:
    main_app()
else:
    login_page()
