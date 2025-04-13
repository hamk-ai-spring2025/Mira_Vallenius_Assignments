# LLM CLI Tool – Assignment #4

This is a Python command-line utility that allows querying or summarizing multiple types of input sources using a Language Model (LLM).

## ✅ Features

- Supports `.txt`, `.pdf`, `.docx`, `.csv` and web URLs
- Accepts multiple input sources at once
- Uses OpenAI (or other LLMs via API)
- Default action is **summarization**
- Optional output to file
- Supports `--query`, `--markdown`, `--citations`, `--model`, `--temperature`

## 📦 Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Insert your OpenAI API key into .env
```

## 🚀 Usage

```bash
# Summarize a PDF
python llm_cli_tool.py examples/example.pdf

# Query CSV and DOCX
python llm_cli_tool.py examples/example.csv examples/example.docx -q "What are the key findings?"

# Summarize a web page
python llm_cli_tool.py https://www.paimensukuinen.fi/ -f summary.txt

# Use markdown output
python llm_cli_tool.py examples/example.txt -m

# Use GPT-4 and change temperature
python llm_cli_tool.py examples/example.txt --model gpt-4 --temperature 0.5
```

## 📁 File structure

- `llm_cli_tool.py` – main program
- `examples/` – sample input files
- `test_output/` – example results
- `.env.example` – environment variable template
