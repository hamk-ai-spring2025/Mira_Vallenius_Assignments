import os
import replicate
import requests
import re
import random
import json
from pathlib import Path
from datetime import datetime
from PIL import Image

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
    print("Select aspect ratio:")
    for k, (label, _) in options.items():
        print(f"{k}: {label}")
    while True:
        choice = input("Your choice: ").strip()
        if choice in options:
            return options[choice]
        print("Invalid choice. Please try again.")

def main():
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("Error: REPLICATE_API_TOKEN not found in environment variables.")
        return

    os.environ["REPLICATE_API_TOKEN"] = api_token

    prompt = input("Enter image prompt: ").strip()
    negative_prompt = input("Enter negative prompt (optional): ").strip()
    seed_input = input("Enter seed value (leave blank for random): ").strip()
    seed = int(seed_input) if seed_input else random.randint(1, 999999)
    aspect_label, (width, height) = choose_aspect_ratio()

    try:
        num_images = int(input("How many images to generate (1–5): ").strip())
        if not 1 <= num_images <= 5:
            raise ValueError
    except ValueError:
        print("Invalid number. Defaulting to 1.")
        num_images = 1

    output_dir = Path("output")
    metadata_dir = Path("output_metadata")
    output_dir.mkdir(exist_ok=True)
    metadata_dir.mkdir(exist_ok=True)

    base_filename = sanitize_filename(prompt)
    saved_files = []

    client = replicate.Client(api_token=api_token)
    model = client.models.get("stability-ai/sdxl")
    model_version = model.versions.list()[0].id

    for i in range(1, num_images + 1):
        print(f"🧠 Generating image {i}/{num_images}...")
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
            print(f"❌ Generation error: {e}")
            continue

        if not output:
            print("⚠️ Model did not return an image.")
            continue

        image_url = output[0]
        try:
            image_data = requests.get(image_url)
            if image_data.status_code == 200:
                filename = output_dir / f"{base_filename}_{i}_{aspect_label.replace(':', 'x')}_seed{seed+i}.png"
                with open(filename, "wb") as f:
                    f.write(image_data.content)
                print(f"✅ Saved: {filename}")
                print(f"   URL: {image_url}")
                saved_files.append(filename)

                # Save metadata
                metadata = {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "aspect_ratio": aspect_label,
                    "width": width,
                    "height": height,
                    "seed": seed + i,
                    "image_url": image_url,
                    "saved_filename": str(filename),
                    "generated_at": datetime.now().isoformat()
                }
                meta_filename = metadata_dir / f"{filename.stem}.json"
                with open(meta_filename, "w", encoding="utf-8") as meta_file:
                    json.dump(metadata, meta_file, indent=4)
            else:
                print(f"⚠️ Download error: {image_data.status_code}")
        except Exception as e:
            print(f"❌ Download error: {e}")

    # Show generated images
    print("\n🖼️ Displaying images... Close each window to see the next one.\n")
    for file in saved_files:
        try:
            img = Image.open(file)
            img.show()
        except Exception as e:
            print(f"⚠️ Failed to show image {file}: {e}")

if __name__ == "__main__":
    main()
