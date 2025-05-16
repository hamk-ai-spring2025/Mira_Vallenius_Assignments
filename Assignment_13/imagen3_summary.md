Tässä lyhyt yhteenveto siitä, mitä tehtiin, millä työvälineillä ja miten

---

## Projektin yhteenveto: Imagen 3 Fast - AI-kuvageneraattori

### Työkalut ja teknologiat
- OpenAI ChatGPT + Streamlit: frontend-käyttöliittymän rakentamiseen
- Replicate API: kuvien generointiin Google Imagen 3 Fast -mallilla
- Python: backend-logiikan hallintaan
- Ympäristömuuttujat (REPLICATE_API_TOKEN): tietoturvalliseen avainten käyttöön

---

### Toteutetut ominaisuudet

- Streamlit UI:
  - Responsiivinen ja selkeä käyttöliittymä, jossa säädöt vasemmassa sivupalkissa
  - Promptin, negatiivisen promptin, kuvasuhteen, tyylien ja suojaustason valinta

- Kuvanhallinta:
  - Mahdollisuus valita resoluutio (pieni, keskitaso, suuri)
  - Kuva ladataan automaattisesti, kun se on valmis
  - Latauspainike (Lataa kuva) toimii heti kuvan valmistuttua

- Älykäs prompti:
  - Automaattinen prompt-variaation generaattori (lisää yksityiskohtia satunnaisesti)
  - Valmiita promptiehdotuksia: sadunomainen metsätarina, kuplassa leijuva kettu, Pride-ketun lähikuva
  - Tyylit lisätään promptiin dynaamisesti (esim. “photorealistic, glowing light, cinematic lighting”)

---

### Mallin käytön logiikka (Imagen 3 Fast @ Replicate)

```python
replicate.run(
    "google/imagen-3-fast",
    input={
        "prompt": <täydellinen promtti>,
        "negative_prompt": <ei-toivotut asiat>,
        "aspect_ratio": "16:9",
        "safety_filter_level": "block_low_and_above"
    }
)
```

Kuvan URL palautetaan listana output[0], ja haetaan requests.get() avulla kuvan latausta varten.

---

### Seuraavat mahdolliset jatkokehitykset:
- Prompt-historian tallennus ja selaus
- Galleriatoiminto generoituja kuvia varten
- Eri mallien (esim. SDXL, Realistic Vision) valinta yhdestä sovelluksesta
- Kuvan jälkikäsittely suoraan käyttöliittymässä (esim. filtteri, rajaus)
