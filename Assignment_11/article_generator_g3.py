import google.generativeai as genai
import os
import pypandoc
import re
from datetime import datetime
# from langdetect import detect, LangDetectException # Voit ottaa tämän käyttöön, jos haluat tarkempaa kielen tunnistusta

# --- Konfiguraatio ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("Virhe: GOOGLE_API_KEY ympäristömuuttujaa ei löydy.")
    print("Aseta se esim. komennolla (Windows): setx GOOGLE_API_KEY \"SINUN_API_AVAIMESI\"")
    print("Ja käynnistä komentokehote/IDE uudelleen.")
    print("Varmista myös, että 'Generative Language API' on käytössä Google Cloud projektissasi.")
    exit()

MODEL_NAME_GOOGLE = "gemini-1.5-flash-latest" # Tai "gemini-1.0-pro" tai "gemini-1.5-pro-latest"

# --- Funktioiden määrittelyt ---

def generate_article_markdown_google_v2(topic: str) -> tuple[str | None, list | None]:
    """
    Generoi tieteellisen artikkelin Markdown-muodossa annetun aiheen kielellä,
    painottaen DOI-lähteitä ja pyytäen LLM:ää arvioimaan viitteiden aitoutta.
    Artikkelin pyydetään olevan laajempi.
    """
    language_for_prompt = "annetun aiheen kieli"
    reference_section_title_example = "## References (tai vastaava aiheen kielellä)"
    assessment_tag_example = "[Assessment: Likely real (tai vastaava aiheen kielellä)]"
    
    topic_lower = topic.lower()
    # Karkea kielen tunnistus (voit korvata langdetectillä)
    is_finnish_topic = any(char in topic_lower for char in ['ä', 'ö']) or " ja " in topic_lower
    is_english_topic = any(word in topic_lower.split() for word in ["the", "and", "of", "in", "for", "on"])

    if is_finnish_topic and not is_english_topic: # Suositaan suomea, jos selkeät indikaattorit
        language_for_prompt = "suomi"
        reference_section_title_example = "## Lähdeluettelo"
        assessment_tag_example = "[Arvio: Todennäköisesti todellinen]"
    elif is_english_topic: # Jos ei selkeästi suomea mutta englantia, oletetaan englanti
        language_for_prompt = "englanti"
        reference_section_title_example = "## References"
        assessment_tag_example = "[Assessment: Likely real]"
    # Muussa tapauksessa käytetään oletuksia (annetaan LLM:n päätellä)

    prompt = f"""
    Tehtävä: Luo laaja ja syvällinen tieteellinen artikkeli alla annetusta aiheesta.
    **TÄRKEÄÄ: Artikkelin kieli tulee olla {language_for_prompt.upper()}.** Noudata tätä kielivaatimusta kaikissa tekstin osissa.

    Aihe: "{topic}"

    Rakennevaatimukset (kaikki osat {language_for_prompt.upper()}):
    1.  **Otsikko**
    2.  **Tiivistelmä (Abstract)**
    3.  **Johdanto (Introduction)**
    4.  **Pääluvut (Chapters)** (useita, alalukuineen)
        *   Esimerkki osioiden nimistä (sovella kieltä): Kirjallisuuskatsaus, Menetelmät, Tulokset, Pohdinta.
        *   Käytä Markdown-otsikkotasoja (#, ##, ###).
    5.  **Taulukot ja/tai Kuviot (Tables/Figures)** (vähintään 1-2 relevanttia)
    6.  **Johtopäätökset (Conclusions)**
    7.  **Lähdeluettelo (References):**
        *   Tämän osion tulee alkaa AINOASTAAN Markdown-otsikolla: `{reference_section_title_example}`.
        *   Pyri ensisijaisesti käyttämään lähteitä, joilla on DOI-tunniste.
        *   Sisällytä niin monta relevanttia lähdettä kuin katsot tarpeelliseksi.
        *   Lähdeluettelon tulee olla APA 7th edition -tyylin mukainen.
        *   JOKAISEN viitteen JÄLKEEN, SAMALLE RIVILLE, lisää merkintä sen todennäköisestä aitoudesta seuraavassa muodossa: `{assessment_tag_example}`.
            Esimerkki ({language_for_prompt}):
            Tekijä, A. (Vuosi). Artikkelin otsikko. *Lehden nimi*, *volyymi*(numero), sivut. https://doi.org/xxxx {assessment_tag_example}
    8.  **Tekstinsisäiset viittaukset** (APA 7th)

    Muotoilu:
    *   Koko artikkeli tulee olla Markdown-muodossa.
    *   Käytä tieteellistä ja akateemista kieltä ({language_for_prompt.upper()}).

    VASTAA VAIN ITSE ARTIKKELIN MARKDOWN-SISÄLLÖLLÄ {language_for_prompt.upper()}.
    ÄLÄ LISÄÄ MITÄÄN YLIMÄÄRÄISTÄ TEKSTIÄ ENNEN ARTIKKELIN ALKUA TAI SEN JÄLKEEN.
    ARTIKKELIN PITÄÄ LOPPUA VIIMEISEEN LÄHDELUETTELON VIITTEESEEN (ja sen arviointimerkintään).
    """
    print(f"\nGeneroidaan laajaa artikkelia aiheesta (pyydetty kieli: {language_for_prompt.upper()}): '{topic}' Google Geminillä (malli: {MODEL_NAME_GOOGLE})...\n")
    try:
        model = genai.GenerativeModel(
            MODEL_NAME_GOOGLE,
            system_instruction=f"Olet erittäin taitava tieteellinen kirjoittaja-assistentti. Tuotat laajoja, hyvin perusteltuja artikkeleita Markdown-muodossa APA-tyylillä. **Noudata tarkasti kehotteessa annettua kielivaatimusta (oletus {language_for_prompt.upper()}).** Keskityt DOI-lähteisiin ja arvioit niiden aitoutta."
        )
        generation_config = genai.types.GenerationConfig(
            temperature=0.6,
            max_output_tokens=16384
        )
        response = model.generate_content(prompt, generation_config=generation_config)

        if response.prompt_feedback and response.prompt_feedback.block_reason:
            print(f"Sisällön generointi estettiin Googlen toimesta. Syy: {response.prompt_feedback.block_reason}")
            if hasattr(response.prompt_feedback, 'safety_ratings') and response.prompt_feedback.safety_ratings:
                for rating in response.prompt_feedback.safety_ratings:
                    print(f"  Kategoria: {rating.category}, Todennäköisyys: {rating.probability}")
            return None, None

        full_markdown_content = ""
        if hasattr(response, 'parts') and response.parts:
             full_markdown_content = "".join(part.text for part in response.parts if hasattr(part, 'text'))
        elif hasattr(response, 'text'):
            full_markdown_content = response.text
        else:
            print("Vastauksesta ei löytynyt tekstisisältöä.")
            return None, None

        if not full_markdown_content:
            print("LLM ei tuottanut sisältöä.")
            return None, None

        article_content_for_pdf = full_markdown_content
        lines = full_markdown_content.splitlines()
        last_reference_line_index = -1
        
        references_section_started_at = -1
        ref_header_pattern_fi = r"^\s*##\s+Lähdeluettelo\s*$"
        ref_header_pattern_en = r"^\s*##\s+References\s*$"

        for i, line_text in enumerate(lines):
            stripped_line = line_text.strip()
            if re.match(ref_header_pattern_fi, stripped_line, re.IGNORECASE) or \
               re.match(ref_header_pattern_en, stripped_line, re.IGNORECASE):
                references_section_started_at = i
                break
        
        if references_section_started_at != -1:
            for i in range(len(lines) - 1, references_section_started_at, -1):
                if ("[Arvio:" in lines[i] or "[Assessment:" in lines[i]) and \
                   not (re.match(ref_header_pattern_fi, lines[i].strip(), re.IGNORECASE) or \
                        re.match(ref_header_pattern_en, lines[i].strip(), re.IGNORECASE)):
                    last_reference_line_index = i
                    break
            if last_reference_line_index != -1:
                article_content_for_pdf = "\n".join(lines[:last_reference_line_index + 1])
                print(f"DEBUG: Leikattu artikkelin sisältö PDF:ää varten päättymään riville {last_reference_line_index + 1} (viimeinen arvioitu viite).")
            else:
                next_h2_after_references = -1
                for i in range(references_section_started_at + 1, len(lines)):
                    stripped_line = lines[i].strip()
                    if stripped_line.startswith("## ") and \
                       not (re.match(ref_header_pattern_fi, stripped_line, re.IGNORECASE) or \
                            re.match(ref_header_pattern_en, stripped_line, re.IGNORECASE)):
                        next_h2_after_references = i
                        break
                if next_h2_after_references != -1:
                    article_content_for_pdf = "\n".join(lines[:next_h2_after_references])
                    print(f"DEBUG: Leikattu artikkelin sisältö PDF:ää varten päättymään ennen seuraavaa H2-otsikkoa rivillä {next_h2_after_references}.")
                else:
                    article_content_for_pdf = "\n".join(lines)
                    print("DEBUG: Lähdeluettelo-osio löytyi, mutta ei arviointitageja tai seuraavaa H2-otsikkoa. Käytetään koko loppuosaa PDF:ään.")
        else:
            print("DEBUG: '## Lähdeluettelo' tai '## References' -otsikkoa ei löytynyt. Käytetään koko LLM:n tuotosta PDF:ään varoen.")

        references_with_llm_assessment = []
        raw_references = extract_references_from_markdown_v2(full_markdown_content)

        for ref_text in raw_references:
            assessment_text = "Ei arviota"
            cleaned_ref = ref_text
            match_fi = re.search(r"\[Arvio:\s*(.+?)\]", ref_text)
            match_en = re.search(r"\[Assessment:\s*(.+?)\]", ref_text)
            
            actual_match = None
            if match_fi: actual_match = match_fi
            elif match_en: actual_match = match_en

            if actual_match:
                assessment_text = actual_match.group(1).strip()
                cleaned_ref = re.sub(r"\s*\[(?:Arvio|Assessment):\s*.+?\]\s*$", "", ref_text).strip()
            
            references_with_llm_assessment.append({"reference": cleaned_ref, "llm_assessment": assessment_text})

        return article_content_for_pdf.strip(), references_with_llm_assessment

    except Exception as e:
        print(f"Google API virhe generate_article_markdown_google_v2:ssa: {e}")
        return None, None

