#!/usr/bin/env python3
"""Suomen kylät -hakuohjelman rakennusskripti.

Lukee Kansallisarkiston CSV-tiedoston (Suomen kylät 1540-1940), tarkistaa ja
korjaa sen, tekee tiiviin JSON-datan ja upottaa sen HTML-pohjaan yhdessä
Leaflet-karttakirjaston kanssa. Tulos on yksi HTML-tiedosto, joka toimii
selaimessa ilman asennuksia.

Käyttö (Windowsin komentokehotteessa kansiossa C:\\suomen-kylat):
    python tyokalut\\build.py Suomen_kylat_v1.csv

Lisäksi luetaan tyokalut\\pitajankartasto_astia.tsv (Kansallisarkiston Astiasta haettu
pitäjänkartaston karttaluettelo), jonka avulla kylän tietokorttiin tulee suora linkki
oman karttalehden pitäjänkarttaan.

Tuottaa samaan kansioon kuin CSV:
    suomen_kylat_haku.html   – hakuohjelma
    suomen_kylat_v1.json     – aineisto JSON-muodossa (WGS84-koordinaatit lisättynä)

Vaatii vain Pythonin (3.8+) vakiokirjaston.
"""
import base64
import csv
import datetime as dt
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "pohja.html")
LIBDIR = os.path.join(HERE, "lib")

VCOLS = ["v1550", "v1600", "v1650", "v1700", "v1750", "v1800",
         "v1850", "v1900", "v1950", "v2000", "v2023"]

LINK_PATTERNS = {
    "placeid": r"^https?://paikkatiedot\.fi/so/1000772/(\d+)$",
    "wikidata": r"^https?://www\.wikidata\.org/wiki/Q?(\d+)$",
    "ysopaikka": r"^https?://finto\.fi/yso-paikat/fi/page/(p\d+)$",
    "bebyggelsenamn": r"^https?://bebyggelsenamn\.sls\.fi/bebyggelsenamn/(.+)$",
    "heraldica": r"^https?://heraldica\.narc\.fi/toimija\.html\?id=(\d+)$",
    "df": r"^https?://df\.narc\.fi/place/(\d+)$",
}
LINK_BASE = {
    "placeid": "http://paikkatiedot.fi/so/1000772/{}",
    "wikidata": "https://www.wikidata.org/wiki/Q{}",
    "ysopaikka": "https://finto.fi/yso-paikat/fi/page/{}",
    "bebyggelsenamn": "https://bebyggelsenamn.sls.fi/bebyggelsenamn/{}",
    "heraldica": "https://heraldica.narc.fi/toimija.html?id={}",
    "df": "https://df.narc.fi/place/{}",
}


# ---------------------------------------------------------------------------
# ETRS-TM35FIN -> ETRS89 maantieteelliset (JHS 154, Krügerin sarjat)
# ---------------------------------------------------------------------------
def tm35_to_latlon(x, y):
    a = 6378137.0
    f = 1 / 298.257222101
    k0, lon0, fe = 0.9996, math.radians(27.0), 500000.0
    n = f / (2 - f)
    a1 = a / (1 + n) * (1 + n ** 2 / 4 + n ** 4 / 64)
    e = math.sqrt(2 * f - f * f)
    h = [n / 2 - 2 / 3 * n ** 2 + 37 / 96 * n ** 3 - 1 / 360 * n ** 4,
         1 / 48 * n ** 2 + 1 / 15 * n ** 3 - 437 / 1440 * n ** 4,
         17 / 480 * n ** 3 - 37 / 840 * n ** 4,
         4397 / 161280 * n ** 4]
    zeta = y / (a1 * k0)
    eta = (x - fe) / (a1 * k0)
    zp, ep = zeta, eta
    for i, hi in enumerate(h, start=1):
        zp -= hi * math.sin(2 * i * zeta) * math.cosh(2 * i * eta)
        ep -= hi * math.cos(2 * i * zeta) * math.sinh(2 * i * eta)
    beta = math.asin(math.sin(zp) / math.cosh(ep))
    l = math.asin(math.tanh(ep) / math.cos(beta))
    q = math.asinh(math.tan(beta))
    qp = q + e * math.atanh(e * math.tanh(q))
    for _ in range(6):
        qp = q + e * math.atanh(e * math.tanh(qp))
    lat = math.degrees(math.atan(math.sinh(qp)))
    lon = math.degrees(lon0 + l)
    return lat, lon


