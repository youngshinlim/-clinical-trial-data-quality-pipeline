
from pathlib import Path
from itertools import product
import pandas as pd

# Locate project folders
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic_lab_results.csv"
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)

# Load synthetic laboratory data
df = pd.read_csv(DATA)

issues = []

# 1. Identify missing laboratory results
for _, row in df[df["result"].isna()].iterrows():
    issues.append({
        "subject_id": row["subject_id"],
        "visit": row["visit"],
        "lab_test": row["lab_test"],
        "issue": "Missing laboratory result"
    })

# 2. Identify results outside reference ranges
abnormal = df[
    df["result"].notna()
    & (
        (df["result"] < df["reference_low"])
        | (df["result"] > df["reference_high"])
    )
]

for _, row in abnormal.iterrows():
    issues.append({
        "subject_id": row["subject_id"],
        "visit": row["visit"],
        "lab_test": row["lab_test"],
        "issue": "Outside reference range"
    })

# 3. Identify duplicate records
keys = ["subject_id", "visit", "lab_test"]

duplicates = df[df.duplicated(subset=keys, keep=False)]
duplicates = duplicates.drop_duplicates(subset=keys)

for _, row in duplicates.iterrows():
    issues.append({
        "subject_id": row["subject_id"],
        "visit": row["visit"],
        "lab_test": row["lab_test"],
        "issue": "Duplicate laboratory record"
    })

# 4. Find expected laboratory records that are absent
visits = ["Baseline", "Day 7", "Day 14"]
tests = ["ALT", "AST", "Creatinine", "Glucose"]

expected = set(product(df["subject_id"].unique(), visits, tests))
observed = set(zip(df["subject_id"], df["visit"], df["lab_test"]))

for subject, visit, test in sorted(expected - observed):
    issues.append({
        "subject_id": subject,
        "visit": visit,
        "lab_test": test,
        "issue": "Expected laboratory record missing"
    })

# 5. Save quality control report
report = pd.DataFrame(
    issues,
    columns=["subject_id", "visit", "lab_test", "issue"]
)

report.to_csv(OUTPUT / "data_quality_report.csv", index=False)

print("Clinical Data Quality Report")
print("----------------------------")
print(f"Total laboratory rows: {len(df)}")
print(f"Total issues identified: {len(report)}")
print()
print(report["issue"].value_counts())
print()
print("Report saved to outputs/data_quality_report.csv")

