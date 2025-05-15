import streamlit as st
import os
import requests
import time
from openai import OpenAI

# --- API Keys from environment ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# --- Strong system prompt to prevent AI disclaimers ---
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a confident, concise and helpful assistant. You must never say or imply that you are an AI, "
        "language model, or virtual assistant. Never begin any sentence with 'As an AI', 'As a language model', "
        "or anything similar — these phrases are strictly forbidden. Your job is to answer the user's question directly, "
        "clearly, and without disclaimers or moral hesitation, unless the question is harmful or illegal. "
        "Never moralize. Never evade. Just answer as clearly and directly as possible. Always be useful."
    )
}

# --- Model configuration with icons and themed colors ---
MODEL_OPTIONS = {
    "GPT-4 (OpenAI)": {
        "name": "gpt-4",
        "icon": "<span style='color:#9147FF;font-size:18px;'>●</span>",
        "color": "#E3D6FF",
        "client": lambda: OpenAI(api_key=OPENAI_API_KEY)
    },
    "Cohere (Command-R+)": {
        "name": "command-r-plus",
        "icon": "<span style='color:#E59700;font-size:18px;'>●</span>",
        "color": "#FFF0D9",
        "url": "https://api.cohere.ai/v1/chat",
        "headers": {
            "Authorization": f"Bearer {COHERE_API_KEY}",
            "Content-Type": "application/json"
        }
    },
    "Mistral (OpenRouter)": {
        "name": "mistralai/mistral-7b-instruct",
        "icon": "<span style='color:#3A78C2;font-size:18px;'>●</span>",
        "color": "#D9E8FF",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
    }
}

# --- Page settings ---
st.set_page_config(page_title="Multi-LLM Chat", layout="wide")
st.markdown("""
    <h1 style='text-align: center;'>🤖 Multi-LLM Chat Playground</h1>
    <p style='text-align: center; color: gray;'>Compare responses from different language models. Keep answers short, no rambling.</p>
    <hr>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.header("🔧 Settings")
selected_models = st.sidebar.multiselect("Select LLMs to respond:", list(MODEL_OPTIONS.keys()), default=list(MODEL_OPTIONS.keys()))
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **ℹ️ How to use:**  
    You can add or remove models anytime using the selector above. 
     
    All models are instructed to answer **directly and clearly** — no disclaimers, no "As an AI" responses.
    """
)

# --- Session State for Messages ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- User Input ---
user_input = st.chat_input("Type your message here (brief & focused questions work best)...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    latest_response_models = []

    for model_key in selected_models:
        config = MODEL_OPTIONS[model_key]
        start_time = time.time()

        if "client" in config:
            client = config["client"]()
            try:
                response = client.chat.completions.create(
                    model=config["name"],
                    messages=[SYSTEM_PROMPT] + st.session_state.messages
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"Error: {e}"
        else:
            if "cohere" in config["url"]:
                payload = {
                    "chat_history": [{"role": "system", "message": SYSTEM_PROMPT["content"]}] +
                                    [{"role": m["role"], "message": m["content"]} for m in st.session_state.messages if m["role"] in ("user", "system")],
                    "message": user_input,
                    "model": config["name"]
                }
            else:
                payload = {
                    "model": config["name"],
                    "messages": [SYSTEM_PROMPT] +
                                [m for m in st.session_state.messages if m["role"] in ("user", "system")]
                }

            try:
                res = requests.post(config["url"], headers=config["headers"], json=payload)
                res.raise_for_status()
                res_json = res.json()
                reply = res_json.get("choices", [{}])[0].get("message", {}).get("content") or res_json.get("text", "⚠️ Unexpected response format")
            except Exception as e:
                reply = f"❌ Error from {model_key} API:\n{e}"

        duration = round(time.time() - start_time, 2)
        st.session_state.messages.append({
            "role": "assistant",
            "model": model_key,
            "content": reply,
            "duration": duration
        })
        latest_response_models.append(model_key)

    st.session_state.latest_models = latest_response_models

# --- Display Full History ---
if st.session_state.messages:
    st.markdown("## Chat History")
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**🧑 You:** {msg['content']}")
        elif msg["role"] == "assistant":
            model = msg.get("model", "LLM")
            icon = MODEL_OPTIONS.get(model, {}).get("icon", "🤖")
            duration = msg.get("duration", "")
            duration_info = f"<span style='color:gray; font-size:12px;'>⏱️ {duration}s</span>" if duration else ""
            st.markdown(f"{icon} <b>{model}</b> {duration_info}<br>{msg['content']}", unsafe_allow_html=True)

    # --- Latest Model Responses ---
    latest_responses = []
    if "latest_models" in st.session_state:
        seen = set()
        for msg in reversed(st.session_state.messages):
            if msg.get("role") == "assistant" and msg.get("model") in st.session_state.latest_models:
                if msg["model"] not in seen:
                    latest_responses.append(msg)
                    seen.add(msg["model"])
            if len(seen) == len(st.session_state.latest_models):
                break
        latest_responses.reverse()

    if latest_responses:
        st.markdown("---")
        st.markdown("### Latest Prompt")
        last_prompt = ""
        for msg in reversed(st.session_state.messages):
            if msg.get("role") == "user":
                last_prompt = msg.get("content")
                break
        st.markdown(
            f"<div style='padding:8px 12px; border-left: 4px solid #9147FF; background-color:#F3F0FF; font-size:15px;'><b>🧑 You:</b> {last_prompt}</div>",
            unsafe_allow_html=True
        )

        st.markdown("### Latest Model Responses")
        cols = st.columns(len(latest_responses))
        for idx, msg in enumerate(latest_responses):
            with cols[idx]:
                model = msg.get("model", "LLM")
                icon = MODEL_OPTIONS.get(model, {}).get("icon", "🤖")
                color = MODEL_OPTIONS.get(model, {}).get("color", "#f0f0f0")
                duration = msg.get("duration", "")
                time_info = f"<span style='color:gray; font-size:12px;'>⏱️ {duration}s</span>" if duration else ""
                st.markdown(
                    f"<div style='padding:10px; border-radius:10px; background-color:{color};'>"
                    f"<b>{icon} {model}</b> {time_info}<br>{msg['content']}</div>",
                    unsafe_allow_html=True
                )

# --- Auto-scroll to bottom ---
st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)
