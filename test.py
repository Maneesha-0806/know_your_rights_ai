from utils.chatbot import ask_question

questions = [
    "What are consumer rights?",
    "How do I report cybercrime?",
    "What rights do students have?",
    "Can I get a refund for a defective product?",
    "What should I do if I am scammed online?"
]
for q in questions:
    print("\nQUESTION:", q)
    print(ask_question(q))

