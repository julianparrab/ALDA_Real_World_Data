import pandas as pd
import re
from typing import Dict, List, Union, Optional

# Define the data types for each column
DTYPES = {
    "name": "category",
    "age": "int64",
    "gender": "category",
    "blood_type": "category",
    "medical_condition": "string",
    "date_of_admission": "category",
    "doctor": "string",
    "hospital": "string",
    "insurance_provider": "string",
    "billing_amount": "float64",
    "room_number": "int64",
    "admission_type": "category",
    "discharge_date": "category",
    "medication": "string",
    "test_results": "category",
}


def load_dataset(filepath):
    # Read the CSV file
    df = pd.read_csv(filepath, dtype=DTYPES)

    # Check if the DataFrame is empty
    if df.empty:
        print("The DataFrame is empty.")
        return df

    # Define patterns for columns
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    print("DataFrame loaded successfully.")
    print("Init:\n", df.head())
    print("Rows:", df.shape[0])

    # Initial cleaning
    df = initial_cleaning(df)
    print("\nInitial cleaning completed.")
    print("Clean:\n", df.head())
    print("Rows:", df.shape[0])

    # Validation Data
    df = validate_data(df)
    print("\nValidation completed.")
    print("Validation:\n", df.head())
    print("Rows:", df.shape[0])

    return df


def initial_cleaning(df):
    """Performs initial cleaning and normalization of a medical records dataframe."""

    # Create a copy to avoid modifying the original
    cleaned_df = df.copy()

    # Delete empty columns
    cleaned_df = cleaned_df.dropna(how="any")

    # 1. Clean and standardize proper names (Patients, Doctors)

    def standardize_name(name):
        if pd.isna(name):
            return name
        # Convert to title case (first letter of each word capitalized)
        name = name.title()
        # Fix special cases like 'McDonald'
        name = re.sub(r"\bMc(\w)", lambda m: "Mc" + m.group(1).upper(), name)
        name = re.sub(r"\bMac(\w)", lambda m: "Mac" + m.group(1).upper(), name)
        name = re.sub(r"\bO\'(\w)", lambda m: "O'" + m.group(1).upper(), name)
        name = re.sub(r"\bD\'(\w)", lambda m: "D'" + m.group(1).upper(), name)

        # Convertir a formato título (primera letra mayúscula, resto minúscula)
        name = name.title()

        # Manejar guiones (ej: María-José -> María-José)
        name = re.sub(r"(\w)-(\w)", lambda m: m.group(1) + "-" + m.group(2).title(), name)
        return name

    # Clean Titles
    titles = r"^(Dr\.|Mr\.|Mrs\.|Ms\.|Prof\.|Dra\.|Sr\.|Sra\.)\s*"
    cleaned_df["name"] = df["name"].str.replace(titles, "", regex=True, flags=re.IGNORECASE)
    cleaned_df["doctor"] = df["doctor"].str.replace(titles, "", regex=True, flags=re.IGNORECASE)

    cleaned_df["name"] = cleaned_df["name"].apply(standardize_name)
    cleaned_df["doctor"] = cleaned_df["doctor"].apply(standardize_name)

    # 2. Clean and standardize hospital names
    def clean_hospital_name(name):
        if pd.isna(name):
            return name
        name = name.strip('"').strip("'").strip()
        # Standardize company suffixes
        name = re.sub(r"\s*,\s*", " & ", name)  # Replace commas with &
        name = name.title()
        return name

    cleaned_df["hospital"] = cleaned_df["hospital"].apply(clean_hospital_name)

    # 3. Standardize gender
    cleaned_df["gender"] = cleaned_df["gender"].str.title()

    # 4. Clean blood types (standard format)
    cleaned_df["blood_type"] = cleaned_df["blood_type"].str.upper()

    # 5. Clean medical conditions (title case)
    cleaned_df["medical_condition"] = cleaned_df["medical_condition"].str.title()

    # 6. Convert dates to datetime objects
    date_cols = ["date_of_admission", "discharge_date"]
    for col in date_cols:
        cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors="coerce")

    # 7. Clean insurance providers (title case)
    cleaned_df["insurance_provider"] = cleaned_df["insurance_provider"].str.title()

    # 8. Round billing amounts to 2 decimal places
    cleaned_df["billing_amount"] = cleaned_df["billing_amount"].round(2)

    # 9. Clean admission type (title case)
    cleaned_df["admission_type"] = cleaned_df["admission_type"].str.title()

    # 10. Clean medications (title case)
    cleaned_df["medication"] = cleaned_df["medication"].str.title()

    # 11. Clean test results (title case)
    cleaned_df["test_results"] = cleaned_df["test_results"].str.title()

    # 12. Add derived columns
    cleaned_df["length_stay"] = (cleaned_df["discharge_date"] - cleaned_df["date_of_admission"]).dt.days

    # 13. Create length_stay groups
    cleaned_df["length_stay_group"] = pd.cut(
        cleaned_df["length_stay"],
        bins=[1, 7, 15, 30, 45, 60, 90],
        labels=["1-7", "8-15", "16-30", "31-45", "46-60", "60+"],
    )

    # 14. Create age groups
    cleaned_df["age_group"] = pd.cut(
        cleaned_df["age"], bins=[0, 18, 30, 45, 60, 75, 100], labels=["0-18", "19-30", "31-45", "46-60", "61-75", "75+"]
    )

    # 15. Create billing amount categories
    bins = [0, 10000, 20000, 30000, 40000, float("inf")]
    labels = ["<10k", "10k-20k", "20k-30k", "30k-40k", "40k+"]
    cleaned_df["billing_category"] = pd.cut(cleaned_df["billing_amount"], bins=bins, labels=labels)

    return cleaned_df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validates and filters data according to specific criteria."""
    # Define valid values for columns
    SEX_VALIDATION = ["Male", "Female"]
    BLOOD_TYPE_VALIDATION = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

    # Filter out invalid values
    df = df[df["age"].between(0, 120)]
    df = df[df["billing_amount"] >= 0]
    df = df[df["room_number"] > 0]
    df = df[df["gender"].isin(SEX_VALIDATION)]
    df = df[df["blood_type"].isin(BLOOD_TYPE_VALIDATION)]
    df = df[df["length_stay"] >= 0]

    return df
