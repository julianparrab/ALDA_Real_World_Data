import unittest
import pandas as pd
import os
from src.analysis import execute_plots


class TestPlottingFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.DataFrame(
            {
                "age": [25, 35, 45, 60, 75],
                "age_group": ["20-30", "30-40", "40-50", "60-70", "70-80"],
                "gender": ["Male", "Female", "Female", "Male", "Female"],
                "blood_type": ["A+", "O-", "B+", "A-", "AB+"],
                "medical_condition": ["Flu", "Diabetes", "Asthma", "Covid", "Flu"],
                "billing_category": ["Low", "High", "Medium", "High", "Low"],
                "length_stay_group": ["Short", "Long", "Medium", "Long", "Short"],
                "hospital": ["Hospital A", "Hospital B", "Hospital A", "Hospital B", "Hospital C"],
            }
        )

        cls.output_files = [
            "plots/patient_categories.png",
            "plots/age_distribution.png",
            "plots/age_group_relationships.png",
            "plots/billing_category_vs_age_group.png",
            "plots/billing_category_vs_gender.png",
            "plots/billing_category_vs_medical_condition.png",
            "plots/billing_category_vs_length_stay_group.png",
            "plots/hospital_vs_billing_category.png",
        ]

        for f in cls.output_files:
            if os.path.exists(f):
                os.remove(f)

        execute_plots(cls.df)

    def test_plot_files_created(self):
        for file in self.output_files:
            with self.subTest(file=file):
                self.assertTrue(os.path.exists(file), f"{file} no fue creado.")

    def test_plot_directory_exists(self):
        self.assertTrue(os.path.exists("plots"), "El directorio 'plots' no fue creado.")


if __name__ == "__main__":
    unittest.main()
