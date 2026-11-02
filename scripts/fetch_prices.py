"""Holt aktuelle Filamentpreise aus dem Bambu Lab EU Store und schreibt prices.json.
Läuft täglich über .github/workflows/preise.yml. Bei Fehlern bleibt prices.json unverändert."""
import json, re, sys, urllib.request, datetime

URL = "https://eu.store.bambulab.com/de/collections/bambu-lab-3d-printer-filament/products.json?limit=250&page={}"
# Name in den Stammdaten -> Regel für den Produkttitel im Shop
RULES = {
    "PLA Basic": r"^pla basic$", "PLA Matt": r"^pla mat(t|te)$", "PLA Silk+": r"^pla silk\+?$", "PLA Metall": r"^pla metal",
    "PLA-CF": r"^pla[- ]cf$", "PETG HF": r"^petg hf$", "PETG Translucent": r"^petg translucent$", "PETG-CF": r"^petg[- ]cf$",
    "ABS": r"^abs$", "ASA": r"^asa$", "PC": r"^pc$", "PAHT-CF": r"^paht[- ]cf$", "TPU 95A HF": r"^tpu 95a hf$",
    "TPU 85A/90A": r"^tpu 85a ?/ ?tpu 90a$|^tpu 85a/90a$", "Support for PLA": r"^support for pla", "PVA": r"^pva$",
}

KG = {"Support for PLA": 0.5, "PVA": 0.5}  # Spulengröße, wenn nicht 1 kg


def pick(variants):
    """Günstigste lieferbare Variante – bevorzugt mit Spule (kein Refill) und 1 kg bzw. Standardgröße."""
    vs = [v for v in variants if v.get("available", True) and v.get("price")]
    txt = lambda v: " ".join(str(v.get(k) or "") for k in ("title", "option1", "option2", "option3")).lower()
    spool = [v for v in vs if "refill" not in txt(v) and "nachfüll" not in txt(v)]
    vs = spool or vs
    std = [v for v in vs if not re.search(r"\b(2|3|4|5|6|8|10)\s?(x|stk|rolls?|rollen|pack)\b|bundle|\bset\b", txt(v))]
    vs = std or vs
    return round(min(float(v["price"]) for v in vs), 2) if vs else None


def fetch(page):
    req = urllib.request.Request(URL.format(page), headers={"User-Agent": "Mozilla/5.0 (Preisabgleich Schulungsunterlage)", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("products", [])

def main():
    try:
        products = []
        for page in range(1, 6):
            batch = fetch(page)
            if not batch:
                break
            products += batch
    except Exception as e:  # Shop nicht erreichbar oder Format geändert
        print("Abruf fehlgeschlagen:", e)
        return 0
    data = json.load(open("prices.json", encoding="utf-8"))
    items, changed = data.setdefault("items", {}), False
    for name, rule in RULES.items():
        for p in products:
            if re.search(rule, p.get("title", "").strip().lower()):
                price = pick(p.get("variants", []))
                if not price:
                    continue
                old = items.get(name, {}).get("price")
                if old != price:
                    items.setdefault(name, {"kg": KG.get(name, 1)})["price"] = price
                    changed = True
                    print(f"{name}: {old} -> {price}")
                break
    if changed:
        data["updated"] = datetime.date.today().isoformat()
        json.dump(data, open("prices.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        open("prices.json", "a", encoding="utf-8").write("\n")
    print("geändert" if changed else "keine Änderung", "-", len(products), "Produkte gelesen")
    return 0

if __name__ == "__main__":
    sys.exit(main())