def load_pitajankartasto(path):
    """Lukee Astiasta haetun pitäjänkartaston luettelon ja tekee hakemiston
    karttalehti ("1042 11") -> lista karttoja. Palauttaa (kartat, hakemisto) tai None."""
    if not os.path.exists(path):
        return None
    maps, index = [], {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#") or "\t" not in line:
                continue
            title, aid = line.rsplit("\t", 1)
            m = re.match(r"^(\d{4}) (\d{1,2})", title)
            if not m:
                continue
            base = m.group(1)
            if "-/-" in title:
                head = title.split("Ia.")[0] if "Ia." in title else title.split("-/-")[0]
                tail = title.split("-/-")[-1]
                var = re.match(r"^\s*-?\s*(_\d+)?", tail).group(1) or ""
                name = re.sub(r"^\s*-?\s*(?:_\d+)?\s*", "", tail).strip()
            else:
                mm = re.match(r"^([\d +]+?)(_\d+)?\s+([^\d+].*)$", title)
                head, var, name = (mm.group(1), mm.group(2) or "", mm.group(3)) if mm else (title, "", "")
            sheets, cur = [], base
            for part in head.strip().split("+"):
                part = part.strip()
                mm = re.match(r"^(\d{4}) (\d{1,2})", part)
                if mm:
                    cur = mm.group(1)
                    sheets.append("%s %02d" % (cur, int(mm.group(2))))
                else:
                    mm = re.match(r"^(\d{1,2})\b", part)
                    if mm:
                        sheets.append("%s %02d" % (cur, int(mm.group(1))))
            sheets = list(dict.fromkeys(sheets))
            label = "+".join(sheets[:1] + [s[5:] if s[:4] == sheets[0][:4] else s for s in sheets[1:]]) + var
            maps.append([name, label, int(aid)])
            for sh in sheets:
                index.setdefault(sh.replace(" ", ""), []).append(len(maps) - 1)
    return maps, index


def css_with_inline_images(css):
    def repl(m):
        name = m.group(1)
        path = os.path.join(LIBDIR, "images", name)
        if not os.path.exists(path):
            return m.group(0)
        with open(path, "rb") as fh:
            data = base64.b64encode(fh.read()).decode("ascii")
        return "url(data:image/png;base64,%s)" % data
    return re.sub(r"url\(images/([\w\-.]+)\)", repl, css)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    csv_path = os.path.abspath(sys.argv[1])
    outdir = os.path.dirname(csv_path)
    report = []

    with open(csv_path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))
    report.append("Rivejä luettu: %d" % len(rows))

    parishes = [""]          # indeksi 0 = tyhjä
    pidx = {"": 0}

    def pid(v):
        v = v.strip()
        if v not in pidx:
            pidx[v] = len(parishes)
            parishes.append(v)
        return pidx[v]

    compact, full = [], []
    fixes, bad_links = 0, 0
    no_coords = 0
    for r in rows:
        rid = int(r["id"])
        x = int(float(r["x"])) if r["x"].strip() else None
        y = int(float(r["y"])) if r["y"].strip() else None
        if x is None or y is None:
            no_coords += 1
            x = y = None
        start = int(r["start"]) if r["start"].strip() else None
        end = int(r["end"]) if r["end"].strip() else None

        links = {}
        for key, pat in LINK_PATTERNS.items():
            val = r.get(key, "").strip()
            if not val:
                links[key] = ""
                continue
            m = re.match(pat, val)
            if not m:
                bad_links += 1
                report.append("Tunnistamaton linkki (id %d, %s): %s" % (rid, key, val))
                links[key] = ""
                continue
            if key == "wikidata" and "/Q" not in val:
                fixes += 1
                report.append("Korjattu Wikidata-linkki (id %d): %s -> Q%s" % (rid, val, m.group(1)))
            links[key] = m.group(1)

        nimi = r["nimi"].strip()
        nimi2 = r["nimi_2"].strip()
        muut = r["nimi_muu"].strip()
        vals = [r[c].strip() for c in VCOLS]

        compact.append([
            rid, x, y, nimi, "" if nimi2 == nimi else nimi2, muut, start, end,
            [pid(v) for v in vals],
            r["rekisteritunnus"].strip(), pid(r["rekisterikunta2013"]),
            r["rekisterikyla2013"].strip(),
            links["placeid"], links["wikidata"], links["ysopaikka"],
            links["bebyggelsenamn"], links["heraldica"], links["df"],
            r["asutus1560luv"].strip(),
            int(r["maara"]) if r["maara"].strip() else 0,
        ])

        rec = {
            "id": rid, "nimi": nimi, "nimi_2": nimi2,
            "nimi_muu": [s.strip() for s in muut.split(";") if s.strip()],
            "start": start, "end": end,
            "pitajat": {c[1:]: v for c, v in zip(VCOLS, vals) if v},
            "rekisteritunnus": r["rekisteritunnus"].strip(),
            "rekisterikunta2013": r["rekisterikunta2013"].strip(),
            "rekisterikyla2013": r["rekisterikyla2013"].strip(),
            "asutus1560luv": r["asutus1560luv"].strip(),
            "maara": int(r["maara"]) if r["maara"].strip() else 0,
            "etrs_tm35fin": {"x": x, "y": y} if x is not None else None,
            "wgs84": None,
            "linkit": {},
        }
        if x is not None:
            lat, lon = tm35_to_latlon(x, y)
            rec["wgs84"] = {"lat": round(lat, 6), "lon": round(lon, 6)}
            rec["linkit"]["karttapaikka"] = (
                "https://asiointi.maanmittauslaitos.fi/karttapaikka/?lang=fi&n=%d&e=%d&zoom=10" % (y, x))
        for key, val in links.items():
            if val:
                rec["linkit"][key] = LINK_BASE[key].format(val)
        full.append(rec)

    report.append("Ilman koordinaatteja: %d" % no_coords)
    report.append("Korjattuja linkkejä: %d, hylättyjä linkkejä: %d" % (fixes, bad_links))
    report.append("Eri pitäjä-/kuntamerkintöjä: %d" % (len(parishes) - 1))

    built = dt.date.today()
    meta = {
        "lahde": "Kansallisarkisto: Suomen kylät 1540–1940, versio 1 (20.12.2023)",
        "doi": "https://doi.org/10.5281/zenodo.10408884",
        "lisenssi": "CC BY 4.0",
        "csv": os.path.basename(csv_path),
        "rakennettu": "%d.%d.%d" % (built.day, built.month, built.year),
        "rivit": len(rows),
    }

    # Erillinen JSON muuta käyttöä varten
    json_path = os.path.join(outdir, "suomen_kylat_v1.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump({"tiedot": meta, "kylat": full}, fh, ensure_ascii=False, indent=1)

    # Pitäjänkartaston karttalehtien Astia-linkit (tyokalut/pitajankartasto_astia.tsv)
    pk = load_pitajankartasto(os.path.join(HERE, "pitajankartasto_astia.tsv"))
    if pk:
        report.append("Pitäjänkartaston karttoja: %d, karttalehtiä: %d" % (len(pk[0]), len(pk[1])))
    else:
        report.append("Pitäjänkartaston luetteloa ei löytynyt – Astia-linkit jäävät pois")

    # Tiivis data ohjelmaan
    data = {"meta": meta, "p": parishes, "r": compact}
    if pk:
        data["pk"] = {"m": pk[0], "k": pk[1]}
    data_js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    with open(TEMPLATE, encoding="utf-8") as fh:
        html = fh.read()
    with open(os.path.join(LIBDIR, "leaflet.js"), encoding="utf-8") as fh:
        leaflet_js = fh.read()
    with open(os.path.join(LIBDIR, "leaflet.css"), encoding="utf-8") as fh:
        leaflet_css = css_with_inline_images(fh.read())

    for ph, val in (("/*__LEAFLET_CSS__*/", leaflet_css),
                    ("/*__LEAFLET_JS__*/", leaflet_js),
                    ("/*__DATA__*/", data_js)):
        if ph not in html:
            raise SystemExit("Pohjasta puuttuu paikka " + ph)
        html = html.replace(ph, val, 1)

    html_path = os.path.join(outdir, "suomen_kylat_haku.html")
    with open(html_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)

    report.append("Kirjoitettu: %s (%d kt)" % (html_path, os.path.getsize(html_path) // 1024))
    report.append("Kirjoitettu: %s (%d kt)" % (json_path, os.path.getsize(json_path) // 1024))
    print("\n".join(report))


if __name__ == "__main__":
    main()
