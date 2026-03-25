"""
Smart Study Assistant - Main Entry Point
An AI-powered web application built with Streamlit for document analysis, 
summarization, and interactive tutoring.
"""
import streamlit as st
import os
from dotenv import load_dotenv
# Import custom document extraction utilities from the utils package
from utils.loader import (
    load_from_pdf,
    load_from_paste,
    load_from_txt,
    load_from_wikipedia
)
from utils.summarizer import summarize

# Load API keys and config from .env file
load_dotenv()

# Configure page title, icon, and layout
st.set_page_config(
    page_title="Smart Study Assistant",
    page_icon="📚",
    layout="wide"
)

# Apply custom CSS from the assets folder to enhance UI aesthetics
try:
    with open("assets/style.css") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    # Fail silently if CSS file is missing to ensure app stability
    pass

# Initialize session state to maintain data (documents, chat history) during app reruns
if "document_text" not in st.session_state:
    st.session_state.document_text = None  # Full extracted text from the source
if "doc_source" not in st.session_state:
    st.session_state.doc_source = ""       # Title/source name for display
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []     # List to store interaction logs

# App header
st.title("Smart Study Assistant 📚")
st.subheader("An AI-powered NLP web app to help you study effectively.")


# Clears the currently loaded document from session state
def clear_loaded_document() -> None:
    st.session_state.document_text = None
    st.session_state.doc_source = ""


# Updates session state with new document content and its source identifier
def set_loaded_document(text: str, source: str) -> None:
    st.session_state.document_text = text
    st.session_state.doc_source = source


# Initialize the multi-tab interface for different app functionalities
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

    # Available document source options
    source_options = [
        "📄 Upload PDF",
        "📝 Paste Text",
        "📂 Upload TXT File",
        "🌐 Fetch Wikipedia"
    ]

    # Selection widget to choose content input method
    source_type = st.radio(
        "How would you like to load content?",
        source_options
    )

    st.divider()

    # Variables to store loaded text and any errors
    document_text = None
    error_message = None

    # Display input widget based on selected source
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

    # Process document loading when button is clicked
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
                    # Process text file extraction
                    document_text, error_message = load_from_txt(input_data)

        elif source_type == "🌐 Fetch Wikipedia":
            if not input_data:
                st.error("❌ Please enter a topic name.")
            else:
                with st.spinner(f"🌐 Searching Wikipedia for '{input_data}'..."):
                    # Retrieve content from Wikipedia API
                    document_text, error_message = load_from_wikipedia(input_data)

        # Update session state on success, show error on failure
        if document_text:
            set_loaded_document(document_text, f"{source_type.split()[1:]} - {input_data.name if hasattr(input_data, 'name') else input_data}")
            st.success(f"✅ Document loaded successfully!")
        elif error_message:
            st.error(f"❌ {error_message}")

    # Display document statistics and preview
    st.divider()
    st.subheader("Document Status")

    if st.session_state.document_text:
        # Calculate text statistics for the user's information
        word_count = len(st.session_state.document_text.split())
        reading_time = max(1, round(word_count / 200)) # Simple estimate (200 wpm)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Word Count", f"{word_count:,}")
        with col2:
            st.metric("Est. Reading Time", f"{reading_time} min")

        # Check if text length exceeds model limits (e.g., BART's token limit)
        if word_count > 750:
            st.info(
                f"📌 **Note:** Your document has {word_count} words, which exceeds BART's 750-word token limit. "
                f"The Summarizer will use only the first portion of your text. The full document is still available for QA and Chat features."
            )

        st.success("✅ Document loaded successfully! You can now use other tabs.")

        # Collapsible preview of document content
        with st.expander("👀 Preview (First 500 chars)"):
            st.text_area("Document Preview", st.session_state.document_text[:500] + "...", disabled=True, height=200)
    else:
        st.info("👈 Load a document using the form above to begin.")

    # Button to clear loaded document from session state
    if st.button("🧹 Clear Loaded Document", use_container_width=True):
        clear_loaded_document()
        st.success("Document cleared.")


# ========== TAB 2: Summarizer ==========
with tab2:
    st.header("📝 Summarizer")
    st.write("Generate concise summaries of your loaded document.")

    # 1. Check if document_text is loaded
    if not st.session_state.document_text:
        st.warning("⚠️ Please load a document in the Document Loader tab first.")
        st.stop()

    st.subheader("Summarization Settings")
    st.write("Adjust the length and click the button to condense your study material.")

    # 2. Slider for Summary Length
    summary_len = st.slider(
        "How detailed should the summary be?",
        min_value=50,
        max_value=300,
        value=150,
        step=10,
        help="Higher values provide more detail but take longer to generate."
    )

    # 3. Generate Summary Button
    if st.button("✨ Generate Summary", use_container_width=True, type="primary"):
        # 4. Show loading indicator
        with st.spinner("🧪 Summarizing your document... This may take a moment for large texts."):
            try:
                # Define range for BART (Max should be the slider value)
                max_l = summary_len
                min_l = max(30, max_l // 3)

                # Call the model
                summary = summarize(
                    st.session_state.document_text, 
                    max_length=max_l, 
                    min_length=min_l
                )
                
                # 5. Display result in a styled alert
                st.divider()
                st.subheader("📑 Document Summary")
                st.success(summary)
                
                # 6. Display compression statistics using columns
                original_words = len(st.session_state.document_text.split())
                summary_words = len(summary.split())
                compression = (1 - summary_words / original_words) * 100 if original_words > 0 else 0

                st.divider()
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("Original Length", f"{original_words} words")
                stat_col2.metric("Summary Length", f"{summary_words} words")
                stat_col3.metric("Compression", f"{compression:.1f}%")
                
            except Exception as e:
                st.error(f"❌ Summarization failed: {e}")


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