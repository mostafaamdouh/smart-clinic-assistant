import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

def get_llm():
    """
    Loads API keys from a .env file and sets up a Chat LLM with a fallback mechanism.
    The primary LLM is Groq (Mixtral 8x7b), with OpenRouter (Mistral 7b) as a backup.
    """
    load_dotenv()
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

    if not groq_api_key and not openrouter_api_key:
        raise ValueError("No API keys found. Please copy .env.example to .env and fill in your keys.")
    if not groq_api_key:
        print("Warning: GROQ_API_KEY missing, using OpenRouter only.")
    if not openrouter_api_key:
        print("Warning: OPENROUTER_API_KEY missing, using Groq only.")

    groq_llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=groq_api_key
    )

    openrouter_llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        model="mistralai/mistral-7b-instruct",
        openai_api_key=openrouter_api_key
    )

    return groq_llm.with_fallbacks([openrouter_llm])