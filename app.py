import streamlit as st
from utils.chatbot import ask_question

# Page configuration
st.set_page_config(
    page_title="Know Your Rights AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Neomorphism CSS styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #E8DDD3;
}

#MainMenu,
footer,
header {
    visibility: hidden;
}

.block-container {
    max-width: 900px;
    padding: 2rem 0 !important;
    margin: 0 auto !important;
}

.element-container {
    margin-bottom: 0.5rem;
}

.stTextArea {
    margin-bottom: 0;
}

/* Header */

.main-header {
    text-align: center;
    margin-bottom: 1.5rem;
}

.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1A1A1A;
    margin-bottom: 0.5rem;
}

.main-subtitle {
    font-size: 1.1rem;
    color: #6B6B6B;
}

/* Containers */

.neo-container,
.response-container {
    border-radius: 20px;
}

.neo-container {
    background: #E8DDD3;
    padding: 32px;
    margin: 0 auto 2rem;
    box-shadow:
        -8px -8px 16px rgba(255,255,255,.9),
        8px 8px 16px rgba(163,140,115,.4);
}

.response-container {
    padding: 24px;
    margin-top: 24px;
    background: linear-gradient(135deg,#E8DDD3 0%,#EDE3D9 100%);
    box-shadow:
        -6px -6px 12px rgba(255,255,255,.8),
        6px 6px 12px rgba(163,140,115,.3);
    animation: fadeIn .4s ease-in-out;
}

/* Labels */

.section-label,
.response-label {
    text-transform: uppercase;
    letter-spacing: .5px;
}

.section-label {
    font-size: .95rem;
    font-weight: 600;
    color: #4A4A4A;
    margin-bottom: 12px;
}

.response-label {
    font-size: .9rem;
    font-weight: 700;
    color: #8B6F47;
    margin-bottom: 12px;
}

/* Text Area */

.stTextArea textarea {
    background: #E8DDD3 !important;
    border: none !important;
    border-radius: 15px !important;
    padding: 16px !important;
    min-height: 120px !important;
    color: #3E3E3E !important;
    font-size: 1rem !important;
    box-shadow:
        inset 6px 6px 12px rgba(163,140,115,.3),
        inset -6px -6px 12px rgba(255,255,255,.7) !important;
}

.stTextArea textarea:focus {
    outline: 2px solid #B8956A !important;
    outline-offset: -2px !important;
}

.stTextArea textarea::placeholder {
    color: #8A8A8A !important;
}

/* Button */

.stButton button {
    width: 100%;
    margin-top: 16px;
    padding: 14px 40px !important;
    background: #E8DDD3 !important;
    border: none !important;
    border-radius: 15px !important;
    color: #3E3E3E !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    transition: .3s;
    box-shadow:
        -8px -8px 16px rgba(255,255,255,.9),
        8px 8px 16px rgba(163,140,115,.4) !important;
}

.stButton button:hover {
    transform: translateY(-2px);
    color: #B8956A !important;
}

.stButton button:active {
    transform: translateY(0);
    box-shadow:
        inset 4px 4px 8px rgba(163,140,115,.3),
        inset -4px -4px 8px rgba(255,255,255,.7) !important;
}

/* Response Content */

.response-container .stMarkdown,
.response-container .stMarkdown * {
    color: black !important;
}

.response-container .stMarkdown {
    font-size: 1rem;
    line-height: 1.8;
}

.response-container .stMarkdown p,
.response-container .stMarkdown li {
    margin-bottom: .5rem;
}

.response-container .stMarkdown ul,
.response-container .stMarkdown ol {
    margin-left: 1.5rem;
}

.response-container .stMarkdown strong {
    font-weight: 700;
}

.response-container .stMarkdown h1,
.response-container .stMarkdown h2,
.response-container .stMarkdown h3 {
    font-weight: 700;
    margin: 1rem 0 .5rem;
}

.response-container .stMarkdown h1 { font-size: 1.5rem; }
.response-container .stMarkdown h2 { font-size: 1.3rem; }
.response-container .stMarkdown h3 { font-size: 1.1rem; }

.stMarkdown,
.stMarkdown * {
    color: #1A1A1A !important;
}

/* Spinner */

.stSpinner > div {
    border-top-color: #B8956A !important;
}

/* Footer */

.footer-container {
    text-align: center;
    margin-top: 2rem;
    padding: 20px;
    border-radius: 15px;
    background: rgba(184,149,106,.1);
}

.disclaimer-title {
    color: #8B6F47;
    font-weight: 700;
    margin-bottom: 8px;
}

.disclaimer-text {
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.6;
    font-size: .875rem;
    color: #4A4A4A;
}

/* Animation */

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Mobile */

@media (max-width:768px) {
    .main-title { font-size: 2rem; }
    .neo-container { padding: 24px; }
    .response-container { padding: 20px; }
    .stButton button { padding: 12px 24px !important; }
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="main-title">⚖️ Know Your Rights AI</div>
    <div class="main-subtitle">Making legal information accessible through AI</div>
</div>
""", unsafe_allow_html=True)

# Section label
st.markdown('<div class="section-label">Ask Your Legal Rights Question</div>', unsafe_allow_html=True)

# Question input
question = st.text_area(
    label="Question",
    placeholder="Example: What are my rights as an employee under the new labour codes?",
    label_visibility="collapsed",
    key="question_input"
)

# Submit button
if st.button("Get Answer", key="submit_button", use_container_width=True):
    if question.strip():
        with st.spinner("Analyzing your question and generating response..."):
            try:
                answer = ask_question(question)
                
                # Display response in neomorphic container using native Streamlit
                st.markdown('<div class="response-label">Answer</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="response-container">{answer}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a question before submitting.")

st.markdown('</div>', unsafe_allow_html=True)

# Footer with disclaimer
st.markdown("""
<div class="footer-container">
    <div class="disclaimer-title">⚠️ Disclaimer</div>
    <div class="disclaimer-text">
        Know Your Rights AI provides educational and informational content only. 
        It does not provide legal advice or legal representation. 
        Please consult a qualified legal professional for specific legal matters.
    </div>
</div>
""", unsafe_allow_html=True)

# Made with Bob
