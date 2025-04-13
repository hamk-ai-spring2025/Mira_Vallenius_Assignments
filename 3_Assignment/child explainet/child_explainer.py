import openai
import sys

def main():
    # Tarkistetaan, että käyttäjä on antanut käsitteen komentoriviparametrina
    if len(sys.argv) < 2:
        print("Käyttö: python child_explainer.py 'Käsitteen selitys'")
        sys.exit(1)
    
    # Käyttäjän antama käsite, esimerkiksi "mitä ovat muuttolinnut" tai "mikä on tekoäly"
    user_prompt = sys.argv[1]

    # System prompt ohjaa LLM:ää selittämään käsitteen selkeästi ja yksinkertaisesti,
    # käyttäen lyhyitä lauseita, havainnollistavia esimerkkejä ja ystävällistä kieltä,
    # jotta 3–6-vuotiaat lapset ymmärtävät asian.
    system_prompt = (
        "Olet ystävällinen ja selittävä opettaja, joka osaa kertoa monimutkaiset käsitteet 3–6-vuotiaille lapsille selkeästi ja ymmärrettävästi. "
        "Käytä yksinkertaista kieltä, lyhyitä lauseita ja havainnollistavia esimerkkejä. Tee selityksestä hauska ja innostava, jotta lapset innostuvat oppimaan."
    )
    
    # Määritellään mallin ja parametrien asetukset
    model = "gpt-3.5-turbo"  # kustannustehokas ja laadukas malli
    temperature = 0.7         # hieman hillitympi luovuus, jotta selitykset pysyvät helposti ymmärrettävinä
    top_p = 0.95
    frequency_penalty = 0.0
    presence_penalty = 0.0
    max_tokens = 500          # riittävä määrä tokenia lyhyelle lapsille soveltuvalle vastaukselle

    outputs = []

    # Luodaan 3 eri versiota käsitteen selityksestä
    for i in range(3):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            max_tokens=max_tokens,
            stream=False,
        )
        text = response.choices[0].message.content.strip()
        outputs.append(text)

    # Tulostetaan kaikki versiot komentoriville
    for i, text in enumerate(outputs, 1):
        print(f"Versio {i}:\n{text}\n{'-'*40}\n")

    # Tallennetaan tulokset tiedostoon
    output_filename = "child_explanations.txt"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            for i, text in enumerate(outputs, 1):
                f.write(f"Versio {i}:\n{text}\n{'-'*40}\n\n")
        print(f"Tulokset on tallennettu tiedostoon: {output_filename}")
    except Exception as e:
        print(f"Tiedostoon kirjoittamisessa tapahtui virhe: {e}")

if __name__ == "__main__":
    main()
