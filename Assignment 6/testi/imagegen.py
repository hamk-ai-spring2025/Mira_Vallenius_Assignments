import replicate
import argparse
import os
import requests
import uuid

# Hae API-token ympäristömuuttujasta
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise RuntimeError("Aseta REPLICATE_API_TOKEN ympäristömuuttujaksi.")

REPLICATE_API_TOKEN = REPLICATE_API_TOKEN.strip()  # Poistaa mahdolliset ylimääräiset välilyönnit

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# Käytettävä malli: Luma Labs / Photon
MODEL = "luma/photon"
VERSION = "b8ac6ef4c88955be13c8e8b3e74c9a23c235cb04c57b4b6aaecf73c24dcd3d41"


def generate_images(args):
    inputs = {
        "prompt": args.prompt,
        "num_images": args.num_images,
    }

    if args.seed:
        inputs["seed"] = int(args.seed)

    print("\n🔮 Generoidaan kuvia...\n")
    output = replicate_client.run(
        f"{MODEL}:{VERSION}",
        input=inputs
    )

    if not output:
        print("❌ Kuvien luonti epäonnistui.")
        return

    for idx, url in enumerate(output):
        print(f"✅ Kuvan {idx+1} URL: {url}")
        response = requests.get(url)
        file_name = f"image_{uuid.uuid4().hex[:8]}.png"
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"💾 Tallennettu: {file_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kuvageneraattori komentoriviltä")
    parser.add_argument("--prompt", required=True, help="Kuvaus, mitä halutaan generoida")
    parser.add_argument("--seed", help="Siemenluku (toistettavuuteen)")
    parser.add_argument("--num_images", type=int, default=1, help="Kuvien määrä")

    args = parser.parse_args()
    generate_images(args)