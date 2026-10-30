
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Locate project folders
ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "outputs" / "data_quality_report.csv"
OUTPUT_DIR = ROOT / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

# 1. Load the clinical data quality report
df = pd.read_csv(INPUT_FILE)

# Extract study site from subject ID
df["site_id"] = df["subject_id"].str.rsplit("-", n=1).str[0]

# 2. Summarize issues by type
issue_summary = (
    df["issue"]
    .value_counts()
    .rename_axis("Issue Type")
    .reset_index(name="Number of Flags")
)

# 3. Summarize issues by study site
site_summary = (
    df.groupby(["site_id", "issue"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

# 4. Generate an Excel workbook
excel_path = OUTPUT_DIR / "clinical_quality_report.xlsx"

with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    issue_summary.to_excel(
        writer, sheet_name="Issue Summary", index=False
    )
    site_summary.to_excel(
        writer, sheet_name="Site Summary", index=False
    )
    df.to_excel(
        writer, sheet_name="All Quality Flags", index=False
    )

# 5. Generate a visualization
fig, ax = plt.subplots(figsize=(10, 5))

ax.barh(
    issue_summary["Issue Type"],
    issue_summary["Number of Flags"]
)

ax.set_title("Clinical Trial Data Quality Flags")
ax.set_xlabel("Number of Flags")
ax.invert_yaxis()

plt.tight_layout()

chart_path = OUTPUT_DIR / "quality_flags_chart.png"
plt.savefig(chart_path, dpi=200)
plt.close()

# 6. Display results
print("Clinical Data Reporting Complete!")
print("--------------------------------")
print(f"Total quality flags: {len(df)}")
print(f"Excel report: {excel_path}")
print(f"Visualization: {chart_path}")

