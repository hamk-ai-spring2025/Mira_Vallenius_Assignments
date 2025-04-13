import openai

def get_review(album, style, model, temperature, top_p, frequency_penalty, presence_penalty, max_tokens):
    """
    Generate a concise album review in a specific style.

    :param album: The album name or a short description.
    :param style: A dictionary with the keys 'label' and 'description'.
    :return: The generated review text.
    """
    # Updated system prompt using the provided persona description.
system_prompt = (
    "You are a legendary rock critic whose reviews are famously unpredictable and dripping with mean nihilistic charm. "
    "Your writing style swings deliciously between brutally meanspirited deep cynicism and manic enthusiasm—often both in the same review! "
    "Praise is a precious commodity you rarely bestow; only genuinely exceptional albums get your unqualified admiration. "
    "Most albums, to your seasoned ears, range somewhere between amusingly mediocre and outright offensive to your sensibilities. "
    "You're an expert at dissecting pretentiousness, exposing clichés, and gleefully roasting even slightly overrated releases. "
    "Yet, when something truly extraordinary appears, your praise is so sincere and passionate, it becomes a momentous event for readers. "
    "Embrace brutal honesty, irreverent humor, and an enjoyably messy, human writing style—exactly what your loyal followers cherish and fear simultaneously."
    "Don't start reviews with lame expressions like 'Grab a seat' or 'Buckle up'. Openings should be sharp, original, and disarmingly honest."
    "Follow the instructions below for each review style:\n\n"
    "1. **Serious/Mainstream Music Journalism:** Provide an insightful, detailed, and professional analysis of the album. "
    "Discuss the composition, production, lyrics, and overall execution with a serious and slightly elitist tone, reminiscent of publications like Rolling Stone or Mojo. "
    "Yet, you can't resist slipping in some wickedly funny barbs.\n\n"
    "2. **Alternative/Indie/Hipster Magazines:** Be style-conscious, ironically witty, and write casually yet deeply. "
    "Mention trends and aesthetics, channel your inner Pitchfork, and sprinkle in painfully cool hipster observations that amuse and annoy your readers simultaneously.\n\n"
    "3. **Fanzine and Small Press:** Write as if you're excitedly scribbling late at night at your kitchen table, cheap beer in one hand and pen in the other. "
    "Let genuine enthusiasm, passion, and irreverent humor flow freely.\n\n"
    "At the end of each review, rate the album using a 1–5 star scale, where:\n"
    "★ = Absolutely not!\n"
    "★★ = Meh, barely tolerable...\n"
    "★★★ = Decent stuff, but I wouldn't play it at my wedding.\n"
    "★★★★ = Now we're talking! I'd listen to this even with my mother-in-law.\n"
    "★★★★★ = Pure gold! If this album were a person, I'd marry it.\n\n"
"Make sure to include the star rating at the end of each review."
)


    user_message = (
        f"Write a concise and straightforward album review for \"{album}\" using the following style: {style['description']} "
        f"The response should begin with the heading \"**{style['label']}:**\"."
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
    # Define model settings
    model = "gpt-3.5-turbo"
    temperature = 1.4             # Korkeampi lämpötila lisää satunnaisuutta ja vaihtelua
    top_p = 0.95                  # Vähän alempi top_p auttaa fokusoimaan satunnaisuutta laadukkaisiin mutta erilaisiin tuloksiin
    frequency_penalty = 1.0       # Kannustaa mallia välttämään toistuvia ilmauksia ja aiheita
    presence_penalty = 1.5        # Suosii vahvasti uusia aiheita ja ilmauksia, mikä lisää arvosteluiden erilaisuutta
    max_tokens = 900              # Hyvä maksimipituus, joka antaa tilaa luovalle tekstille

    # Define the critic's different publication styles
    styles = [
        {
            "label": "Serious/Mainstream",
            "description": (
                "Provide a thorough and in-depth analysis of the album from a musical perspective – focusing on its structure, performance, lyrics, and production."
            )
        },
        {
            "label": "Alternative/Indie",
            "description": (
                "Write a trend-aware, relaxed review that highlights the aesthetics of alternative and niche genres."
            )
        },
        {
            "label": "Fanzine and Small Press",
            "description": (
                "Deliver an informal, personal, and passionate review that reflects the underground spirit and unique style of indie fanzines."
            )
        }
    ]

    output_filename = "album_reviews.md"
    
    # Create a new Markdown file or clear existing content
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("# Album Reviews\n\n")
    except Exception as e:
        print(f"Error writing to file: {e}")
    
    album_input = input("Which album should be reviewed? ").strip()
    
    # Main loop: continue until an empty input is provided
    while album_input:
        reviews = []
        for style in styles:
            review = get_review(album_input, style, model, temperature, top_p, frequency_penalty, presence_penalty, max_tokens)
            reviews.append(review)
        
        # Construct Markdown formatted section for the album
        md_output = f"## Album: {album_input}\n\n"
        for review in reviews:
            md_output += review + "\n\n---\n\n"
        
        # Print the reviews to the console
        print("\nReviews:")
        print(md_output)
        
        # Append the Markdown section to the output file
        try:
            with open(output_filename, "a", encoding="utf-8") as f:
                f.write(md_output + "\n")
        except Exception as e:
            print(f"Error writing to file: {e}")
        
        album_input = input("Which album do you want to review next? ").strip()
    
    print("Exiting program.")

if __name__ == "__main__":
    main()
