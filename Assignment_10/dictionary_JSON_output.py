import os
import json
import re
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- Aseta Gemini API käyttöön ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("Ympäristömuuttuja 'GEMINI_API_KEY' puuttuu.")

genai.configure(api_key=api_key)

MODEL_NAME = "gemini-1.5-flash-latest"
model = genai.GenerativeModel(MODEL_NAME)

# Salli kaikki sisällöt
supported_harm_categories = [
    HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    HarmCategory.HARM_CATEGORY_HARASSMENT,
]
safety_settings = {category: HarmBlockThreshold.BLOCK_NONE for category in supported_harm_categories}

# --- Kehotusmalli ---
PROMPT_TEMPLATE = """
You are a multilingual dictionary generator.

Detect the language of the input word: "{word}".

- If the word is in Finnish, generate the entire dictionary entry in Finnish.
- If the word is in English, generate the dictionary entry in English.
- If the word is unknown, try to guess the intended language based on common usage.

Only return valid JSON, without any preamble, explanation or code block formatting.

JSON format:
{{
    "word": "original input word",
    "definition": "definition of the word",
    "synonyms": ["list", "of", "synonyms"],
    "antonyms": ["list", "of", "antonyms"],
    "examples": ["example sentence 1", "example sentence 2"]
}}
"""

# --- Main Loop ---
print("Dictionary Application (Gemini Flash)")
print("Type a word (e.g. programming, koira, freedom) or press Enter to exit.")

while True:
    word = input("\nWord? ").strip()
    if not word:
        print("Exiting.")
        break

    prompt = PROMPT_TEMPLATE.format(word=word)

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2
            ),
            safety_settings=safety_settings
        )

        response_text = response.text.strip()

        # Etsi JSON-objekti säännöllisellä lausekkeella
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            json_string = match.group()
            try:
                data = json.loads(json_string)
                pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
                print(pretty_json)

                # Tallenna JSON tiedostoksi
                safe_filename = f"{data['word'].replace(' ', '_')}.json"
                with open(safe_filename, "w", encoding="utf-8") as f:
                    f.write(pretty_json)

            except json.JSONDecodeError:
                print("⚠️ JSON ei ole kelvollinen.")
                print(json_string)
        else:
            print("⚠️ JSON-muotoista osuutta ei löytynyt.")
            print(response_text)

    except Exception as e:
        print(f"❌ Virhe API-kutsussa: {e}")
