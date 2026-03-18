from langchain_ollama import OllamaLLM


class LLMClient:
    """
    A wrapper around the Ollama LLM backend that provides a simple interface
    for sending prompts and receiving generated text responses. Uses Gemma 3 1B
    as the default model for lightweight, local, privacy-centric inference.
    """

    def __init__(self, model="gemma3:1b", temperature=0):
        self.llm = OllamaLLM(model=model, temperature=temperature)

    def generate(self, prompt: str) -> str:
        """
        Send prompt to the local LLM and return response
        """
        response = self.llm.invoke(prompt)
        return response
