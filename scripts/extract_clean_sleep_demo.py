import os
import pandas as pd

# -----------------------------
# Paths
# -----------------------------
RAW_PATH = os.path.join("data", "raw", "adult24.csv")
CLEAN_PATH = os.path.join("data", "clean", "nhis_sleep_demo_clean.csv")

# -----------------------------
# Variables to select
# -----------------------------
SLEEP_PREFIX = "SLP"
DEMO_VARS = ["SEX_A", "AGEP_A", "EDUCP_A"]

# -----------------------------
# Codes representing invalid responses
# -----------------------------
INVALID_CODES = [7, 8, 9, 97, 98, 99]

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv(RAW_PATH)

# -----------------------------
# Select sleep and demographic variables
# -----------------------------
sleep_vars = [col for col in df.columns if col.startswith(SLEEP_PREFIX)]
selected_vars = sleep_vars + DEMO_VARS
df_selected = df[selected_vars]

# -----------------------------
# Drop rows with invalid codes
# -----------------------------
for col in df_selected.columns:
    df_selected = df_selected[~df_selected[col].isin(INVALID_CODES)]

# -----------------------------
# Save cleaned dataset
# -----------------------------
os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)
df_selected.to_csv(CLEAN_PATH, index=False)

print(f"✅ Cleaned file saved to {CLEAN_PATH} with {df_selected.shape[0]} rows.")
