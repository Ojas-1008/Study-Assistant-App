import streamlit as st
import os
from dotenv import load_dotenv
from utils.loader import (
    load_from_pdf, 
    load_from_paste, 
    load_from_txt, 
    load_from_wikipedia
)

# Load environment variables from .env file
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Smart Study Assistant",
    page_icon="📚",
    layout="wide"
)

# Load and inject custom CSS
try:
    with open("assets/style.css") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Initialize session state keys once to avoid first-run key errors
if "document_text" not in st.session_state:
    st.session_state.document_text = None
if "doc_source" not in st.session_state:
    st.session_state.doc_source = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Header Section
st.title("Smart Study Assistant 📚")
st.subheader("An AI-powered NLP web app to help you study effectively.")


# Helper functions
def clear_loaded_document() -> None:
    st.session_state.document_text = None
    st.session_state.doc_source = ""


def set_loaded_document(text: str, source: str) -> None:
    st.session_state.document_text = text
    st.session_state.doc_source = source


# Create six feature tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📂 Document Loader",
    "📝 Summarizer",
    "❓ Question Answering",
    "💬 AI Chat Tutor",
    "🧪 Quiz Generator",
    "🔍 Concept Simplifier"
])

# ========== TAB 1: Document Loader ==========
with tab1:
    st.header("📂 Document Loader")
    st.write("Upload or fetch your study material from multiple sources.")
    
    st.subheader("Choose a Source")
    
    source_options = [
        "📄 Upload PDF",
        "📝 Paste Text",
        "📂 Upload TXT File",
        "🌐 Fetch Wikipedia"
    ]
    
    # Use radio button to select input method
    source_type = st.radio(
        "How would you like to load content?",
        source_options
    )
    
    st.divider()
    
    # Show input widget based on selection
    document_text = None
    error_message = None
    
    if source_type == "📄 Upload PDF":
        st.markdown("### 📄 Upload a PDF Document")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Only .pdf files are accepted."
        )
        input_data = uploaded_file
        
    elif source_type == "📝 Paste Text":
        st.markdown("### 📝 Paste Your Text")
        pasted_text = st.text_area(
            "Copy and paste your content here:",
            height=300,
            help="Enter your text below."
        )
        input_data = pasted_text
        
    elif source_type == "📂 Upload TXT File":
        st.markdown("### 📂 Upload a TXT File")
        txt_file = st.file_uploader("Choose a TXT file", type=["txt"])
        input_data = txt_file
        
    elif source_type == "🌐 Fetch Wikipedia":
        st.markdown("### 🌐 Fetch from Wikipedia")
        topic = st.text_input(
            "Enter a topic (e.g., 'Quantum Mechanics', 'Python Programming'):",
            help="Type a Wikipedia topic name."
        )
        input_data = topic
    
    # Load Document button
    if st.button("📥 Load Document", use_container_width=True, type="primary"):
        if source_type == "📄 Upload PDF":
            if input_data is None:
                st.error("❌ Please select a PDF file.")
            else:
                with st.spinner("📖 Extracting text from PDF..."):
                    document_text, error_message = load_from_pdf(input_data)
                    
        elif source_type == "📝 Paste Text":
            if not input_data:
                st.error("❌ Please paste some text.")
            else:
                document_text, error_message = load_from_paste(input_data)
                
        elif source_type == "📂 Upload TXT File":
            if input_data is None:
                st.error("❌ Please select a TXT file.")
            else:
                with st.spinner("📖 Reading TXT file..."):
                    document_text, error_message = load_from_txt(input_data)
                    
        elif source_type == "🌐 Fetch Wikipedia":
            if not input_data:
                st.error("❌ Please enter a topic name.")
            else:
                with st.spinner(f"🌐 Searching Wikipedia for '{input_data}'..."):
                    document_text, error_message = load_from_wikipedia(input_data)
        
        # Handle success or error
        if document_text:
            set_loaded_document(document_text, f"{source_type.split()[1:]} - {input_data.name if hasattr(input_data, 'name') else input_data}")
            st.success(f"✅ Document loaded successfully!")
        elif error_message:
            st.error(f"❌ {error_message}")
    
    # Display document stats
    st.divider()
    st.subheader("Document Status")
    
    if st.session_state.document_text:
        word_count = len(st.session_state.document_text.split())
        reading_time = max(1, round(word_count / 200))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Word Count", f"{word_count:,}")
        with col2:
            st.metric("Est. Reading Time", f"{reading_time} min")
        
        # BART Token Limit Check (Step 3.5)
        if word_count > 750:
            st.info(
                f"📌 **Note:** Your document has {word_count} words, which exceeds BART's 750-word token limit. "
                f"The Summarizer will use only the first portion of your text. The full document is still available for QA and Chat features."
            )
        
        st.success("✅ Document loaded successfully! You can now use other tabs.")
        
        with st.expander("👀 Preview (First 500 chars)"):
            st.text_area("Document Preview", st.session_state.document_text[:500] + "...", disabled=True, height=200)
    else:
        st.info("👈 Load a document using the form above to begin.")
    
    # Clear button in all cases
    if st.button("🧹 Clear Loaded Document", use_container_width=True):
        clear_loaded_document()
        st.success("Document cleared.")


