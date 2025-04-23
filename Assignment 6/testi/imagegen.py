import os
import requests
import json
import re
from pathlib import Path

def sanitize_filename(text, max_words=4):
    # Poista erikoismerkit ja ota ensimmäiset sanat
    words = re.findall(r'\w+', text)
    return '_'.join(words[:max_words]).lower()

def choose_aspect_ratio():
    options = {
        "1": ("1:1", "512x512"),
        "2": ("16:9", "1024x1024"),  # Approximaatio
        "3": ("4:3", "512x512"),
        "4": ("3:4", "512x512")
    }
    print("Valitse kuvasuhde:")
    for k, (label, _) in options.items():
        print(f"{k}: {label}")
    while True:
        choice = input("Valintasi: ").strip()
        if choice in options:
            return options[choice][1], options[choice][0]
        print("Virheellinen valinta, yritä uudelleen.")

def main():
    # API-avain ympäristömuuttujista
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Virhe: OPENAI_API_KEY ei löytynyt ympäristömuuttujista.")
        return

    prompt = input("Anna kuvaus (prompt): ").strip()
    negative_prompt = input("Anna negatiivinen prompt (ei käytössä DALL·E 2:ssa, voit ohittaa): ").strip()
    aspect_size, aspect_label = choose_aspect_ratio()
    try:
        num_images = int(input("Montako kuvaa generoidaan (1–10)? ").strip())
    except ValueError:
        print("Virheellinen määrä. Oletetaan 1.")
        num_images = 1

    # Luo output-kansio
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # OpenAI API -kutsu
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
    "prompt": prompt,
    "n": num_images,
    "size": aspect_size
}

    print("Generoidaan kuvia...")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Virhe API-kutsussa: {response.status_code} – {response.text}")
        return

    data = response.json()
    urls = [item['url'] for item in data['data']]
    print("Kuvat generoitu. Ladataan...")

    base_filename = sanitize_filename(prompt)

    for i, image_url in enumerate(urls, start=1):
        response = requests.get(image_url)
        if response.status_code == 200:
            filename = output_dir / f"{base_filename}_{i}_{aspect_label.replace(':', 'x')}.png"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"[{i}] Tallennettu: {filename}")
            print(f"    URL: {image_url}")
        else:
            print(f"Virhe ladattaessa kuvaa {i}: {response.status_code}")

if __name__ == "__main__":
    main()
