import pandas as pd
from src.parser import load_dataset
from src.analysis import execute_plots


def main():
    PATH_FILE = "data/healthcare_dataset.csv"

    # Load the dataset
    df = load_dataset(PATH_FILE)
    if df.empty:
        print("The Dataset is empty. Please check the file.")
        return

    print("Data Analysis")
    # print(df.columns)
    df.describe(include="all")
    df.info()

    # Plotting
    execute_plots(df)


if __name__ == "__main__":
    main()
