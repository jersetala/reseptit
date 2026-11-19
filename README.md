# reseptit

- Sovelluksessa käyttäjät pystyvät jakamaan ruokareseptejään. Reseptissä lukee tarvittavat ainekset ja valmistusohje.
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään reseptejä ja muokkaamaan ja poistamaan niitä.
- Käyttäjä näkee sovellukseen lisätyt reseptit.
- Käyttäjä pystyy etsimään reseptejä hakusanalla.
- Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt ja listan käyttäjän lisäämistä resepteistä.
- Käyttäjä pystyy valitsemaan esimerkiksi seuraavia luokitteluja:
        Ruoan tyyppi: alkuruoka, pääruoka tai jälkiruoka
        Ruokavalio: laktoositon, gluteeniton tai vegaaninen
- Käyttäjä pystyy antamaan reseptille kommentin ja joko positiivisen tai negatiivisen arvosanan. Reseptistä näytetään kommentit ja postitiivisten ja negatiivisten arvosanojen erotus.
- Kommenteille voi myös antaa samanlaisen arvosanan.

## Mikä tällä hetkellä toimii?
- Käyttäjä voi luoda tunnuksen ja kirjautumaan sisään.
- Käyttäjä pystyy lisäämään yksinkertaisia puhtaasti tekstipohjaisia reseptejä ja poistamaan niitä. Reseptit ovat käytännössä tekstikenttiä.
- Käyttäjä näkee sovellukseen lisätyt reseptit.
- Käyttäjä pystyy antamaan reseptille kommentin ja joko positiivisen tai negatiivisen arvosanan.
- Kommenteille voi myös antaa samanlaisen arvosanan.
- Käyttäjä pystyy muokkaamaan ja poistamaan luomiaan kohteita.
- Käyttäjä pystyy hakemaan reseptejä otsikon perusteella.

# Sovelluksen käyttö

Ei-juurikäyttäjällä:
``` sh
# Kloonaa repositorio
git clone git@github.com:jersetala/reseptit
cd reseptit
# Luo virtuaaliympäristö ja aktivoi se
python -m venv .venv
source .venv/bin/activate
# Asenna flask
pip install flask
# Luo tietokanta
sqlite3 database.db < schema.sql
# Käynnistä sovellus
flask run
```
