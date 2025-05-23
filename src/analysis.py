import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os

# Ensure plot directory exists
os.makedirs("plots", exist_ok=True)


def execute_plots(df: pd.DataFrame):
    # General category distributions
    category_columns = ["age_group", "gender", "blood_type", "medical_condition"]
    plot_categories(df, category_columns, nrows=2, ncols=2, filename="patient_categories.png")

    # Age distribution
    plot_column_distribution(df, column="age")

    # Field relationships by reference category
    plot_field_relationships(df, "age_group", ["gender", "blood_type", "medical_condition", "billing_category"])

    # Biilling amount relationships
    plot_single_relationship(df, "billing_category", "age_group")
    plot_single_relationship(df, "billing_category", "gender")
    plot_single_relationship(df, "billing_category", "medical_condition")
    plot_single_relationship(df, "billing_category", "length_stay_group")

    plot_single_relationship(df, "hospital", "billing_category")


def plot_column_distribution(df: pd.DataFrame, column: str):
    plt.figure(figsize=(10, 6))
    sns.histplot(df[column], bins=30, kde=True)
    plt.title(f"Distribution of {column.title()}")
    plt.xlabel(column.title())
    plt.ylabel("Frequency")
    plt.savefig(f"plots/{column}_distribution.png")
    plt.close()


def plot_categories(df: pd.DataFrame, columns: list, nrows: int, ncols: int, filename: str):
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(18, 12))
    axes = axes.flatten()

    for i, column in enumerate(columns):
        if i >= len(axes):
            break
        value_counts = df[column].value_counts()
        axes[i].pie(value_counts, labels=value_counts.index, autopct="%1.1f%%", startangle=90)
        axes[i].set_title(f"Distribution of {column.replace('_', ' ').title()}", fontsize=12)
        axes[i].axis("equal")

    plt.tight_layout()
    plt.savefig(f"plots/{filename}")
    plt.close()


def plot_field_relationships(df: pd.DataFrame, base_field: str, compare_fields: list):
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)
    fig.suptitle(f"{base_field.replace('_', ' ').title()} Relationships", fontsize=16)

    for i, field in enumerate(compare_fields):
        row, col = divmod(i, 2)
        sns.countplot(data=df, x=base_field, hue=field, ax=axes[row, col])
        axes[row, col].set_title(f"{base_field.replace('_', ' ').title()} vs {field.replace('_', ' ').title()}")
        axes[row, col].set_xlabel(base_field.replace("_", " ").title())
        axes[row, col].set_ylabel("Count")
        axes[row, col].tick_params(axis="x", rotation=45)

    plt.savefig(f"plots/{base_field}_relationships.png")
    plt.close()


def plot_single_relationship(df: pd.DataFrame, field: str, hue: str):
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x=field, hue=hue)
    plt.title(f"{field} vs {hue}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"plots/{field}_vs_{hue}.png")
    plt.clf()
