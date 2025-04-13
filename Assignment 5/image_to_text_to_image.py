from PIL import Image, ImageOps
import base64
import openai
import argparse
import os
import requests
from datetime import datetime

# Asetetaan API-avain ympäristömuuttujista
openai.api_key = os.getenv("OPENAI_API_KEY")

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_description_from_image(image_path):
    base64_image = encode_image_to_base64(image_path)

    print("[INFO] Lähetetään kuva GPT-4 Turbo Vision -mallille...")

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "Kuvaile tämä kuva tarkasti ja yksityiskohtaisesti suomeksi:"},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}" }}
            ]}
        ],
        max_tokens=300
    )

    return response['choices'][0]['message']['content']

def generate_image_from_description(prompt):
    print("[INFO] Generoidaan kuva DALL·E 3:lla...")

    response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )

    image_url = response['data'][0]['url']
    print("[INFO] Kuva generoitu. Ladataan...")

    image_data = requests.get(image_url).content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generoitu_kuva_{timestamp}.png"

    with open(filename, "wb") as f:
        f.write(image_data)

    print(f"✅ Kuva tallennettu tiedostoon: {filename}")
    return filename

def create_comparison_image(original_path, generated_path):
    original = Image.open(original_path)
    generated = Image.open(generated_path)

    # Muutetaan molemmat samankokoisiksi korkeuden mukaan
    max_height = min(original.height, generated.height)
    original = ImageOps.contain(original, (original.width, max_height))
    generated = ImageOps.contain(generated, (generated.width, max_height))

    # Luodaan tyhjä kangas ja liitetään kuvat vierekkäin
    comparison_width = original.width + generated.width
    comparison_image = Image.new("RGB", (comparison_width, max_height))

    comparison_image.paste(original, (0, 0))
    comparison_image.paste(generated, (original.width, 0))

    comparison_path = "vertailu_kuva.png"
    comparison_image.save(comparison_path)
    print(f"🖼 Vertailukuva tallennettu tiedostoon: {comparison_path}")
    comparison_image.show()

def main():
    parser = argparse.ArgumentParser(description="Image-to-Text-to-Image generaattori")
    parser.add_argument("image_path", type=str, help="Polku syötettävään kuvaan")
    args = parser.parse_args()

    # Näytetään alkuperäinen kuva
    img = Image.open(args.image_path)
    img.show()

    print("[INFO] Generoidaan kuvaus...")
    description = generate_description_from_image(args.image_path)

    print("\n📄 Kuvasta generoitua tekstiä:\n")
    print(description)

    # Generoidaan uusi kuva kuvauksen perusteella
    new_image_path = generate_image_from_description(description)

    # Näytetään vertailu
    create_comparison_image(args.image_path, new_image_path)

if __name__ == "__main__":
    main()
