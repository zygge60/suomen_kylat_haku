# Suomen kylät 1540–1940 – kylähaku sukututkijoille

**Versio 1.0**

Selaimessa toimiva hakuohjelma Kansallisarkiston paikkatietoaineistoon *Suomen kylät 1540–1940*. Aineistossa on Suomen vanhat maakirjakylät voudintileistä 1900-luvulle, yhteensä 14 172 kylää. Ohjelmalla voi etsiä kyliä eri tavoin, katsoa kylän pitäjähistorian, avata kylän linkit muihin palveluihin ja kopioida kylän koordinaatit eri sovellusten käyttämissä muodoissa.

Ohjelma on yksi HTML-tiedosto, jonka sisällä ovat aineisto ja karttakirjasto. Asennuksia tai palvelinta ei tarvita.

## Käyttö

1. Lataa tiedosto `index.html` (tai koko kansio).
2. Avaa se tuplaklikkaamalla. Ohjelma aukeaa selaimessa (Chrome, Edge tai Firefox).

Tai voit avata ohjelman verkosta osoitteesta:
https://zygge60.github.io/suomen_kylat_haku/

Haku toimii ilman verkkoyhteyttä. Taustakartat ja ulkoiset linkit tarvitsevat verkon. Tarkempi käyttöohje on tiedostossa `docs/Suomen_kylat_haku_kayttoohje.pdf` ja ohjelman Ohje-sivulla.

## Ominaisuudet

**Haku**
- Pikahaku kylän nykyisellä nimellä, vanhalla kirjoitusasulla ja muilla nimimuodoilla. Samaan kenttään voi kirjoittaa myös pitäjän, rekisteritunnuksen tai koordinaatit.
- Nimihaun tavat: sisältää, alkaa, täsmälleen, jokerimerkit (`*`, `?`) ja sumea haku. Sumea haku sallii vanhoille lähteille tyypilliset kirjoitusvaihtelut (w/v, c/k, th/t, kaksoiskirjaimet, -inen/-is, -lax/-la).
- Pitäjä tai kunta valittuna ajankohtana (1550–2023). Haku löytää myös kappelit ja pitäjänosat.
- Aikahaku (kylä olemassa vuonna tai aikavälillä) ja tila (edelleen kylä, lakannut, luovutettu alue 1944).
- Rekisteritunnus, rekisterikunta ja -kylä, *Suomen asutus 1560-luvulla* -viite ja aineiston tunniste.
- Kylät valitun pisteen ympäriltä (1–300 km) tai kartan näkyvältä alueelta.
- Lähimmät kylät liitetyistä koordinaateista.
- Kaikki ehdot voi yhdistää. Haku tallentuu osoiteriville, joten sen voi tallentaa kirjanmerkiksi.

**Kylän tietokortti**
- Nimimuodot ja pitäjä tai kunta eri aikoina aikajanana (epävarmat merkinnät näkyvät erikseen).
- Varhaisin lähdemaininta, arvioitu lakkaaminen, rekisteritunnus ja muut tunnisteet.
- Linkit uuteen välilehteen: MML:n Nimistö ja Karttapaikka, Wikidata, YSO-paikat, Bebyggelsenamn, Heraldica, Diplomatarium Fennicum, OpenStreetMap, Google Maps ja Paikkatietoikkuna.
- **Pitäjänkartasto:** kylän vanhan peruskarttalehden numero (yleislehtijako) ja suora linkki saman lehden pitäjänkarttaan Kansallisarkiston Astiassa.
- Koordinaatit seitsemässä muodossa kopioitaviksi: ETRS-TM35FIN (N, E ja x, y), WGS84 (desimaaliasteet, asteet ja minuutit, asteet–minuutit–sekunnit), ETRS-GK-kaista ja KKJ:n yhtenäiskoordinaatisto (YKJ). Lisäksi näytetään yleislehtijaon lehtinumero.
- Lähimmät kylät etäisyyksineen.

**Kartta ja tallennus**
- Taustakartat: Esrin maasto-, katu- ja ilmakuvakartta, OpenTopoMap sekä Senaatin kartaston aikainen venäläinen topografikartta (1870–1944).
- Kartalta voi valita pisteen ja hakea sen lähimmät kylät.
- Hakutuloksen tallennus CSV- (Excel), KML- (Google Earth), GPX- (GPS-laitteet) ja GeoJSON-muodossa (QGIS).
- Karttanäkymän tallennus PNG-kuvana selitteineen, mittakaavoineen ja lähdetietoineen.

## Kansion sisältö

| Tiedosto | Sisältö |
|---|---|
| `suomen_kylat_haku.html` | Hakuohjelma. Aineisto ja karttakirjasto ovat tiedoston sisällä. |
| `suomen_kylat_v1.json` | Koko aineisto JSON-muodossa, mukana WGS84-koordinaatit ja täydet linkit |
| `Suomen_kylat_v1.csv` | Kansallisarkiston alkuperäinen aineisto (Zenodo) |
| `docs/Suomen_kylat_haku_kayttoohje.pdf` | Käyttöohje |
| `tyokalut/build.py` | Rakennusskripti, joka tekee ohjelman CSV-tiedostosta |
| `tyokalut/pohja.html` | Ohjelman pohja (käyttöliittymä ja ohjelmakoodi) |
| `tyokalut/pitajankartasto_astia.tsv` | Pitäjänkartaston karttaluettelo Astia-tunnisteineen |
| `tyokalut/lib/` | Leaflet 1.9.4 -karttakirjasto ja sen lisenssi |

