import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
from utils.vector_store import get_context, get_context_with_scores
from utils.prompt_loader import load_prompt

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

@st.cache_resource
def load_model():
    """
    Load Qwen2.5-1.5B-Instruct with 8-bit quantization for 4GB VRAM GPUs.
    Qwen2.5 offers excellent quality with fast inference.
    """
    # Detect available device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    
    # Load model with optimizations based on device
    if device == "cuda":
        # GPU: Use 8-bit quantization to fit in 4GB VRAM
        print("🔧 Loading Qwen2.5-1.5B-Instruct with 8-bit quantization...")
        
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0,
            llm_int8_has_fp16_weight=False
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            quantization_config=quantization_config,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        print(f"✓ Qwen2.5-1.5B loaded on GPU with 8-bit quantization")
        print(f"✓ Model size: ~1.5B parameters (~1.5GB VRAM in 8-bit)")
        print(f"✓ Expected response time: 3-5 seconds")
    else:
        # CPU: Load normally
        model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
        model = model.to(device)
        print(f"✓ Qwen2.5-1.5B loaded on CPU")
    
    return tokenizer, model, device

tokenizer, model, device = load_model()

# Configuration for context validation
# With new similarity formula: 1/(1+distance)
# distance=0 → similarity=1.0 (perfect match)
# distance=0.5 → similarity=0.67
# distance=1.0 → similarity=0.5
# distance=2.0 → similarity=0.33
MIN_SIMILARITY_THRESHOLD = 0.5  # Minimum similarity score (corresponds to distance ~1.0)
N_RESULTS = 3  # Number of document chunks to retrieve

# Fallback messages for different rejection scenarios
FALLBACK_MESSAGES = {
    "low_similarity": (
        "I couldn't find relevant information in the available legal documents to answer your question. "
        "I can only provide information about Indian legal rights and regulations covered in my knowledge base, "
        "including:\n"
        "• Labour Codes and Employment Rights\n"
        "• Consumer Rights and Protection\n"
        "• Cyber Laws and Digital Rights\n"
        "• Women's Rights and POCSO Act\n"
        "• Data Protection (DPDP Act)\n"
        "• Telecommunication and Online Gaming Regulations\n"
        "• Student Rights and UGC Guidelines\n\n"
        "Please ask a question related to these topics."
    ),
    "context_not_relevant": (
        "The available documents don't contain sufficient information to answer this specific question. "
        "While your question may be related to legal matters, I can only provide accurate answers based on "
        "the documents in my knowledge base. Please try rephrasing your question or ask about a different topic "
        "covered in the documents listed above."
    )
}

