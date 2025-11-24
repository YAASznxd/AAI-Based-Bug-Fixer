css = """
<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">

<style>
:root{
  --bg: #0b0f1a;
  --card-bg: rgba(255,255,255,0.03);
  --glass-bg: rgba(255,255,255,0.05);
  --accent: linear-gradient(90deg, #7c3aed, #06b6d4);
  --text-light: #e6eef8;
  --text-muted: rgba(255,255,255,0.6);
  --success: #10b981;
  --danger: #ef4444;
  --shadow: 0 12px 36px rgba(0,0,0,0.5);
  --radius: 16px;
  --transition: 0.25s cubic-bezier(.4,0,.2,1);
}

/* Global Page */
html, body, .main {
  background: var(--bg) !important;
  font-family: 'Inter', sans-serif;
  color: var(--text-light);
}

/* Main container */
.block-container {
  max-width: 1050px;
  margin: 24px auto;
  padding: 28px 36px !important;
  background: transparent !important;
}

/* Input fields - smaller */
.stTextInput > div, .stTextArea > div {
  border-radius: 10px !important;
  background: rgba(255,255,255,0.02) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  padding: 4px 8px !important;
  font-size: 13px !important;
  min-height: 28px !important;
}
.stTextInput input, .stTextArea textarea {
  background: transparent !important;
  color: var(--text-light) !important;
  font-weight:500 !important;
  font-size: 13px !important;
  padding: 2px 4px !important;
}

/* Chat button smaller */
.stButton>button {
  border-radius:12px !important;
  padding:6px 12px !important;
  font-weight:600 !important;
  font-size:13px !important;
}
.stButton>button:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 50px rgba(0,0,0,0.7) !important;
}

/* Input fields */
.stTextInput > div, .stTextArea > div {
  border-radius:12px !important;
  background: rgba(255,255,255,0.02) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  padding: 8px 12px !important;
}
.stTextInput input, .stTextArea textarea {
  background: transparent !important;
  color: var(--text-light) !important;
  font-weight:500 !important;
}

/* Meta and badges */
.app-meta {
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-top:14px;
  font-size:13px;
  color: var(--text-muted);
}
.badge {
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:6px 12px;
  border-radius:999px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.05);
  font-size:12px;
  color: var(--text-muted);
}

/* Responsive */
@media(max-width:720px){
  .block-container { padding:18px 16px !important; }
  .app-card { padding:16px; border-radius:12px; }
  .chat-bubble { max-width: 94%; }
}
</style>
"""
import streamlit as st
import dspy
import time

# Inject custom CSS
st.markdown(css, unsafe_allow_html=True)

# Helper function for chat bubbles
def render_bubble(text, role="assistant"):
    cls = "assistant" if role=="assistant" else "user"
    html = f'<div class="chat-bubble {cls}">{text}</div>'
    st.markdown(html, unsafe_allow_html=True)

# ======================
# 1) API KEY
# ======================
KEY = "AIzaSyBLhKLueCxnS-0P8-BK8eAG1xVO15rHo2o"

# ======================
# 2) Modular prompt components
# ======================
BASE_INSTRUCTION = """
You are an AI-based bug-fixing assistant. 
Your job is to analyse code, identify bugs, explain the problem clearly, 
and propose corrected code. 
Keep answers accurate, structured, and helpful for developers.
"""

MODULE_ANALYSIS = """
[MODULE: BUG ANALYSIS]
- Identify syntax errors
- Identify logical errors
- Identify performance bottlenecks
- Identify missing dependencies
"""

MODULE_FIXING = """
[MODULE: BUG FIXING]
For each bug:
1. Explain cause of the bug  
2. Provide corrected version of code  
3. Explain why fix works  
"""

MODULE_OPTIMIZATION = """
[MODULE: PROMPT OPTIMIZATION]
Generate the final answer using:
- Minimal wording
- Clear structure
- Developer-friendly formatting
- Bullet points for explanations
"""

def build_prompt(user_code):
    return f"{BASE_INSTRUCTION}\n{MODULE_ANALYSIS}\n{MODULE_FIXING}\n{MODULE_OPTIMIZATION}\n[USER CODE]\n{user_code}"

# ======================
# 3) DSPy Signature
# ======================
class BugFixer(dspy.Signature):
    code_input: str = dspy.InputField(desc="Code provided by user that may have bugs.")
    fixed_output: str = dspy.OutputField(desc="The optimized bug-analysis and bug-fix response.")

# ======================
# Streamlit UI
# ======================
st.set_page_config(page_title="AI Bug Fixer (DSPy)", page_icon="🛠️")
st.title("AI Bug Fixer Prototype")
st.write("Paste buggy code, and the AI will analyze + fix it using modular prompts. ")

# Configure DSPy predictor
if "predictor" not in st.session_state:
    try:
        lm = dspy.LM("gemini/gemini-2.0-flash", api_key=KEY)
        dspy.configure(lm=lm)
        st.session_state.predictor = dspy.Predict(BugFixer)
    except Exception as e:
        st.error(f"Setup error: {e}")
        st.stop()

predict = st.session_state.predictor

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome! Paste any buggy code and I'll fix it."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_code = st.chat_input("Paste your buggy code here...")

if user_code:
    st.session_state.messages.append({"role": "user", "content": user_code})
    with st.chat_message("user"):
        st.markdown(user_code)

    with st.chat_message("assistant"):
        try:
            optimized_prompt = build_prompt(user_code)
            start = time.time()
            out = predict(code_input=optimized_prompt)
            end = time.time()
            bot_response = out.fixed_output if hasattr(out, "fixed_output") else str(out)
            bot_response += f"\n\n⏱️ **Response Time:** {round(end - start,2)} sec"
        except Exception as e:
            bot_response = f"Error: {e}"

        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Clear chat
if st.button("Clear"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Chat cleared. Paste new code to analyze!"}
    ]
    st.rerun()
