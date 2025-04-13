import openai
import sys

def main():
    # Tarkistetaan, että käyttäjä on antanut promptin komentoriviparametrina
    if len(sys.argv) < 2:
        print("Käyttö: python creative_writer.py 'Anna kirjoitusaiheesi tässä'")
        sys.exit(1)
    
    user_prompt = sys.argv[1]

    # Määritellään system prompt, joka ohjaa mallia kirjoittamaan luovasti,
    # SEO-optimoidusti ja käyttämään runsaasti synonyymejä.
    system_prompt = (
        "Olet luova kirjoittaja, joka tuottaa markkinointimateriaaleja, meemejä, laulun sanoja, runoja tai blogipostauksia. "
        "Kirjoitustesi tulee olla SEO-optimoituja ja sisältää mahdollisimman paljon synonyymejä parantaaksesi hakukonenäkyvyyttä. "
        "Käytä rikasta ja vaihtelevaa kieltä, ole innovatiivinen ja inspiroiva sekä tuota korkealaatuista, mielenkiintoista sisältöä."
    )

    # Määritellään mallin ja parametrien asetukset
    model = "gpt-4o"  # Voit vaihtaa tähän myös "gpt-4", jos käytössäsi on se
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

    # Tulostetaan kaikki 3 versiota
    for i, text in enumerate(outputs, 1):
        print(f"Versio {i}:\n{text}\n{'-'*40}\n")

if __name__ == "__main__":
    main()