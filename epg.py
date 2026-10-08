#!/usr/bin/env python3
"""
L1 MAX EPG automático.
Fuente principal: página oficial de Liga1 Te Apuesto (liga1.pe).
Convierte los horarios publicados (hora de Perú) a XMLTV UTC-5.
"""

import html
import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

SOURCE = "https://liga1.pe/fixture-y-resultados-del-clausura-liga1-te-apuesto-2026/"
TZ = ZoneInfo("America/Lima")
CHANNEL_ID = "l1max.pe"
CHANNEL_NAME = "L1 MAX"
DURATION_MINUTES = 150
OUT = Path("epg.xml")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; L1MAX-EPG/1.0; +https://github.com/)"
}

def clean(value):
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()

def esc(value):
    return (html.escape(value or "", quote=True)
            .replace("&#x27;", "&apos;"))

def parse_datetime(raw, year=2026):
    """
    Acepta formatos de la página oficial como:
    Jueves 08/10 – 13:00
    Viernes 09/10 – 20:00
    """
    raw = clean(raw).replace("–", "-").replace("—", "-")
    m = re.search(r"(\d{1,2})/(\d{1,2})\s*-\s*(\d{1,2}):(\d{2})", raw)
    if not m:
        return None
    day, month, hour, minute = map(int, m.groups())
    return datetime(year, month, day, hour, minute, tzinfo=TZ)

def main():
    r = requests.get(SOURCE, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    programs = []
    seen = set()

    # La página oficial presenta cada fecha en tablas.
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = [clean(td.get_text(" ", strip=True)) for td in tr.find_all(["td", "th"])]
            if len(cells) < 3:
                continue

            # Filas programadas: [fecha/hora, local, vs., visita, estadio]
            dt = parse_datetime(cells[0])
            if not dt:
                continue

            # Normalizamos las posiciones para tolerar pequeñas variaciones.
            local = cells[1]
            visit = cells[3] if len(cells) >= 4 and cells[2].lower() in ("vs.", "vs", "v") else cells[2]
            if not local or not visit:
                continue

            # No usar filas de cabecera.
            if local.lower() in ("local", "fecha") or visit.lower() in ("visita", "estadio"):
                continue

            title = f"{local} vs {visit}"
            key = (dt.isoformat(), title.lower())
            if key in seen:
                continue
            seen.add(key)

            programs.append({
                "start": dt,
                "title": title,
                "desc": f"Liga 1 de Perú - {title}. Transmisión por L1 MAX.",
            })

    # Orden cronológico y solo una ventana razonable.
    programs.sort(key=lambda x: x["start"])
    now = datetime.now(TZ)
    cutoff = now - timedelta(hours=12)
    programs = [p for p in programs if p["start"] + timedelta(minutes=DURATION_MINUTES) >= cutoff]

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<tv generator-info-name="L1 MAX EPG automático" generator-info-url="https://liga1.pe/">',
        f'  <channel id="{CHANNEL_ID}">',
        f'    <display-name lang="es">{CHANNEL_NAME}</display-name>',
        '  </channel>',
    ]

    for p in programs:
        start = p["start"]
        stop = start + timedelta(minutes=DURATION_MINUTES)
        xml += [
            f'  <programme start="{start.strftime("%Y%m%d%H%M%S %z")}" stop="{stop.strftime("%Y%m%d%H%M%S %z")}" channel="{CHANNEL_ID}">',
            f'    <title lang="es">{esc(p["title"])}</title>',
            f'    <desc lang="es">{esc(p["desc"])}</desc>',
            '    <category lang="es">Fútbol</category>',
            '  </programme>',
        ]

    xml.append("</tv>")
    OUT.write_text("\n".join(xml) + "\n", encoding="utf-8")
    print(f"EPG generado: {len(programs)} programas")
    for p in programs[:10]:
        print(p["start"].strftime("%Y-%m-%d %H:%M"), p["title"])

if __name__ == "__main__":
    main()
