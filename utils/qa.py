import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_qa_pipeline():
    """
    Initializes the RoBERTa question-answering pipeline and caches it to memory.
    Ensures the model is loaded only once per session.
    """
    return pipeline("question-answering", model="deepset/roberta-base-squad2")

def get_answer(question, context):
    """
    Answers a question based on the provided context using RoBERTa.
    Truncates the context to avoid exceeding the 512 token limit.
    """
    # Load the cached QA pipeline
    qa_pipeline = load_qa_pipeline()

    # Truncate context to approximately 400 words to respect RoBERTa's 512 token limit
    words = context.split()
    truncated_context = " ".join(words[:400])

    # Call the pipeline with the question and context
    result = qa_pipeline(question=question, context=truncated_context)

    # Return both the answer string and the score float
    return result['answer'], result['score']