def extract_references_from_markdown_v2(markdown_content: str) -> list[str]:
    references = []
    in_references_section = False
    ref_header_pattern_fi = r"^\s*##\s+Lähdeluettelo\s*$"
    ref_header_pattern_en = r"^\s*##\s+References\s*$"
    lines = markdown_content.splitlines()
    for i, line_content in enumerate(lines):
        stripped_line_for_header_check = line_content.strip()
        is_ref_header = False
        if re.match(ref_header_pattern_fi, stripped_line_for_header_check, re.IGNORECASE) or \
           re.match(ref_header_pattern_en, stripped_line_for_header_check, re.IGNORECASE):
            is_ref_header = True
        if is_ref_header:
            in_references_section = True
            continue
        if in_references_section:
            is_next_h2_not_ref_header = False
            if stripped_line_for_header_check.startswith("## ") and \
               not (re.match(ref_header_pattern_fi, stripped_line_for_header_check, re.IGNORECASE) or \
                    re.match(ref_header_pattern_en, stripped_line_for_header_check, re.IGNORECASE)):
                is_next_h2_not_ref_header = True
            if is_next_h2_not_ref_header:
                in_references_section = False
                break
            stripped_line = line_content.strip()
            if stripped_line:
                references.append(stripped_line)
    if not references:
        print("DEBUG extract_references_from_markdown_v2: Ei löytänyt viitteitä.")
    return references

