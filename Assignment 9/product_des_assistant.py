import os
import base64
import google.generativeai as genai
from PIL import Image

#  API-avain ympäristömuuttujasta
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

#  Muunna kuva base64:ksi
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

#  Aseta kuvan polku ja valinnainen käyttäjän teksti
image_path = "Puro_Villahuopa.jpg"
user_text = "Paksu ja pehmeä villahuopa, joka on kudottu laadukkaasta, mulesing-vapaasta villasta. Kohderyhmä: Laatutietoiset lahjan ostajat ja sisustajat."

image_base64 = encode_image(image_path)

#  Luo Gemini Flash -instanssi
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

#  Prompt + multimodaalinen sisältö
response = model.generate_content(
    [
        "You are a structured product content generator AI.",
        {
            "mime_type": "image/jpeg",
            "data": image_base64
        },
        f"""User description: {user_text}

Please output the result in strict JSON format, with the following structure:

{{
  "description": "Short, stylish product description (max 3 sentences).",
  "slogans": [
    "Slogan 1",
    "Slogan 2",
    "Slogan 3"
  ]
}}

Do not include any markdown or explanations. Respond with a valid JSON object only."""
    ],
    generation_config={
        "temperature": 0.8
    }
)

#  Tulosta tulos
print(response.text)
