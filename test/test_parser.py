import unittest
import pandas as pd
from io import StringIO
from src.parser import load_dataset, initial_cleaning, validate_data


class TestHospitalDataProcessing(unittest.TestCase):
    def setUp(self):
        self.csv_data = StringIO(
            """name,age,gender,blood_type,medical_condition,date_of_admission,doctor,hospital,insurance_provider,billing_amount,room_number,admission_type,discharge_date,medication,test_results
        Dr. John Doe,35,male,A+,flu,2023-01-01,Dr. Jane Smith,"General Hospital",Insurance Co,25000.50,101,Emergency,2023-01-10,Paracetamol,Positive
        Mrs. Alice Johnson,28,FEMALE,o-,diabetes,2023-02-15,Dr. House,"Clinic, Ltd",Health Corp,15000,102,Elective,2023-02-25,Insulin,Negative
        """
        )
        # Asegurar normalización similar a load_dataset
        df = pd.read_csv(
            self.csv_data,
            dtype={
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
            },
        )
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        self.cleaned_df = initial_cleaning(df)
        self.validated_df = validate_data(self.cleaned_df)

    def test_initial_cleaning_standardizes_names(self):
        cleaned_names = list(self.cleaned_df["name"].values)
        self.assertTrue(any("John Doe" in name for name in cleaned_names))
        self.assertTrue(any("Jane Smith" in doc for doc in self.cleaned_df["doctor"].values))

    def test_initial_cleaning_gender_title_case(self):
        self.assertTrue(all(g in ["Male", "Female"] for g in self.cleaned_df["gender"]))

    def test_initial_cleaning_blood_type_upper(self):
        self.assertTrue(all(bt in ["A+", "O-"] for bt in self.cleaned_df["blood_type"]))

    def test_date_conversion(self):
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.cleaned_df["date_of_admission"]))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.cleaned_df["discharge_date"]))

    def test_length_of_stay_calculated(self):
        self.assertIn("length_stay", self.cleaned_df.columns)
        self.assertTrue((self.cleaned_df["length_stay"] == 9).any())

    def test_age_group_created(self):
        self.assertIn("age_group", self.cleaned_df.columns)
        self.assertTrue(self.cleaned_df["age_group"].notnull().all())

    def test_validate_data_filters_out_of_range(self):
        invalid_data = self.cleaned_df.copy()
        invalid_data.loc[0, "age"] = 150
        result = validate_data(invalid_data)
        self.assertNotIn(150, result["age"].values)

    def test_billing_amount_filter(self):
        invalid_data = self.cleaned_df.copy()
        invalid_data.loc[0, "billing_amount"] = -1000
        result = validate_data(invalid_data)
        self.assertTrue((result["billing_amount"] >= 0).all())

    def test_gender_validation(self):
        invalid_data = self.cleaned_df.copy()
        invalid_data.loc[0, "gender"] = "Unknown"
        result = validate_data(invalid_data)
        self.assertNotIn("Unknown", result["gender"].values)

    def test_blood_type_validation(self):
        invalid_data = self.cleaned_df.copy()
        invalid_data.loc[0, "blood_type"] = "X+"
        result = validate_data(invalid_data)
        self.assertNotIn("X+", result["blood_type"].values)


if __name__ == "__main__":
    unittest.main()
