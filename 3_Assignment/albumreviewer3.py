import openai
import requests

def fetch_album_info(album):
    """
    Fetch album information from the MusicBrainz API.
    
    :param album: Album name or a short description.
    :return: A dictionary with some album details if found, otherwise None.
    """
    url = "http://musicbrainz.org/ws/2/release/"
    params = {"query": f'release:"{album}"', "fmt": "json"}
    headers = {"User-Agent": "MusicCriticReview/1.0 (example@example.com)"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            releases = data.get("releases", [])
            if releases:
                # Palautetaan ensimmäisen osuman perus tiedot
                first = releases[0]
                title = first.get("title", "Unknown Title")
                date = first.get("date", "Unknown Date")
                return {"title": title, "date": date}
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error fetching album info: {e}")
        return None

def get_review(album, style, model, temperature, top_p, frequency_penalty, presence_penalty, max_tokens):
    """
    Generate a concise album review in a specific style.
    
    :param album: The album name or description.
    :param style: A dict with keys 'label' and 'description'.
    :return: Generated review text.
    """
    system_prompt = (
    "You are a seasoned music critic with a razor-sharp wit, a wickedly funny yet vicious sense of humor, and an attitude reminiscent of an evil stand-up comedian. "
    "You have toured with countless bands and know the music scene inside and out. Your reviews are super fun and mean, delivering scathing criticisms with biting sarcasm and unforgettable one-liners. "
    "However, when an album truly shines, you don’t hesitate to give genuine, well-deserved praise. Your commentary balances ruthless insult with moments of brilliant appreciation. "
    "Never start your reviews with bland or uninspired phrases; instead, begin with bold, attention-grabbing openings that set the stage for your no-holds-barred critique. "
    "Conclude each review with a concise star rating (e.g., 'Rating: ★★★★☆').\n\n"
    "Follow these instructions for each review style:\n\n"
    "1. **Serious/Mainstream Music Journalism:** Provide a comprehensive and in-depth analysis of the album’s structure, performance, lyrics, and production. "
    "Your tone should merge professional critique with your signature wicked humor, similar to publications like Rolling Stone or Mojo—but with an extra sting.\n\n"
    "2. **Alternative/Indie/Hipster Magazines:** Write a trend-aware, relaxed review that highlights the aesthetics of alternative and niche genres. "
    "Adopt a style reminiscent of Pitchfork or Stereogum, combining laid-back insights with playful, cutting commentary.\n\n"
    "3. **Fanzine and Small Press:** Deliver an informal, personal, and passionate review that captures the underground spirit and raw, unfiltered attitude of indie fanzines. "
    "Let your genuine passion, brutal honesty, and offbeat humor shine through in every word.\n\n"
    "Do not hold back your opinions—let your true thoughts flow freely with that unmistakably 'mojov' flair, blending scorn and praise into an unforgettable performance!"
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
    temperature = 1.2
    top_p = 0.95
    frequency_penalty = 1.5
    presence_penalty = 1.5
    max_tokens = 800

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
    
    # Create a new Markdown file or clear existing content.
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("# Album Reviews\n\n")
    except Exception as e:
        print(f"Error writing to file: {e}")
    
    album_input = input("Write the album's name for a review.").strip()
    
    # Main loop: continue until an empty input is provided
    while album_input:
        # Fetch album info from the internet
        album_info = fetch_album_info(album_input)
        if album_info is None:
            print(f"Well, it seems there's no trace of \"{album_input}\" in the vast archives of music – a phantom album, perhaps?")
            album_input = input("Which album do you want to review next? ").strip()
            continue
        else:
            print(f"Found album: {album_info['title']} (Released: {album_info['date']})")
        
        reviews = []
        for style in styles:
            review = get_review(album_input, style, model, temperature, top_p, frequency_penalty, presence_penalty, max_tokens)
            reviews.append(review)
        
        # Construct a Markdown formatted section for the album
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
