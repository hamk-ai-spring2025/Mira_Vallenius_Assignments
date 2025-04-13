# Ohjelman tiivistelmä: Albumiarvosteluapplikaatio

## Yleiskuvaus

Ohjelma on interaktiivinen komentorivisovellus, joka hakee tietoja albumista MusicBrainzin API:n kautta ja generoi albumiarvosteluja OpenAI:n ChatCompletion-rajapinnan avulla. Lopputuloksena saadaan Markdown-muotoisia arvioita, jotka kirjoitetaan tiedostoon ja näytetään käyttäjälle.

## Keskeiset osiot

### 1. Albumin tiedon haku – `fetch_album_info()`

- **Tarkoitus:**  
  Hakea albumin perustiedot (kuten otsikko ja julkaisupäivä) MusicBrainz API:sta.
  
- **Toiminta:**
  - Rakentaa HTTP GET -pyynnön osoitteeseen `http://musicbrainz.org/ws/2/release/` käyttäen parametrina annettua albumin nimeä (query: `release:"{album}"`).
  - Asettaa pyynnön headeriin käyttäjäagentin (esim. `MusicCriticReview/1.0 (example@example.com)`).
  - Jos vastauskoodi on 200, käsittelee JSON-datan ja palauttaa ensimmäisen löytyneen julkaisun tietoja sanakirjassa (`{"title": title, "date": date}`).
  - Jos albumia ei löydy tai tapahtuu virhe, palauttaa `None` ja tulostaa virheilmoituksen.

### 2. Arvostelun generointi – `get_review()`

- **Tarkoitus:**  
  Generoida lyhyt ja ytimekäs albumiarvostelu tietyn tyylin mukaisesti.
  
- **Toiminta:**
  - **System-prompt:**  
    Ohjeistaa mallia toimimaan kokeneen musiikkikriitikon tavoin: terävä, humoristinen, ilkeä mutta myös kykenevä antamaan vilpittömiä kehuja silloin, kun albumi loistaa. Ohjeistus sisältää myös eri julkaisutyylien kuvaukset.
  - **Käyttäjäviesti:**  
    Muodostetaan viesti, jossa pyydetään kirjoittamaan arvostelu annetulle albumille tietyn tyylivaihtoehdon mukaisesti. Arvostelun tulee alkaa tyylin otsikolla (label).
  - **API-kutsu:**  
    OpenAI:n ChatCompletion API kutsutaan seuraavilla asetuksilla:
    - Malli: esim. `gpt-3.5-turbo`
    - Parametrit:
      - `temperature`: esim. 1.2 (tarjoaa luovaa, mutta koherenttia tekstiä)
      - `top_p`: 0.95
      - `frequency_penalty` & `presence_penalty`: asetettu arvoon 1.5, mikä vähentää toistoa ja kannustaa uuteen sisältöön
      - `max_tokens`: 800
  - **Tuloste:**  
    Palauttaa generoitu tekstin, joka sisältää albumiarvostelun.

### 3. Pääohjelma – `main()`

- **Malliasetukset:**
  - Määrittelee käytettävän mallin (`gpt-3.5-turbo`) ja siihen liitettävät asetukset (temperature, top_p, frequency_penalty, presence_penalty, max_tokens).

- **Arvostelutyyli:**  
  Määrittelee kolme eri julkaisutyylin vaihtoehtoa:
  
  1. **Serious/Mainstream:**  
     Yksityiskohtaista analyysiä musiikillisesta näkökulmasta (rakenne, esitys, sanoitukset, tuotanto) yhdistettynä iskevään huumoriin.
  
  2. **Alternative/Indie:**  
     Rentoa ja trenditietoista näkökulmaa, joka painottaa vaihtoehtoisten ja niche-genren estetiikkaa.
  
  3. **Fanzine and Small Press:**  
     Epämuodollista, henkilökohtaista ja intohimoista arvostelua, joka heijastaa underground-henkeä.

- **Tiedoston hallinta:**
  - Alussa luodaan tai tyhjennetään Markdown-tiedosto (`album_reviews.md`).
  - Jokaisesta albumista generoitu Markdown-osio sisältää albumin nimen ja kunkin tyylin mukaiset arvostelut.

- **Käyttäjävuorovaikutus:**
  - Käyttäjältä kysytään albumin nimeä.
  - Jos albumia ei löydy MusicBrainzista, ilmoitetaan siitä ja pyydetään uusi syöte.
  - Jos albumi löytyy, sitä käytetään arvostelujen generointiin kaikilla määritellyillä tyyleillä.
  - Arvostelut näytetään konsolissa ja tallennetaan tiedostoon.
  - Prosessi toistuu niin kauan, kunnes käyttäjä syöttää tyhjän merkkijonon.

## Teknologiat ja API:t

- **Python-kirjastot:**
  - `openai`: Käytetään albumiarvostelujen generointiin ChatCompletion API:n avulla.
  - `requests`: Käytetään HTTP-pyyntöjen tekemiseen MusicBrainz API:lle.

- **API:t:**
  - **MusicBrainz API:**  
    Tarjoaa tietoa musiikki-julkaisuista ja käytetään albumin tietojen hakuun.
  
  - **OpenAI ChatCompletion API:**  
    Generoi albumiarvosteluja system-promptin ja käyttäjäviestin perusteella.

## Yhteenveto

Ohjelman ydinajatus on tuottaa monipuolisia ja tyylillisesti eriytettyjä albumiarvosteluja:

- **Albumin perustiedot** haetaan ulkoisesta tietolähteestä (MusicBrainz).
- **Arvostelut** generoidaan ennalta määriteltyjen tyylien mukaisesti OpenAI:n avulla.
- **Lopputulos** kirjoitetaan Markdown-tiedostoon ja näytetään käyttäjälle.
- **Vuorovaikutteisuus:**  
  Käyttäjä voi generoida arvosteluja useista albumeista, ja ohjelma jatkaa niin kauan, kunnes syöte on tyhjä.


## Lisenssi

Tämä projekti on tarkoitettu opetus- ja harjoitustarkoituksiin. Käytä ja muokkaa vapaasti omiin tarpeisiisi.

Tekijä: Mira Vallenius / Tekoälyosaaja Kevät 2025

Nauti rockkriitikkona olemisesta ja anna rehellisten mielipiteiden virrata!
