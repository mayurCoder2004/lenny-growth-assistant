from app.config import settings
from app.llm.factory import get_llm_provider
from app.llm.ollama_provider import OllamaProvider
from app.llm.anthropic_provider import AnthropicProvider

print("Configured provider:", settings.llm_provider)

provider = get_llm_provider()

print("Provider class:", provider.__class__.__name__)

assert isinstance(provider, OllamaProvider)

print("Factory test: PASSED")