def validate_context_relevance(question, context):
    """
    Step 1: Use LLM to validate if the retrieved context is relevant to the question.
    Returns True if context can answer the question, False otherwise.
    """
    # Create validation prompt
    validation_messages = [
        {
            "role": "system",
            "content": (
                "You are a relevance validator. Determine if the provided context "
                "contains information to answer the question. Answer ONLY with YES or NO."
            )
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}\n\nCan this context answer the question? (YES/NO):"
        }
    ]
    
    # Apply chat template
    validation_prompt = tokenizer.apply_chat_template(
        validation_messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # Tokenize
    inputs = tokenizer(
        validation_prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048
    )
    
    # Move to device
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # Generate validation response (very short)
    outputs = model.generate(
        **inputs,
        max_new_tokens=10,  # Just need YES or NO
        do_sample=False,
        num_beams=1,
        pad_token_id=tokenizer.eos_token_id
    )
    
    # Decode response
    input_length = inputs["input_ids"].shape[1]
    generated_tokens = outputs[0][input_length:]
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip().upper()
    
    # Check if response contains YES
    is_relevant = "YES" in response
    
    print(f"🔍 Relevance validation: {response} -> {'RELEVANT' if is_relevant else 'NOT RELEVANT'}")
    
    return is_relevant

def ask_question(question):
    """
    Generate answer to legal rights question using RAG approach with two-step validation.
    
    Step 1: Check similarity scores - reject if all scores < MIN_SIMILARITY_THRESHOLD
    Step 2: Validate context relevance using LLM - reject if context can't answer question
    Step 3: Generate answer only if both validations pass
    """
    print(f"\n{'='*60}")
    print(f"📥 Question: {question}")
    print(f"{'='*60}")
    
    # Retrieve relevant context with similarity scores
    print(f"🔍 Retrieving top {N_RESULTS} documents from vector store...")
    context_data = get_context_with_scores(question, n_results=N_RESULTS)
    
    documents = context_data["documents"]
    similarities = context_data["similarities"]
    distances = context_data["distances"]
    context = context_data["context"]
    
    # Log retrieved documents and scores
    print(f"\n📊 Retrieved Documents:")
    for i, (doc, sim, dist) in enumerate(zip(documents, similarities, distances), 1):
        preview = doc[:100].replace('\n', ' ') + "..." if len(doc) > 100 else doc
        print(f"  {i}. Similarity: {sim:.3f} (distance: {dist:.3f}) | Preview: {preview}")
    
    # VALIDATION STEP 1: Check similarity scores
    max_similarity = max(similarities) if similarities else 0.0
    print(f"\n🎯 Max similarity score: {max_similarity:.3f} (threshold: {MIN_SIMILARITY_THRESHOLD})")
    print(f"   Formula: similarity = 1/(1+distance), where lower distance = higher similarity")
    
    if max_similarity < MIN_SIMILARITY_THRESHOLD:
        print(f"❌ REJECTED: All similarity scores below threshold")
        print(f"{'='*60}\n")
        return FALLBACK_MESSAGES["low_similarity"]
    
    print(f"✓ Similarity check passed")
    
    # Truncate context if too long
    max_context_length = 1500  # characters
    if len(context) > max_context_length:
        context = context[:max_context_length] + "..."
        print(f"⚠ Context truncated to {max_context_length} characters")
    
    # VALIDATION STEP 2: Check context relevance using LLM
    print(f"\n🤖 Validating context relevance...")
    is_relevant = validate_context_relevance(question, context)
    
    if not is_relevant:
        print(f"❌ REJECTED: Context not relevant to question")
        print(f"{'='*60}\n")
        return FALLBACK_MESSAGES["context_not_relevant"]
    
    print(f"✓ Relevance check passed")
    
    # STEP 3: Generate answer (both validations passed)
    print(f"\n✅ All validations passed - generating answer...")
    
    # Format as chat messages for Qwen2.5 with enhanced system prompt
    messages = [
        {
            "role": "system",
            "content": (
                "You are Know Your Rights AI, a legal awareness assistant. "
                "CRITICAL RULES:\n"
                "1. Answer ONLY using information from the provided context\n"
                "2. Do NOT use your general knowledge or training data\n"
                "3. If the context doesn't fully answer the question, clearly state what's missing\n"
                "4. Use simple, clear language and keep responses concise\n"
                "5. Cite specific parts of the context when possible\n"
                "6. If the question is about a specific law or regulation, reference it by name\n"
                "7. If the context is incomplete or unclear, explicitly state what's missing\n"
                "8. Never invent facts or make up information\n"
                "9. If the question is ambiguous, ask for clarification\n"
                "10. Always prioritize the most recent information in the context\n"
                "11. Answer to the entire question and not just parts of it"
            )
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}\n\nProvide a clear and concise answer based ONLY on the context above:"
        }
    ]
    
    # Apply Qwen2.5 chat template
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    print(f"📝 Prompt length: {len(prompt)} characters")
    
    # Tokenize with truncation
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048
    )
    
    print(f"🔢 Input tokens: {inputs['input_ids'].shape[1]}")

    # Move inputs to model device
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    # Generate with optimized parameters
    print("🚀 Generating response...")
    outputs = model.generate(
        **inputs,
        max_new_tokens=150,     # Output length
        do_sample=False,        # Greedy decoding (faster)
        num_beams=1,            # No beam search (faster)
        pad_token_id=tokenizer.eos_token_id
    )
    
    # Decode only the generated tokens (exclude input prompt)
    input_length = inputs["input_ids"].shape[1]
    generated_tokens = outputs[0][input_length:]
    answer = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )
    
    print(f"✅ Generated {len(generated_tokens)} tokens")
    print(f"{'='*60}\n")

    return answer.strip()