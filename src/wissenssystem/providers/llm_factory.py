from wissenssystem.interfaces.llm_provider import LLMProvider


def build_llm(provider: str, model: str, **kwargs) -> LLMProvider:
    """Return the right LLMProvider.

    provider: "anthropic" or "ollama"
    kwargs: api_key (anthropic), ollama_url (ollama)
    """
    if provider == "anthropic":
        from wissenssystem.providers.anthropic_provider import AnthropicLLMProvider

        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        return AnthropicLLMProvider(model=model, api_key=api_key)

    from wissenssystem.providers.ollama_provider import OllamaLLMProvider

    return OllamaLLMProvider(model=model, ollama_url=kwargs.get("ollama_url", "http://localhost:11434"))
