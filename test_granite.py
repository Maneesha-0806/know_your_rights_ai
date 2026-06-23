from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "ibm-granite/granite-3.3-2b-instruct"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_id)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype="auto"
)

print("Model loaded successfully!")

prompt = "Explain consumer rights in simple language."

inputs = tokenizer(
    prompt,
    return_tensors="pt"
)

outputs = model.generate(
    **inputs,
    max_new_tokens=100
)

response = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True
)

print("\nResponse:")
print(response)