# 🧠 Image-to-Text-to-Image Generator

Tämä projekti on Python-ohjelma, joka lukee kuvan, luo siitä kuvauksen tekoälyn avulla ja generoi sitten uuden kuvan tämän kuvauksen perusteella. Putki toimii seuraavasti:

📷 ➜ 📝 ➜ 🎨  
*Kuva ➜ Tekstikuvaus ➜ Uusi kuva*

## 🔧 Teknologiat

- **OpenAI GPT-4 Turbo** (Vision)
- **OpenAI DALL·E 3**
- **Python** (`openai`, `Pillow`, `requests`)
- **Komentorivikäyttöliittymä**

## 📦 Asennus

1. Luo virtuaaliympäristö (valinnainen mutta suositeltava):

```bash
python -m venv venv
source venv/bin/activate  # tai Windows: venv\Scripts\activate
```

2. Asenna tarvittavat kirjastot:

```bash
pip install openai pillow requests
```

3. Aseta ympäristömuuttuja API-avaimelle:

```bash
export OPENAI_API_KEY=sk-...  # Windows PowerShell: $env:OPENAI_API_KEY="sk-..."
```

## 🚀 Käyttö

```bash
python image_to_text_to_image.py polku/kuvaasi.jpg
```

Ohjelma:
1. Näyttää alkuperäisen kuvan.
2. Lähettää sen GPT-4 Turbo -mallille, joka tuottaa tekstikuvauksen.
3. Syöttää kuvauksen DALL·E 3:lle, joka generoi uuden kuvan.
4. Tallentaa uuden kuvan `generoitu_kuva_*.png` tiedostoksi.

## 🛠 Kehitysideoita

- GUI käyttöliittymä (`tkinter` tai `streamlit`)
- Valinta kielestä (englanti/suomi)
- Kuvien vertailunäyttö
- Kuvan tallennus alkuperäisellä nimellä

## 📄 Lisenssi

Tämä on opiskeluprojekti ja tarkoitettu oppimiskäyttöön.