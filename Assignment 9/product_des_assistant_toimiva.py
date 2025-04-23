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
        "You are a creative AI assistant helping to write stylish product descriptions and slogans.",
        {
            "mime_type": "image/jpeg",
            "data": image_base64
        },
        f"""User description: {user_text}

Please generate the output in markdown format with the following sections:

## Product Description
- Write a short and stylish product description based on the image and user description.
- Limit the description to **a maximum of 3 sentences**.

## Marketing Slogans
- Generate **exactly 3 marketing slogans**.
- Make them concise, creative, and suitable for branding."""
    ],
    generation_config={
        "temperature": 0.8
    }
)

#  Tulosta tulos
print(response.text)
