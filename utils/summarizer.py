import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_summarizer():
    """
    Initializes the BART summarization pipeline and caches it to memory.
    Ensures the model is loaded only once per session.
    """
    return pipeline("summarization", model="facebook/bart-large-cnn")

def summarize(document_text, max_length, min_length):
    """
    Summarizes the provided document text using BART.
    - Truncates input to stay within model token limits (~750 words).
    - Returns the generated summary string.
    """
    # Load the cached summarizer pipeline
    summarizer_pipeline = load_summarizer()

    # Truncate input to the first 1024 tokens (approx the first 750 words) to respect BART's context limit
    words = document_text.split()
    truncated_text = " ".join(words[:750])

    # Call the pipeline with the truncated text and the length parameters
    summary_output = summarizer_pipeline(
        truncated_text, 
        max_length=max_length, 
        min_length=min_length, 
        do_sample=False
    )

    # Return only the generated summary string from the pipeline's output dictionary
    return summary_output[0]['summary_text']
