
# 🤖 Multi-LLM Chat Playground

A clean and responsive Streamlit app for comparing responses from multiple LLMs side by side.

##  Features

- Compare answers from **OpenAI GPT-4**, **Cohere Command-R+**, and **Mistral (OpenRouter)**
- Dynamic multi-column layout
- Real-time response timings
- Chat history with role tags and model icons
- Custom instruction (system prompt) for all models:
  - ❌ No disclaimers
  - ❌ No "As an AI..." phrases
  - ✅ Direct, clear, concise answers only
- Model selector for enabling/disabling models on the fly
- Sidebar instructions for end users
- Clean and default Streamlit look — no custom CSS needed

## 🛠 Setup

### 1. Install dependencies

```bash
pip install streamlit openai requests
```

### 2. Set environment variables

Set the following environment variables in your terminal before running:

```bash
$env:OPENAI_API_KEY = "sk-..."
$env:OPENROUTER_API_KEY = "or-..."
$env:COHERE_API_KEY = "cohere-..."
```

### 3. Run the app

```bash
streamlit run multi_llm_streamlit_app.py
```

## 📌 Notes

- All models are pre-configured to **never refuse questions** with AI disclaimers
- "As an AI..." phrases are blocked via system prompt
- Works best with focused, well-formed prompts

## 🧠 Example Prompt

> What is consciousness in one sentence?

## 📄 License

MIT — Use responsibly.
