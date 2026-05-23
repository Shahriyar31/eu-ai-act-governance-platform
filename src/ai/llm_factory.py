import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.callbacks import BaseCallbackHandler


class ModelLogger(BaseCallbackHandler):

    def __init__(self, prefix):
        self.prefix = prefix

    def on_llm_start(self, serialized, prompts, **kwargs):
        provider = serialized.get("id", ["unknown"])[-1]
        model = (
            serialized.get("kwargs", {}).get("model_name")
            or serialized.get("kwargs", {}).get("model")
            or kwargs.get("invocation_params", {}).get("model")
            or "unknown"
        )
        print(f"{self.prefix} Using {provider} — model: {model}")


def get_rag_llm():
    primary = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )
    fallback_gemini = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2,
    )
    fallback_small = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )
    return primary.with_fallbacks([fallback_gemini, fallback_small])


def get_agent_llm():
    primary = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
    )
    fallback_gemini = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1,
    )
    fallback_small = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
    )
    return primary.with_fallbacks([fallback_gemini, fallback_small])