import pandas as pd

# Read CSV and skip metadata line
df = pd.read_csv(
    "customer_behavior.csv",
    encoding="latin1",
    skiprows=1
)

print("Rows before cleaning:", len(df))

# Remove completely empty rows
df = df.dropna(how="all")

# Remove duplicate rows
df = df.drop_duplicates()

# Clean column names
df.columns = df.columns.str.strip()
df.columns = df.columns.str.lower()
df.columns = df.columns.str.replace(" ", "_")

print("Rows after cleaning:", len(df))

# Save cleaned file
df.to_csv("clean_customer_data.csv", index=False)

print("Clean dataset saved.")