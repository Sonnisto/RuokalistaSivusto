# Opiskelijaravintoloiden Ruokalistat - Web-sovellus

Tämä projekti on web-sovellus, joka hakee ja näyttää Turun opiskelijaravintoloiden päivittäiset ruokalistat. Sovellus hyödyntää Flask-backendia tiedonhakuun ja rajapintojen avulla noudetaan reaaliaikaisesti ruokalistoja eri ravintoloilta. Sovelluksessa on myös navigointiominaisuus, jonka avulla käyttäjä voi selata eri viikonpäivien ruokalistoja.

## Ominaisuudet
- **Päivittäiset ruokalistat**: Näyttää päivän ruokalistat useista eri opiskelijaravintoloista Turussa.
- **Reaaliaikainen tietojen haku**: Noutaa tiedot ravintoloiden avoimista JSON-rajapinnoista ja näyttää ne siististi sovelluksessa.
- **Navigointi viikonpäivien välillä**: Käyttäjät voivat selata eri viikonpäivien ruokalistoja.

## Käytetyt Teknologiat
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS
- **API-tietojen haku**: JSON-rajapinnat
- **Ajan käsittely**: `datetime`, `dateutil.parser`

## Sovelluksen Rakenne

- **`app.py`**: Sovelluksen päälogiikka ja reitit, jotka noutavat ja näyttävät ruokalistat.
- **`templates/day.html`**: HTML-pohja päivittäiselle ruokalistalle.
- **`static/css/styles.css`**: CSS-tiedosto, joka määrittelee sovelluksen tyylin.

## Rajapinnat
Sovellus käyttää julkisia JSON-rajapintoja eri opiskelijaravintoloilta. Tietoa haetaan ja käsitellään Pythonin `requests`-kirjastolla, ja käsitellyt ruokalistat näytetään sovelluksessa.

## Käyttöohjeet
1. **Päivän ruokalista**: Sovellus avautuu nykyisen päivän ruokalistaan, ja käyttäjä voi nähdä päivän tarjonnan kaikista ravintoloista.
2. **Navigointi eri päivien välillä**: Navigointipainikkeilla voi selata eteen- ja taaksepäin eri päivien ruokalistoja.

---

Tämä README antaa perustiedot sovelluksen käytöstä, teknologioista ja asennuksesta.
