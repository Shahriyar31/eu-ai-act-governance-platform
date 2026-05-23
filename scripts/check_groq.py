"""Quick check that Groq is responding and estimate tokens remaining."""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Reply with just: OK"}],
        max_tokens=5
    )
    print("Status:  AVAILABLE")
    print(f"Model:   llama-3.1-8b-instant")
    print(f"Reply:   {response.choices[0].message.content}")
    print(f"Tokens used this call: {response.usage.total_tokens}")
    print("Check full usage at: https://console.groq.com/settings/usage")

except Exception as e:
    if "429" in str(e):
        print("Status:  RATE LIMITED — daily token limit reached")
        print("Resets:  midnight UTC")
        print("Check:   https://console.groq.com/settings/usage")
    else:
        print(f"Status:  ERROR — {e}")
