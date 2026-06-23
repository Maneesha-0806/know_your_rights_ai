from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="hf-inference",
    api_key="YOUR_HF_TOKEN"
)

response = client.text_generation(
    "What is consumer protection?",
    model="google/flan-t5-small",
    max_new_tokens=50
)

print(response)