## Ohjelman päivittäminen uuteen aineistoversioon

Kun Kansallisarkisto julkaisee aineistosta uuden version, tallenna uusi CSV ohjelman kansioon ja aja kansiossa:

```
python tyokalut/build.py Suomen_kylat_v2.csv
```

Skripti vaatii vain Pythonin (3.8 tai uudempi) vakiokirjaston. Se tarkistaa aineiston, korjaa tunnetut linkkivirheet ja kirjoittaa uudet tiedostot `suomen_kylat_haku.html` ja `suomen_kylat_v1.json` CSV:n viereen. Ohjelman käyttöliittymää muutetaan tiedostossa `tyokalut/pohja.html`, ja muutokset tulevat ohjelmaan, kun skripti ajetaan uudelleen.

Pitäjänkartaston luettelo on haettu Astiasta 26.11.2026. Jos Kansallisarkisto lisää karttoja, luettelo pitää hakea uudelleen. Tiedostossa on jokaisesta kartasta Astian arkistoyksikön nimeke ja tunniste (`aineistoId`).

## Tekninen toteutus

- Ohjelma on tavallista HTML:ää ja JavaScriptiä. Karttakirjasto on [Leaflet](https://leafletjs.com/).
- Koordinaattimuunnokset on toteutettu omalla koodilla JHS 154 -suosituksen kaavoilla (Krügerin sarjat). Ne on tarkistettu pyproj-kirjastoa vastaan 204 pisteessä, ja ero on alle millimetrin. KKJ-muunnos tehdään seitsemän parametrin Helmert-muunnoksella (EPSG:n "KKJ to EUREF-FIN (2)"), jonka tarkkuus on noin 1–2 m.
- Yleislehtijaon (vanhan KKJ-peruskarttalehtijaon) lehtinumero lasketaan KKJ:n kaistakoordinaateista. Laskenta on tarkistettu Maanmittauslaitoksen Nimistö-kortteja vastaan. KKJ-kaistojen rajoilla (noin 1,5 % kylistä) MML käyttää levennettyjä reunalehtiä. Niillä ohjelma näyttää lähimmän tavallisen lehden ja tarkistaa pitäjänkartat myös reunalehdeltä.
- Sumea nimihaku normalisoi kirjoitusasun ja vertaa nimiä Levenshteinin etäisyydellä.

## Tunnetut rajoitukset

- Kansallisarkiston mukaan aineiston versio 1 on keskeneräinen. Pitäjätietoja ei ole kaikilta osin tarkistettu.
- 768 kylältä puuttuvat koordinaatit. Ne löytyvät haulla, mutta eivät näy kartalla.
- OpenStreetMapin ja CARTOn karttapalvelimet estävät karttakuvat, kun sivu avataan tiedostosta. Siksi taustakarttoina käytetään Esrin karttoja ja OpenTopoMapia.
- Senaatin kartastosta ei ole avointa väritettyä karttapalvelua. Ohjelmassa on Maanmittauslaitoksen georeferoima mustavalkoinen versio (CSC:n Paituli-palvelu). Se kattaa Lounais-Suomen, Uudenmaan, Kymenlaakson, Hämeen ja Satakunnan, ja se näkyy vasta lähennettäessä noin mittakaavasta 1:140 000 alkaen.
- Selaimet avaavat yleensä vain yhden uuden välilehden napsautusta kohden. Tietokortin *Avaa kaikki* -painike avaa siksi linkit tarvittaessa yksi kerrallaan.

## Lähteet ja lisenssit

- **Kyläaineisto:** Kansallisarkisto, *Suomen kylät 1540–1940*, versio 1 (20.12.2023). CC BY 4.0. https://doi.org/10.5281/zenodo.10408884. Aineistoon on tehty yksi korjaus: Wikidata-linkistä (Hummelkila, Siuntio) puuttui Q-kirjain.
- **Paikannimet:** Maanmittauslaitoksen nimistöaineisto 2023_01, CC BY 4.0 (osana kyläaineistoa).
- **Pitäjänkartaston luettelo:** Kansallisarkiston Astia-palvelu, sarja *Ia.\* Pitäjänkartasto (1749–1917)*.
- **Senaatin kartaston aikaiset kartat:** venäläiset topografiset kartat 1:21 000 ja 1:42 000 © Maanmittauslaitos, jakelu CSC Paituli (CC BY 4.0).
- **Muut taustakartat:** Esri (maasto-, katu- ja ilmakuvakartta), OpenTopoMap (CC BY-SA), © OpenStreetMapin tekijät (ODbL).
- **Karttakirjasto:** Leaflet 1.9.4, BSD 2-Clause -lisenssi (`tyokalut/lib/LEAFLET_LICENSE.txt`).

Kun käytät aineistoa tai ohjelmalla tehtyjä karttakuvia, mainitse lähteet. Ohjelman tallentamissa karttakuvissa lähdetiedot ovat mukana valmiina.

## Tekijä

Jari Aro  
jari.t.aro (at) gmail.com
