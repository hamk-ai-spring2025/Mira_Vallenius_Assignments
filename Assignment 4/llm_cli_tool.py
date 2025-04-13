import argparse
import os
import sys
import requests
from bs4 import BeautifulSoup
from docx import Document
import pandas as pd
import PyPDF2
import openai
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df.to_string(index=False)

def read_url(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    return soup.get_text()

def detect_type(file_path):
    if file_path.startswith("http"):
        return "url"
    ext = Path(file_path).suffix.lower()
    return {
        '.txt': "text",
        '.pdf': "pdf",
        '.docx': "docx",
        '.csv': "csv"
    }.get(ext, None)

def get_content(path):
    t = detect_type(path)
    if not t:
        print(f"Unsupported file type: {path}", file=sys.stderr)
        return ""
    if t == "text":
        return read_text_file(path)
    elif t == "pdf":
        return read_pdf(path)
    elif t == "docx":
        return read_docx(path)
    elif t == "csv":
        return read_csv(path)
    elif t == "url":
        return read_url(path)

def query_llm(prompt, model="gpt-3.5-turbo", temperature=0.7):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

def parse_args():
    epilog = """
Examples:
  python llm_cli_tool.py -r input.txt
  python llm_cli_tool.py -q "What are the key findings?" data.csv notes.docx
  python llm_cli_tool.py url.txt -f summary.txt
    """
    parser = argparse.ArgumentParser(
        description="Summarize or query documents and web pages using LLM.",
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("inputs", nargs="+", help="Input file paths or URLs")
    parser.add_argument("-q", "--query", default="Summarize the content.", help="Query for the LLM")
    parser.add_argument("-f", "--file", help="Optional output file to save the result")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-m", "--markdown", action="store_true", help="Format the output as markdown")
    parser.add_argument("-c", "--citations", action="store_true", help="(Placeholder) Include citations in the output")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model to use (default: gpt-3.5-turbo)")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    return parser.parse_args()

def main():
    args = parse_args()

    all_content = ""
    for source in args.inputs:
        if args.verbose:
            print(f"Reading: {source}")
        try:
            content = get_content(source)
            if content:
                all_content += "\n\n" + content
        except Exception as e:
            print(f"Failed to read {source}: {e}", file=sys.stderr)

    if args.verbose:
        print("Sending to LLM...")

    full_prompt = f"{args.query}\n\n{all_content}"
    result = query_llm(full_prompt, model=args.model, temperature=args.temperature)

    if args.citations:
        result += "\n\n_Lähteet: Yhdistetty useista syötteistä. (Tämä on kosmeettinen placeholder)._"

    if args.markdown:
        result = f"### Vastauksen yhteenveto\n\n{result}"

    if args.file:
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(result)
        if args.verbose:
            print(f"Output written to {args.file}")
    else:
        print(result)

if __name__ == "__main__":
    main()
