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

