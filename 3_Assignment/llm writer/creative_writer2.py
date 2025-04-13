import openai
import sys

def main():
    # Tarkistetaan, että käyttäjä on antanut promptin komentoriviparametrina
    if len(sys.argv) < 2:
        print("Käyttö: python creative_writer.py 'Anna kirjoitusaiheesi tässä'")
        sys.exit(1)
    
    user_prompt = sys.argv[1]

    # System prompt ohjaa mallia tuottamaan SEO-optimoitua ja synonyymejä runsasta sisältöä
    system_prompt = (
        "Olet luova kirjoittaja, joka tuottaa markkinointimateriaaleja, meemejä, laulun sanoja, runoja tai blogipostauksia. "
        "Kirjoitustesi tulee olla SEO-optimoituja ja sisältää mahdollisimman paljon synonyymejä parantaaksesi hakukonenäkyvyyttä. "
        "Käytä rikasta ja vaihtelevaa kieltä, ole innovatiivinen ja inspiroiva sekä tuota korkealaatuista, mielenkiintoista sisältöä."
    )

    # Määritellään mallin ja parametrien asetukset
    model = "gpt-3.5-turbo"  # Käytetään kustannustehokasta mutta luovaa mallia
    temperature = 0.9
    top_p = 0.95
    frequency_penalty = 0.3
    presence_penalty = 0.6
    max_tokens = 1000

    outputs = []

    # Luodaan 3 eri versiota käyttäjän promptista
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
        text = response.choices[0].message.content
        outputs.append(text)

    # Tulostetaan kaikki 3 versiota komentoriville
    for i, text in enumerate(outputs, 1):
        print(f"Versio {i}:\n{text}\n{'-'*40}\n")

    # Kirjoitetaan tulokset myös tiedostoon
    output_filename = "creative_outputs.txt"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            for i, text in enumerate(outputs, 1):
                f.write(f"Versio {i}:\n{text}\n{'-'*40}\n\n")
        print(f"Tulokset on tallennettu tiedostoon: {output_filename}")
    except Exception as e:
        print(f"Tiedostoon kirjoittamisessa tapahtui virhe: {e}")

if __name__ == "__main__":
    main()