# ========== TAB 2: Summarizer ==========
with tab2:
    st.header("📝 Summarizer")
    st.write("Generate concise summaries of your loaded document.")
    
    if st.session_state.document_text:
        st.info("✅ Document loaded. Coming soon: Summarization features will appear here.")
        # Placeholder for future implementation
        st.write("**Features to be added:**")
        st.write("- Extract key points from the document")
        st.write("- Generate short, medium, and long summaries")
        st.write("- Highlight important concepts")
    else:
        st.warning("⚠️ Please load a document in the Document Loader tab first.")


# ========== TAB 3: Question Answering ==========
with tab3:
    st.header("❓ Question Answering")
    st.write("Ask questions about your loaded document and get instant answers.")
    
    if st.session_state.document_text:
        st.info("✅ Document loaded. Coming soon: QA features will appear here.")
        # Placeholder for future implementation
        st.write("**Features to be added:**")
        st.write("- Ask questions about the document content")
        st.write("- Get answers with relevant excerpts")
        st.write("- Track question history")
    else:
        st.warning("⚠️ Please load a document in the Document Loader tab first.")


# ========== TAB 4: AI Chat Tutor ==========
with tab4:
    st.header("💬 AI Chat Tutor")
    st.write("Chat with an AI tutor about your study material.")
    
    if st.session_state.document_text:
        st.info("✅ Document loaded. Coming soon: Chat features will appear here.")
        # Placeholder for future implementation
        st.write("**Features to be added:**")
        st.write("- Interactive chat with AI tutor")
        st.write("- Explain difficult concepts")
        st.write("- Get personalized learning suggestions")
    else:
        st.warning("⚠️ Please load a document in the Document Loader tab first.")


# ========== TAB 5: Quiz Generator ==========
with tab5:
    st.header("🧪 Quiz Generator")
    st.write("Generate quizzes based on your study material.")
    
    if st.session_state.document_text:
        st.info("✅ Document loaded. Coming soon: Quiz features will appear here.")
        # Placeholder for future implementation
        st.write("**Features to be added:**")
        st.write("- Auto-generate multiple-choice questions")
        st.write("- Create practice quizzes")
        st.write("- Track quiz scores and performance")
    else:
        st.warning("⚠️ Please load a document in the Document Loader tab first.")


# ========== TAB 6: Concept Simplifier ==========
with tab6:
    st.header("🔍 Concept Simplifier")
    st.write("Break down complex concepts into simple explanations.")
    
    if st.session_state.document_text:
        st.info("✅ Document loaded. Coming soon: Concept simplification features will appear here.")
        # Placeholder for future implementation
        st.write("**Features to be added:**")
        st.write("- Identify and simplify complex concepts")
        st.write("- Create visual explanations")
        st.write("- Provide real-world examples")
    else:
        st.warning("⚠️ Please load a document in the Document Loader tab first.")