"""
Test script to verify the chatbot properly rejects questions without relevant context.
Tests both in-scope and out-of-scope questions.
"""

from utils.chatbot import ask_question

# Test cases
test_cases = [
    {
        "category": "OUT OF SCOPE - General Knowledge",
        "questions": [
            "What is the weather today?",
            "Who won the cricket match yesterday?",
            "What is the capital of France?",
            "How do I bake a cake?",
        ]
    },
    {
        "category": "OUT OF SCOPE - Unrelated Legal",
        "questions": [
            "What are the traffic rules in California?",
            "How do I file for bankruptcy in the US?",
            "What are the property laws in the UK?",
        ]
    },
    {
        "category": "IN SCOPE - Labour Rights",
        "questions": [
            "What are my rights as an employee under the new labour codes?",
            "What is the minimum wage under labour laws?",
        ]
    },
    {
        "category": "IN SCOPE - Consumer Rights",
        "questions": [
            "What are my rights as a consumer?",
            "How can I file a consumer complaint?",
        ]
    },
    {
        "category": "IN SCOPE - Cyber Laws",
        "questions": [
            "What are the provisions of the DPDP Act 2023?",
            "What are my rights under cyber laws?",
        ]
    },
    {
        "category": "IN SCOPE - Women's Rights",
        "questions": [
            "What are the provisions of POCSO Act?",
            "What are women's rights in India?",
        ]
    }
]

def run_tests():
    """Run all test cases and display results."""
    print("\n" + "="*80)
    print("CONTEXT VALIDATION TEST SUITE")
    print("="*80)
    
    total_tests = 0
    for test_group in test_cases:
        category = test_group["category"]
        questions = test_group["questions"]
        
        print(f"\n{'='*80}")
        print(f"CATEGORY: {category}")
        print(f"{'='*80}")
        
        for i, question in enumerate(questions, 1):
            total_tests += 1
            print(f"\n[Test {total_tests}] Question: {question}")
            print("-" * 80)
            
            try:
                answer = ask_question(question)
                print(f"\n📝 ANSWER:\n{answer}")
                
                # Check if it's a rejection message
                is_rejected = (
                    "couldn't find relevant information" in answer.lower() or
                    "don't contain sufficient information" in answer.lower() or
                    "can only provide information" in answer.lower()
                )
                
                if category.startswith("OUT OF SCOPE"):
                    if is_rejected:
                        print("\n✅ PASS: Correctly rejected out-of-scope question")
                    else:
                        print("\n❌ FAIL: Should have rejected but provided answer")
                else:  # IN SCOPE
                    if not is_rejected:
                        print("\n✅ PASS: Correctly answered in-scope question")
                    else:
                        print("\n⚠️  WARNING: Rejected in-scope question (may need threshold adjustment)")
                
            except Exception as e:
                print(f"\n❌ ERROR: {str(e)}")
            
            print("-" * 80)
    
    print(f"\n{'='*80}")
    print(f"TEST SUITE COMPLETED - {total_tests} tests run")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    print("\n🚀 Starting Context Validation Tests...")
    print("This will test if the chatbot properly rejects questions without relevant context.\n")
    
    run_tests()
    
    print("\n✅ Testing complete!")
    print("\nNOTE: Review the results above to ensure:")
    print("  1. OUT OF SCOPE questions are rejected with fallback messages")
    print("  2. IN SCOPE questions receive proper answers from the documents")
    print("  3. If in-scope questions are rejected, consider lowering MIN_SIMILARITY_THRESHOLD")

# Made with Bob
