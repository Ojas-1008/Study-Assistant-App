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
from utils.qa import get_answer

# Load API keys and config from .env file
load_dotenv()

# Import AI utilities (Cerebras-powered)
from utils.gemini import configure, get_chat_response, generate_quiz, simplify_text

# Configure Cerebras API
configure(os.getenv("CEREBRAS_API_KEY"))

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
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = None # Store generated quiz data
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}     # Store student selections
if "show_explanations" not in st.session_state:
    st.session_state.show_explanations = {} # Track which explanations to show

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

    # 1. Check for an empty document (same guard as the Summarizer tab).
    if not st.session_state.document_text:
        st.warning("⚠️ Please load a document in the Document Loader tab first.")
        st.stop()

    st.subheader("Interactive Q&A")
    st.write("Enter your question below, and the AI will scan the document for the answer.")

    # 2. Add a st.text_input() for the student's question
    user_question = st.text_input(
        "Enter your question:",
        placeholder="Ask a factual question about the document...",
        help="Type a question based on the document content."
    )

    # 3. Add an "Find Answer" button.
    if st.button("🔍 Find Answer", use_container_width=True, type="primary"):
        if not user_question.strip():
            st.error("❌ Please enter a question.")
        else:
            with st.spinner("🧠 Searching the document for an answer..."):
                try:
                    # 4. Call get_answer()
                    answer, score = get_answer(user_question, st.session_state.document_text)

                    # Display result
                    st.divider()
                    st.subheader("💡 Answer Found")
                    
                    # The answer text in a styled card using st.success()
                    st.success(answer)

                    # The confidence score as a percentage using st.progress()
                    score_percentage = round(score * 100)
                    st.write(f"**Confidence Score:** {score_percentage}%")
                    st.progress(score)

                    # 5. Add a conditional warning: if the confidence score is below 0.30 (30%)
                    if score < 0.30:
                        st.warning(f"⚠️ **Note:** The confidence score is low ({score_percentage}%). The answer may not be explicitly present in the loaded document. Consider rephrasing your question or checking the source text directly.")

                except Exception as e:
                    st.error(f"❌ Question Answering failed: {e}")


# ========== TAB 4: AI Chat Tutor ==========
with tab4:
    st.header("💬 AI Chat Tutor")
    st.write("Chat with an AI tutor about your study material. The tutor knows everything in your document!")

    # 1. Check for an empty document
    if not st.session_state.document_text:
        st.warning("⚠️ Please load a document in the Document Loader tab first.")
        st.stop()

    # 5. Clear Chat Button
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.divider()

    # 2. Display existing chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. Chat Input Box
    if prompt := st.chat_input("Ask your study tutor a question..."):
        # 4. Handle student message
        # Display student message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to session state
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Generate AI response
        with st.spinner("🧠 AI tutor is thinking..."):
            try:
                response = get_chat_response(
                    prompt, 
                    st.session_state.document_text, 
                    st.session_state.chat_history
                )
                
                # Display assistant message
                with st.chat_message("assistant"):
                    st.markdown(response)
                
                # Add to session state
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            except Exception as e:
                st.error(f"❌ Chat failed: {e}")


