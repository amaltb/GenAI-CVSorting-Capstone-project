

from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="gemma3:1b")
response = llm.invoke("Write 2 line professional summary for a data engineer")

print(response)
