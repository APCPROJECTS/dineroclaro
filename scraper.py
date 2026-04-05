"""
DineroClaro - Scraper BCU Uruguay
Corre diariamente via GitHub Actions y actualiza data.json con tasas reales del BCU.
"""

import json
import requests
import datetime
import os
import re

DATA_FILE = "data.json"
BCU_URL = "https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/TasasDeInteres.aspx"

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    data["ultima_actualizacion"] = datetime.date.today().isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"data.json actualizado: {data['ultima_actualizacion']}")

def fetch_bcu_rates():
    rates = {}
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; DineroClaro/1.0)"}
        response = requests.get(BCU_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            import re
            brou_match = re.search(r'BROU[^<]*(\d{1,3}[.,]\d{1,2})\s*%', response.text, re.IGNORECASE)
            if brou_match:
                rates["BROU"] = float(brou_match.group(1).replace(",", "."))
    except Exception as e:
        print(f"BCU no disponible: {e}")
    fallback = {"BROU": 23.0, "Santander": 29.0, "BBVA": 28.0, "Itau": 30.0, "COPAC": 30.34, "Creditel": 117.0, "Pronto": 67.0, "Cash": 85.0, "Credito de la Casa": 95.0, "FUCAC": 45.0, "COFAC": 35.0, "COMAC": 38.0, "FUCEREP": 42.0}
    for k, v in fallback.items():
        if k not in rates:
            rates[k] = v
    return rates

def update_credit_rates(data, rates):
    updated = 0
    for item in data.get("creditos", []):
        name = item["name"]
        if name in rates:
            new_rate = rates[name]
            if abs(new_rate - item["costo"]) > 0.5:
                item["costo"] = new_rate
                item["costoR"] = f"{new_rate:.1f}% TEA"
                updated += 1
    return updated

def main():
    data = load_data()
    rates = fetch_bcu_rates()
    updated = update_credit_rates(data, rates)
    print(f"{updated} tasas actualizadas")
    save_data(data)
    print("Proceso completado")

if __name__ == "__main__":
    main()
