from ollama_client import call_ollama

prompt = "Tell me a cool story"

response = call_ollama(
    prompt, 
    temperature=0.1, 
    top_p=0.7,
    top_k=20,
    num_predict=300
)

print(f"Response: {response}\n")
