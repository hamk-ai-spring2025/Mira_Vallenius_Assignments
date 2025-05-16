import streamlit as st
import replicate
import os
import requests
import random

st.set_page_config(page_title="Imagen 3 Fast - AI-kuvageneraattori", layout="wide")
st.title("🚄 Imagen 3 Fast - AI-kuvageneraattori")

# Prompt-variaation generaattori
def generate_prompt_variation(base, styles):
    style_text = ", ".join(styles)
    details = [
        "golden hour lighting",
        "morning mist",
        "dramatic perspective",
        "wild flora around the subject",
        "shallow depth of field",
        "natural forest tones"
    ]
    extra = random.sample(details, 2)
    return f"{base}, {style_text}, {', '.join(extra)}"

with st.sidebar:
    st.header("📝 Kuvan sisältö")
    base_prompt = st.text_area("Pääkohteen kuvaus", "Two red fox kits resting on a moss-covered tree root in a Finnish swamp forest...")
    negative_prompt = st.text_area("🚫 Negatiivinen prompt", "low quality, blurry, text, watermark, error")
    style_tags = st.multiselect(
        "✨ Tyyli / vaikutelma",
        ["photorealistic", "DSLR", "cinematic lighting", "soft focus", "dreamlike", "concept art", "storybook illustration", "studio ghibli style", "oil painting", "impressionist", "glowing light", "autumn tones", "misty atmosphere"],
        default=["photorealistic", "cinematic lighting"]
    )
    auto_prompt = st.checkbox("🔀 Luo variaatioita automaattisesti", value=True)
    if auto_prompt:
        full_prompt = generate_prompt_variation(base_prompt, style_tags)
        st.text_area("🔁 Generoitu variaatio", full_prompt, height=100)
    else:
        full_prompt = base_prompt + ", " + ", ".join(style_tags) if style_tags else base_prompt

    st.header("🖼️ Kuvan asetukset")
    aspect_ratio = st.selectbox("📐 Kuvasuhde", ["1:1", "16:9", "9:16"])
    safety = st.selectbox(
        "🛡️ Suojaustaso",
        ["block_low_and_above", "block_medium_and_above", "block_high_and_above"],
        index=0
    )

    resolution = st.selectbox("🧮 Resoluutio", [
        "Small (512x512)", "Medium (768x512 / 512x768)", "Large (1024x576 / 576x1024)"
    ])
    st.markdown("---")
    generate = st.button("🎨 Generoi kuva")

api_token = os.environ.get("REPLICATE_API_TOKEN")

if not api_token:
    st.error("❌ REPLICATE_API_TOKEN puuttuu ympäristömuuttujista!")
elif generate:
    with st.spinner("🚄 Luodaan kuva Imagen 3 Fast -mallilla..."):
        try:
            # Kuvakoko aspect ration ja resoluution perusteella
            if resolution.startswith("Small"):
                w, h = (512, 512)
            elif resolution.startswith("Medium"):
                w, h = (768, 512) if aspect_ratio == "16:9" else (512, 768)
            else:
                w, h = (1024, 576) if aspect_ratio == "16:9" else (576, 1024)

            output = replicate.run(
                "google/imagen-3-fast",
                input={
                    "prompt": full_prompt,
                    "negative_prompt": negative_prompt,
                    "aspect_ratio": aspect_ratio,
                    "safety_filter_level": safety
                }
            )
            image_url = output[0] if isinstance(output, list) else str(output)
            st.success("✅ Kuva luotu!")
            st.image(image_url, caption="Generoitu kuva", use_container_width=True)

            img_data = requests.get(image_url).content
            st.download_button(
                label="📥 Lataa kuva",
                data=img_data,
                file_name="imagen3_generated.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"❌ Virhe generoinnissa: {e}")
