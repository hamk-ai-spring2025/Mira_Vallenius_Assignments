import os
import replicate
import requests
import re
import random
from pathlib import Path

def sanitize_filename(text, max_words=4):
    words = re.findall(r'\w+', text)
    return '_'.join(words[:max_words]).lower()

def choose_aspect_ratio():
    options = {
        "1": ("1:1", (1024, 1024)),
        "2": ("16:9", (1024, 576)),
        "3": ("4:3", (960, 720)),
        "4": ("3:4", (720, 960))
    }
    print("Valitse kuvasuhde:")
    for k, (label, _) in options.items():
        print(f"{k}: {label}")
    while True:
        choice = input("Valintasi: ").strip()
        if choice in options:
            return options[choice]
        print("Virheellinen valinta, yritä uudelleen.")

def main():
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("Virhe: REPLICATE_API_TOKEN ei löytynyt ympäristömuuttujista.")
        return

    os.environ["REPLICATE_API_TOKEN"] = api_token  # varmuuden vuoksi myös tälle muodolle

    prompt = input("Anna kuvaus (prompt): ").strip()
    negative_prompt = input("Anna negatiivinen prompt: ").strip()
    seed_input = input("Anna siemenluku (ENTER = satunnainen): ").strip()
    seed = int(seed_input) if seed_input else random.randint(1, 999999)
    aspect_label, (width, height) = choose_aspect_ratio()

    try:
        num_images = int(input("Montako kuvaa generoidaan (1–5)? ").strip())
        if not 1 <= num_images <= 5:
            raise ValueError
    except ValueError:
        print("Virheellinen määrä. Oletetaan 1.")
        num_images = 1

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    base_filename = sanitize_filename(prompt)

    # Hae tuorein versio SDXL-mallista
    client = replicate.Client(api_token=api_token)
    model = client.models.get("stability-ai/sdxl")
    model_version = model.versions.list()[0].id

    for i in range(1, num_images + 1):
        print(f"🧠 Generoidaan kuva {i}/{num_images}...")
        try:
            output = replicate.run(
                f"stability-ai/sdxl:{model_version}",
                input={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height,
                    "seed": seed + i,
                    "num_outputs": 1,
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5,
                }
            )
        except Exception as e:
            print(f"❌ Virhe generoinnissa: {e}")
            continue

        if not output:
            print("⚠️ Malli ei palauttanut kuvaa.")
            continue

        image_url = output[0]
        try:
            image_data = requests.get(image_url)
            if image_data.status_code == 200:
                filename = output_dir / f"{base_filename}_{i}_{aspect_label.replace(':', 'x')}_seed{seed+i}.png"
                with open(filename, "wb") as f:
                    f.write(image_data.content)
                print(f"✅ [{i}] Tallennettu: {filename}")
                print(f"    URL: {image_url}")
            else:
                print(f"⚠️ [{i}] Virhe ladattaessa kuvaa: {image_data.status_code}")
        except Exception as e:
            print(f"❌ [{i}] Latausvirhe: {e}")

if __name__ == "__main__":
    main()
