"""
Thin wrapper around the Groq API. Groq is used here because it has a
generous free tier and low latency - swap GROQ_MODEL or this whole module
for another provider without touching the rest of the app.

Free tier setup: create a key at https://console.groq.com - no payment
details required for the free tier at time of writing.
"""

import os
from groq import Groq

GROQ_MODEL = "openai/gpt-oss-20b"  # fast, free-tier model on Groq

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set")
        _client = Groq(api_key=api_key)
    return _client


def generate_answer(question: str, context: str) -> str:
    """Generate an answer to `question` grounded in `context`. Instructs the
    model to say when it doesn't know rather than hallucinate."""
    client = _get_client()

    system_prompt = (
        "You are an assistant for a business ERP system. Answer the user's "
        "question using ONLY the context provided below. If the context "
        "does not contain the answer, say you don't have that information "
        "instead of guessing."
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=400,
    )
    return response.choices[0].message.content
