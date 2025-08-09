import tiktoken
from app.core.config import settings

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    # tiktoken model name mapping if required
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))
