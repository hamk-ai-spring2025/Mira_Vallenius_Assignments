import openai

def get_answers(user_prompt, system_prompt, model, temperature, top_p, frequency_penalty, presence_penalty, max_tokens):
    outputs = []
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
    return outputs

def main():
    # System prompt ohjaa LLM:ää selittämään käsitteet 3–6-vuotiaille ymmärrettävällä tavalla
    system_prompt = (
        "Olet inspiroiva mutta selkeä opettaja, joka osaa selittää monimutkaiset käsitteet 3–6-vuotiaille lapsille sekä opettavaisella että innostavalla tavalla. "
        "Yhdistä tarinankerronta ja yksinkertaiset esimerkit, jotta lapset viihtyvät ja oppivat samalla."
    )
    
    # Määritellään mallin asetukset
    model = "gpt-3.5-turbo"  # kustannustehokas ja laadukas malli luovaan kirjoittamiseen
    temperature = 0.7         # Tasapainoisen luovuuden ja johdonmukaisuuden saavuttamiseksi.
    top_p = 0.95
    frequency_penalty = 0.3 # rajoitetaan toistuvia sanoja
    presence_penalty = 0.2 # rohkaistaan uusia ideoita
    max_tokens = 500
    
    output_filename = "child_explanations.txt"
    
    # Poistetaan mahdollisesti vanha sisältö tiedostosta, jotta aloitamme puhtaasti
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("Child Explanations Outputs\n\n")
    except Exception as e:
        print(f"Tiedostoon kirjoittamisessa tapahtui virhe: {e}")
    
    # Ensimmäinen kysymys: "Mitä haluaisit tietää?"
    user_input = input("Mitä haluaisit tietää? ").strip()
    
    # Pääsilmukka: jatketaan, kunnes käyttäjä ei syötä mitään
    while user_input:
        # Generoidaan kolme versiota vastauksista
        outputs = get_answers(user_input, system_prompt, model, temperature, top_p, frequency_penalty, presence_penalty, max_tokens)
        
        # Tulostetaan tulokset komentoriville
        print("\nTulokset:")
        print(f"Kysymys: {user_input}\n")
        for i, text in enumerate(outputs, 1):
            answer_text = f"Versio {i}:\n{text}\n{'-'*40}\n"
            print(answer_text)
        
        # Tallennetaan tulokset tiedostoon
        try:
            with open(output_filename, "a", encoding="utf-8") as f:
                f.write(f"Kysymys: {user_input}\n")
                for i, text in enumerate(outputs, 1):
                    f.write(f"Versio {i}:\n{text}\n{'-'*40}\n\n")
                f.write("\n")
        except Exception as e:
            print(f"Tiedostoon kirjoittamisessa tapahtui virhe: {e}")
        
        # Kysytään seuraavaa kysymystä
        user_input = input("Mitä haluat tietää seuraavaksi? ").strip()
    
    print("Ohjelma lopetetaan.")

if __name__ == "__main__":
    main()
