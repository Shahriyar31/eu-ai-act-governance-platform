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


def _groq_base_url() -> str:
    account_id = os.getenv("CF_ACCOUNT_ID")
    gateway_name = os.getenv("CF_GATEWAY_NAME")
    if account_id and gateway_name:
        return f"https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_name}/groq"
    return "https://api.groq.com/openai/v1"


def get_rag_llm():
    primary = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=_groq_base_url(),
        temperature=0.2,
    )
    fallbacks = []
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        fallbacks.append(ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_key,
            temperature=0.2,
        ))
    fallbacks.append(ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=_groq_base_url(),
        temperature=0.2,
    ))
    return primary.with_fallbacks(fallbacks)


def get_agent_llm():
    primary = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=_groq_base_url(),
        temperature=0.1,
    )
    fallbacks = []
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        fallbacks.append(ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_key,
            temperature=0.1,
        ))
    fallbacks.append(ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=_groq_base_url(),
        temperature=0.1,
    ))
    return primary.with_fallbacks(fallbacks)