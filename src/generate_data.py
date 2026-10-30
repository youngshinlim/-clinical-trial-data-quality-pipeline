
from pathlib import Path
from datetime import date, timedelta

import numpy as np
import pandas as pd

# Reproducible synthetic data
rng = np.random.default_rng(42)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Illustrative laboratory ranges (not clinical guidance)
LAB_TESTS = {
    "ALT": (7, 56, "U/L"),
    "AST": (10, 40, "U/L"),
    "Creatinine": (0.6, 1.3, "mg/dL"),
    "Glucose": (70, 99, "mg/dL"),
}

VISITS = {
    "Baseline": 0,
    "Day 7": 7,
    "Day 14": 14,
}

records = []

for site_number in range(1, 11):
    site_id = f"SITE-{site_number:03d}"

    for participant in range(1, 21):
        subject_id = f"{site_id}-{participant:03d}"
        start_date = date(2026, 1, 1) + timedelta(
            days=int(rng.integers(0, 60))
        )

        for visit, expected_day in VISITS.items():
            offset = int(rng.integers(-3, 4))
            collection_date = start_date + timedelta(
                days=expected_day + offset
            )

            for test, (low, high, unit) in LAB_TESTS.items():

                # Simulate an occasionally missing lab record
                if rng.random() < 0.04:
                    continue

                result = rng.normal(
                    loc=(low + high) / 2,
                    scale=(high - low) / 6
                )

                # Simulate occasional out-of-range values
                if rng.random() < 0.04:
                    result = high * 1.4

                # Simulate some missing result values
                if rng.random() < 0.02:
                    result = np.nan

                records.append({
                    "study_id": "SYNTHETIC-001",
                    "site_id": site_id,
                    "subject_id": subject_id,
                    "visit": visit,
                    "expected_day": expected_day,
                    "collection_date": collection_date,
                    "lab_test": test,
                    "result": round(float(result), 2),
                    "unit": unit,
                    "reference_low": low,
                    "reference_high": high,
                })

df = pd.DataFrame(records)

# Add duplicate records for future validation testing
duplicates = df.sample(n=6, random_state=42)
df = pd.concat([df, duplicates], ignore_index=True)

output = DATA_DIR / "synthetic_lab_results.csv"
df.to_csv(output, index=False)

print(f"Generated {len(df)} laboratory records.")
print("Sites: 10 | Participants: 200")
print(f"Saved dataset to: {output}")
print(df.head())
