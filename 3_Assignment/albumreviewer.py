import openai

def get_review(album, style, model, temperature, top_p, frequency_penalty, presence_penalty, max_tokens):
    """
    Generoi levystä napakan arvostelun tietyllä tyylillä.
    
    :param album: Albumin nimi tai lyhyt kuvaus.
    :param style: Sanakirja, jossa on avaimet 'label' ja 'description'.
    :return: Luotu arvostelu teksti.
    """
    system_prompt = (
        "Olet kokenut ja kyyninen rockkriitikko, joka on nähnyt bändejä nousevan ja tuhoutuvan vuosikymmenten ajan. "
        "Et säästele sanojasi, ja sinulla on aina vahva mielipide."
    )
    user_message = (
        f"Kirjoita napakka ja suorasukainen arvostelu albumista \"{album}\" käyttäen seuraavaa tyyliä: {style['description']} "
        f"Vastauksen tulee alkaa otsikolla \"**{style['label']}:**\". Älä pidättele kritiikissäsi!"
    )
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        max_tokens=max_tokens,
        stream=False
    )
    review_text = response.choices[0].message.content.strip()
    return review_text

def main():
    # Määritellään mallin asetukset
    model = "gpt-3.5-turbo"
    temperature = 0.8
    top_p = 0.95
    frequency_penalty = 0.3
    presence_penalty = 0.5
    max_tokens = 500

    # Määritellään kolme näkökulmaa
    styles = [
        {
            "label": "Analyyttinen Puristi",
            "description": (
                "Pureutuu levyn rakenteeseen, soittoon, sanoituksiin ja tuotantoon. Vertaa menneisiin suuruuksiin ja etsi armotta heikkouksia. "
                "Syväluotaavaa, kriittistä, historiaan ja teoriaan painottuvaa asiantuntijakirjoittamista."
            )
        },
        {
            "label": "Trenditietoinen Kyynikko",
            "description": (
                "Arvioi levyn ajankohtaisuutta, potentiaalista vaikutusta ja 'cooliutta'. Ole skeptinen hypen suhteen ja viittaa "
                "ajankohtaisiin ilmiöihin sarkastisesti."
            )
        },
        {
            "label": "Vanhan Liiton Murisija",
            "description": (
                "Arvioi levyn uskollisuutta 'oikealle' rock-hengelle ja artistin aikaisemmalle tuotannolle. "
                "Ole epämuodollinen, puolueellinen, tunteellinen ja intohimoinen. Vihaa tai rakasta levyä."
            )
        }
    ]

    output_filename = "album_reviews.md"
    
    # Tyhjennetään mahdollisesti vanha sisältö tai luodaan uusi Markdown-tiedosto
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("# Album Reviews\n\n")
    except Exception as e:
        print(f"Tiedostoon kirjoittamisessa tapahtui virhe: {e}")
    
    album_input = input("Mikä albumi on analysoitavana? ").strip()
    
    # Pääsilmukka: jatketaan kunnes käyttäjä antaa tyhjän syötteen
    while album_input:
        reviews = []
        for style in styles:
            review = get_review(album_input, style, model, temperature, top_p, frequency_penalty, presence_penalty, max_tokens)
            reviews.append(review)
        
        # Muodostetaan Markdown-muotoinen osio kyseiselle albumille
        md_output = f"## Albumi: {album_input}\n\n"
        for review in reviews:
            md_output += review + "\n\n---\n\n"
        
        # Tulostetaan myös komentoriville
        print("\nArvostelut:")
        print(md_output)
        
        # Lisätään Markdown-osio tiedostoon
        try:
            with open(output_filename, "a", encoding="utf-8") as f:
                f.write(md_output + "\n")
        except Exception as e:
            print(f"Tiedostoon kirjoittamisessa tapahtui virhe: {e}")
        
        album_input = input("Mitä albumia haluat seuraavaksi analysoida? ").strip()
    
    print("Ohjelma lopetetaan.")

if __name__ == "__main__":
    main()