# ========== TAB 5: Quiz Generator ==========
with tab5:
    st.header("🧪 Quiz Generator")
    st.write("Generate a 5-question practice quiz based on your study material.")

    # 1. Check for an empty document
    if not st.session_state.document_text:
        st.warning("⚠️ Please load a document in the Document Loader tab first.")
        st.stop()

    # 2. Add a "Generate Quiz" button
    if st.button("✨ Generate New Quiz", use_container_width=True, type="primary"):
        # 3. Call generate_quiz() wrapped in a spinner
        with st.spinner("🧠 AI is creating your practice quiz..."):
            result = generate_quiz(st.session_state.document_text)
            
            if isinstance(result, list):
                # Store the result in st.session_state.quiz_questions
                st.session_state.quiz_questions = result
                # Reset previous answers when a new quiz is generated
                st.session_state.user_answers = {}
                st.session_state.show_explanations = {}
                st.success("✅ Quiz generated successfully!")
            else:
                # If the function returned an error string
                st.error(result)

    # 4. Display each question if quiz exists
    if st.session_state.quiz_questions:
        st.divider()
        
        # Use a loop with enumerate() to render questions
        for idx, q_data in enumerate(st.session_state.quiz_questions):
            st.markdown(f"### Question {idx + 1}")
            st.write(q_data["question"])
            
            # Prepare radio options as a list of "A: text", "B: text", etc.
            # This makes selecting easier for the user
            option_keys = ["A", "B", "C", "D"]
            options_display = [f"{k}: {q_data['options'][k]}" for k in option_keys]
            
            # Store/retrieve student answer in session state
            # We map index to index for st.radio
            current_choice_idx = st.session_state.user_answers.get(idx, None)
            
            user_choice = st.radio(
                f"Select an answer for Question {idx + 1}:",
                options_display,
                index=current_choice_idx,
                key=f"q_radio_{idx}",
                label_visibility="collapsed"
            )
            
            # Update session state only if a selection is made
            if user_choice is not None:
                st.session_state.user_answers[idx] = options_display.index(user_choice)
            
            # Add a "Check Answer" button for each question
            if st.button(f"🔎 Check Answer {idx + 1}", key=f"btn_{idx}"):
                st.session_state.show_explanations[idx] = True
            
            # When clicked, compare to correct key and show results
            if st.session_state.show_explanations.get(idx):
                selected_letter = option_keys[st.session_state.user_answers[idx]]
                correct_letter = q_data["correct"]
                
                if selected_letter == correct_letter:
                    st.success(f"✅ **Correct!** The answer is {correct_letter}.")
                else:
                    st.error(f"❌ **Incorrect.** You selected {selected_letter}, but the correct answer is {correct_letter}.")
                
                st.info(f"💡 **Explanation:** {q_data['explanation']}")
            
            st.divider()
            
        # 5. Display Score Card if all questions are answered and checked
        if len(st.session_state.show_explanations) == 5:
            st.title("🏆 Quiz Results")
            
            # Calculate total score
            score = 0
            option_keys = ["A", "B", "C", "D"]
            for i, q_data in enumerate(st.session_state.quiz_questions):
                selected_idx = st.session_state.user_answers.get(i)
                if selected_idx is not None:
                    selected_letter = option_keys[selected_idx]
                    if selected_letter == q_data["correct"]:
                        score += 1
            
            # Display Score with metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Final Score", f"{score} / 5")
            
            with col2:
                # Dynamic motivational message
                if score == 5:
                    st.success("🌟 **Excellent! Perfect Score!** You've mastered this material.")
                elif score >= 3:
                    st.info("👍 **Good effort!** You've got a solid handle on the key concepts.")
                else:
                    st.warning("📖 **Keep studying!** Review the document again and try the quiz once more.")
            
            st.divider()
            
        # Optional: Reset Quiz button
        if st.button("🧹 Clear Quiz Results", use_container_width=True):
            st.session_state.quiz_questions = None
            st.session_state.user_answers = {}
            st.session_state.show_explanations = {}
            st.rerun()


# ========== TAB 6: Concept Simplifier ==========
with tab6:
    st.header("🔍 Concept Simplifier")
    st.write("Paste any difficult sentence or paragraph and get it rewritten in simple, clear English.")
    st.info("💡 **Note:** This tool works independently — you don't need to load a document to use it!")

    # 1. Text area for the complex input
    complex_input = st.text_area(
        "Paste your complex text here:",
        placeholder="e.g., 'The mitochondrial matrix is the site of the TCA cycle, a series of chemical reactions used by all aerobic organisms to generate energy...'",
        height=200
    )

    # 2. Simplify button
    if st.button("✨ Simplify This", use_container_width=True, type="primary"):
        if not complex_input.strip():
            st.error("❌ Please paste some text first.")
        else:
            # 3. Call simplify_text() with a spinner
            with st.spinner("🧠 Breaking it down into simple terms..."):
                try:
                    simplified_result = simplify_text(complex_input)
                    
                    st.divider()
                    st.subheader("📝 Comparison")
                    
                    # 4. Side-by-side comparison
                    col_orig, col_simp = st.columns(2)
                    
                    with col_orig:
                        st.markdown("**Original Text:**")
                        st.info(complex_input)
                    
                    with col_simp:
                        st.markdown("**Simplified Version:**")
                        st.success(simplified_result)
                        
                except Exception as e:
                    st.error(f"❌ Simplification failed: {e}")

    st.divider()
    st.markdown("### How it works")
    st.write("- **Plain English:** Replaces academic jargon with everyday words.")
    st.write("- **Short Sentences:** Breaks long, run-on sentences into punchy ones.")
    st.write("- **Preservation:** Keeps the exact same meaning, just makes it easier to read.")