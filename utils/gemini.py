import time
import json
import re
from openai import OpenAI

# Global client for the Cerebras API
client = None

# List of Cerebras models to try in order of preference
CEREBRAS_MODELS = [
    "llama3.1-8b",
    "gpt-oss-120b",
]

def configure(api_key):
    """
    Configures the Cerebras API client with the provided API key.
    """
    global client
    client = OpenAI(
        base_url="https://api.cerebras.ai/v1",
        api_key=api_key,
    )

def get_chat_response(student_message, document_text, chat_history):
    """
    Generates a response from the AI acting as a study tutor via Cerebras.
    """
    global client
    if client is None:
        raise ValueError("Cerebras API client not configured. Please call configure(api_key).")

    system_prompt = (
        f"Document content:\n{document_text}\n\n"
        "You are a helpful study tutor. Your goal is to assist students by answering their questions "
        "BASED ON THE PROVIDED DOCUMENT ABOVE. Explain concepts clearly, break down complex topics, "
        "and provide relevant examples if asked. If the answer is not in the document, "
        "politely inform the student and try to guide them using the available information."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for message in chat_history:
        messages.append({"role": message["role"], "content": message["content"]})
    messages.append({"role": "user", "content": student_message})

    for model_id in CEREBRAS_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "404" in str(e):
                time.sleep(1)
                continue
            raise
    return "All AI models are currently unavailable. Please try again later."

def generate_quiz(document_text):
    """
    Generates a 5-question multiple-choice quiz from the document text.
    Follows instructions from Step 7.1.
    """
    global client
    if client is None:
        return "AI Client not configured. Please check your API key."

    # 1. Build the prompt as described in Step 7.1
    prompt = (
        f"Read the following document text and generate exactly 5 multiple-choice questions "
        f"based on key facts from the document.\n\n"
        f"DOCUMENT TEXT:\n{document_text}\n\n"
        "INSTRUCTIONS:\n"
        "- Generate exactly 5 multiple-choice questions.\n"
        "- Format each question with exactly 4 options labeled A, B, C, and D.\n"
        "- Clearly indicate which option is correct.\n"
        "- Return the output as a structured JSON array where each element has:\n"
        '  - "question" — the question text\n'
        '  - "options" — a dictionary with keys A, B, C, D and their answer text\n'
        '  - "correct" — the letter of the correct answer ("A", "B", "C", or "D")\n'
        '  - "explanation" — a one-sentence explanation of why that answer is correct\n'
        "- Return ONLY the JSON array with no extra text, markdown formatting, or code fences around it."
    )

    # 2. Send it to AI (using a single call, not a chat session)
    try:
        # Try the most efficient model first
        response = client.chat.completions.create(
            model=CEREBRAS_MODELS[0],
            messages=[{"role": "user", "content": prompt}]
        )
        
        raw_output = response.choices[0].message.content.strip()

        # Robustness: Remove markdown code fences if AI ignored the "ONLY JSON" instruction
        if raw_output.startswith("```"):
            raw_output = re.sub(r'^```(?:json)?\s+|\s+```$', '', raw_output, flags=re.MULTILINE)

        # 3. Parse the returned JSON string using json.loads()
        quiz_list = json.loads(raw_output)

        # 4. Return the list of 5 question dictionaries
        return quiz_list

    except (json.JSONDecodeError, Exception) as e:
        # 5. Wrap in try/except — if JSON parse fails, return a friendly error message
        return f"Sorry, I couldn't generate the quiz right now. The AI response was not in the expected format. Error: {str(e)}"

def simplify_text(complex_text):
    """
    Simplifies complex or technical text into plain, everyday English.
    Designed for a high school reading level.
    """
    global client
    if client is None:
        return "AI Client not configured. Please check your API key."

    # Prompt design for the Concept Simplifier
    prompt = (
        "You are an expert at explaining complex topics in simple terms. Your goal is to "
        "rewrite the provided text according to these strict rules:\n"
        "1. Use plain, simple English that a high school student can easily understand.\n"
        "2. Use short sentences and common everyday words.\n"
        "3. Avoid jargon and technical terms. If a technical term is absolutely necessary, "
        "briefly explain it in a simple way.\n"
        "4. Keep the meaning EXACTLY THE SAME — do not add or remove information, only simplify it.\n"
        "5. Maintain a clear and helpful tone.\n\n"
        f"TEXT TO SIMPLIFY:\n{complex_text}\n\n"
        "SIMPLIFIED VERSION:"
    )

    # Single-turn request (no conversation history)
    for model_id in CEREBRAS_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if "429" in str(e) or "404" in str(e):
                time.sleep(1)
                continue
            raise
    
    return "The AI was unable to simplify the text at this time. Please try again later."
