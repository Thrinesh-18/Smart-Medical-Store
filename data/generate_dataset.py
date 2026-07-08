from __future__ import annotations

import json
import random
import sqlite3
from pathlib import Path

import pandas as pd

random.seed(42)

BASE_MEDICINES = [
    ("Paracetamol", "Paracetamol", "Acetaminophen 500mg", ["fever", "headache", "body pain"], "Analgesic", ["Crocin", "Dolo", "Calpol"]),
    ("Ibuprofen", "Ibuprofen", "Ibuprofen 400mg", ["pain", "inflammation", "fever"], "NSAID", ["Brufen", "Ibugesic", "Advil"]),
    ("Azithromycin", "Azithromycin", "Azithromycin 500mg", ["bacterial infection", "throat infection", "ear infection"], "Antibiotic", ["Azee", "Azax", "Zithromax"]),
    ("Cetirizine", "Cetirizine", "Cetirizine 10mg", ["allergy", "cold", "runny nose"], "Antihistamine", ["Cetzine", "Okacet", "Alerid"]),
    ("Omeprazole", "Omeprazole", "Omeprazole 20mg", ["acidity", "heartburn", "gastric reflux"], "Gastrointestinal", ["Omez", "Prilosec", "Ocid"]),
    ("Amoxicillin", "Amoxicillin", "Amoxicillin 500mg", ["bacterial infection", "sinus infection", "bronchitis"], "Antibiotic", ["Mox", "Amoxil", "Novamox"]),
    ("Metformin", "Metformin", "Metformin 500mg", ["type 2 diabetes", "high blood sugar"], "Antidiabetic", ["Glycomet", "Gluformin", "Obimet"]),
    ("Losartan", "Losartan", "Losartan 50mg", ["high blood pressure", "hypertension"], "Cardiovascular", ["Losar", "Repace", "Angizaar"]),
    ("Atorvastatin", "Atorvastatin", "Atorvastatin 10mg", ["high cholesterol", "dyslipidemia"], "Cardiovascular", ["Atorlip", "Lipitor", "Storvas"]),
    ("Pantoprazole", "Pantoprazole", "Pantoprazole 40mg", ["acidity", "ulcer", "heartburn"], "Gastrointestinal", ["Pantocid", "Pan", "Protonix"]),
]

FORMS = ["tablet", "capsule", "syrup", "injection"]
MANUFACTURERS = ["Sun Pharma", "Cipla", "Dr Reddy's", "Mankind", "Lupin", "Zydus", "Glenmark", "Abbott"]
STOCK_STATUS = ["in_stock", "low_stock", "out_of_stock"]
SIDE_EFFECTS = [
    "nausea",
    "dizziness",
    "dry mouth",
    "constipation",
    "stomach upset",
    "rash",
    "drowsiness",
]


def generate_records(total: int = 600) -> list[dict]:
    records = []
    for i in range(1, total + 1):
        base = BASE_MEDICINES[(i - 1) % len(BASE_MEDICINES)]
        med_name, generic, composition, symptoms, category, aliases = base
        strength = random.choice([250, 500, 650])
        form = random.choice(FORMS)
        manufacturer = random.choice(MANUFACTURERS)
        price = round(random.uniform(15, 450), 2)
        prescription_required = category in {"Antibiotic", "Cardiovascular", "Antidiabetic"}
        stock_status = random.choices(STOCK_STATUS, weights=[0.7, 0.2, 0.1])[0]
        keyword_list = [generic.lower(), category.lower(), *[s.lower() for s in symptoms], form, "medicine", "pharmacy"]

        records.append(
            {
                "medicine_id": i,
                "medicine_name": f"{med_name} {strength}",
                "generic_name": generic,
                "composition": composition.replace("500", str(strength)),
                "symptoms": symptoms,
                "uses": f"Used for {', '.join(symptoms)}.",
                "dosage_form": form,
                "category": category,
                "prescription_required": prescription_required,
                "manufacturer": manufacturer,
                "side_effects": random.sample(SIDE_EFFECTS, k=3),
                "price": price,
                "stock_status": stock_status,
                "keywords": keyword_list,
                "aliases": aliases,
            }
        )
    return records


def save_outputs(records: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "medicines.json"
    csv_path = out_dir / "medicines.csv"
    db_path = out_dir / "medical_store.db"

    json_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False)

    conn = sqlite3.connect(db_path)
    db_df = df.copy()
    for column in ["symptoms", "side_effects", "keywords", "aliases"]:
        db_df[column] = db_df[column].apply(json.dumps)
    db_df.to_sql("medicines", conn, if_exists="replace", index=False)
    conn.close()


if __name__ == "__main__":
    directory = Path(__file__).resolve().parent
    data = generate_records(600)
    save_outputs(data, directory)
    print(f"Generated {len(data)} medicine records.")