# TÄMÄ ON NYT MUKANA
def convert_md_to_pdf(markdown_content: str, output_filename_base: str) -> tuple[str | None, str | None]:
    md_filename = f"{output_filename_base}.md"
    pdf_filename = f"{output_filename_base}.pdf"
    try:
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"Markdown tallennettu tiedostoon: {md_filename}")
        print("Yritetään PDF-muunnosta Pandocin oletusasetuksilla...")
        pypandoc.convert_file(
            md_filename,
            'pdf',
            outputfile=pdf_filename
        )
        print(f"PDF generoitu tiedostoon: {pdf_filename}")
        return md_filename, pdf_filename
    except FileNotFoundError:
        print("Virhe: Pandoc-ohjelmaa ei löytynyt. Varmista, että se on asennettu ja PATH-muuttujassa.")
        print("Lataa Pandoc: https://pandoc.org/installing.html")
        if os.path.exists(md_filename): return md_filename, None
        return None, None
    except Exception as e:
        print(f"Virhe PDF-muunnoksessa: {e}")
        if os.path.exists(md_filename): return md_filename, None
        return None, None

def main():
    print("--- Tieteellisen artikkelin generaattori v2.6 (Monikielinen, Google Gemini & APA-tyyli) ---") # Versionumero päivitetty
    topic = input("Anna artikkelin aihe (ohjelma käyttää tämän kieltä): ")
    if not topic:
        print("Aihetta ei annettu. Lopetetaan.")
        return

    markdown_for_pdf, llm_assessed_references = generate_article_markdown_google_v2(topic)

    if not markdown_for_pdf:
        print("Artikkelin generointi epäonnistui (ei sisältöä LLM:ltä).")
        return

    safe_topic_str = re.sub(r'[^\w\s-]', '', topic.lower())
    safe_topic_str = re.sub(r'[-\s]+', '-', safe_topic_str).strip('-_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    lang_indicator = "unk"
    topic_lower_main = topic.lower()
    # Parempi kielen tunnistuslogiikka tiedostonimeen (otettu generate-funktiosta)
    is_finnish_main = any(char in topic_lower_main for char in ['ä', 'ö']) or " ja " in topic_lower_main
    is_english_main = any(word in topic_lower_main.split() for word in ["the", "and", "of", "in", "for", "on"])

    if is_finnish_main and not is_english_main: lang_indicator = "fi"
    elif is_english_main: lang_indicator = "en"
    
    filename_base = f"artikkeli_{lang_indicator}_{safe_topic_str[:20]}_{timestamp}"

    md_file, pdf_file = convert_md_to_pdf(markdown_for_pdf, filename_base) # Tämä kutsu on nyt ok

    if md_file:
        print(f"\n--- Lähdeviitteiden tarkistus (LLM:n arvio) ---")
        if llm_assessed_references:
            print("LLM:n generoimat ja arvioimat lähdeviitteet (nämä EIVÄT OLE PDF:ssä, vain konsolitulosteessa):")
            potential_hallucinations_count = 0
            total_references_by_llm = len(llm_assessed_references)

            for i, item in enumerate(llm_assessed_references):
                ref = item["reference"]
                assessment = item["llm_assessment"]
                print(f"{i+1}. {ref}\n   LLM:n arvio: {assessment}")

                assessment_lower = assessment.lower()
                is_hallucination_by_llm = "kuvitteellinen" in assessment_lower or "fictional" in assessment_lower
                is_uncertain_by_llm = "epävarma" in assessment_lower or "uncertain" in assessment_lower or \
                                      "mahdollisesti generoitu" in assessment_lower or "possibly generated" in assessment_lower

                if is_hallucination_by_llm or is_uncertain_by_llm:
                    potential_hallucinations_count += 1
            
            if total_references_by_llm > 0:
                print(f"\nLLM:n arvion perusteella {potential_hallucinations_count}/{total_references_by_llm} viitettä voisi olla potentiaalisia hallusinaatioita tai epävarmoja.")
            else:
                print("\nLLM ei tuottanut analysoitavia viitteitä tai niitä ei voitu purkaa.")
            print("HUOM: Tämä on vain LLM:n oma arvio, eikä takaa viitteiden todellista aitoutta. Manuaalinen tarkistus on edelleen suositeltavaa.")
        else:
            print("Lähdeluetteloa tai LLM:n arvioita ei voitu purkaa automaattisesti LLM:n tuotoksesta.")
            print(f"Tarkista generoitu Markdown-tiedosto ({md_file}) manuaalisesti.")

    if pdf_file:
        print(f"\nValmis! PDF-tiedosto löytyy nimellä: {pdf_file}")
        print("Tarkista PDF ja varmista, että se loppuu lähdeluetteloon.")
    elif md_file:
        print(f"\nPDF-generointi epäonnistui, mutta Markdown-tiedosto löytyy nimellä: {md_file}")
    else:
        print("\nKäsittely epäonnistui, tiedostoja ei luotu.")

if __name__ == "__main__":
    main()