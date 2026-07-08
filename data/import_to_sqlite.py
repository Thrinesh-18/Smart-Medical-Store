import json
import sqlite3
from pathlib import Path

import pandas as pd


def run():
    base = Path(__file__).resolve().parent
    records = json.loads((base / "medicines.json").read_text(encoding="utf-8"))
    df = pd.DataFrame(records)
    for column in ["symptoms", "side_effects", "keywords", "aliases"]:
        df[column] = df[column].apply(json.dumps)
    conn = sqlite3.connect(base / "medical_store.db")
    df.to_sql("medicines", conn, if_exists="replace", index=False)
    conn.close()
    print("SQLite import completed.")


if __name__ == "__main__":
    run()
