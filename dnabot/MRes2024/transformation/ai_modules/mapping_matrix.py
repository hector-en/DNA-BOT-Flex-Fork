import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json


def create_mapping_matrix(diffs, experimental_results):
    """
    Create a mapping matrix correlating diffs to experimental results.
    Args:
        diffs (list): List of diff lines (e.g., from code changes).
        experimental_results (pd.DataFrame): Experimental results, including Z-factors and other insights.
    Returns:
        pd.DataFrame: Mapping matrix showing correlations between diffs and experimental results.
    """
    try:
        # Convert diffs into numerical features
        diff_features = {
            f"diff_{i}": len(diff.split()) for i, diff in enumerate(diffs)
        }
        diff_df = pd.DataFrame([diff_features])

        # Combine diff features with experimental results
        mapping_matrix = pd.concat([diff_df, experimental_results], axis=1)

        # Calculate correlations
        mapping_matrix["Z-Factor"] = experimental_results["Z-Factor"]
        mapping_matrix_corr = mapping_matrix.corr()

        return mapping_matrix_corr
    except Exception as e:
        print(f"[ERROR] Failed to create mapping matrix: {e}")
        return pd.DataFrame()


def visualize_mapping_matrix(matrix, output_file="mapping_matrix.png"):
    """
    Visualize the mapping matrix as a heatmap.
    Args:
        matrix: Pandas DataFrame containing the mapping matrix.
        output_file: Path to save the visualization.
    """
    try:
        plt.figure(figsize=(12, 10))
        sns.heatmap(matrix, annot=True, cmap="coolwarm", fmt=".2f", cbar=True)
        plt.title("Correlation Between Diffs and Experimental Results")
        plt.savefig(output_file)
        plt.close()
        print(f"[INFO] Mapping matrix visualization saved to {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to visualize mapping matrix: {e}")


def save_mapping_matrix(matrix, output_file="mapping_matrix.csv"):
    """
    Save the mapping matrix to a CSV file.
    Args:
        matrix: Pandas DataFrame containing the mapping matrix.
        output_file: Path to save the matrix.
    """
    try:
        matrix.to_csv(output_file, index=False)
        print(f"[INFO] Mapping matrix saved to {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to save mapping matrix: {e}")


def extract_important_correlations(mapping_matrix, threshold=0.5):
    """
    Extract and print the most important correlations from the mapping matrix.
    Args:
        mapping_matrix: Pandas DataFrame containing the mapping matrix correlations.
        threshold: Correlation value above which relationships are considered important.
    Returns:
        pd.DataFrame: Important correlations above the threshold.
    """
    try:
        # Extract significant correlations above the threshold
        important_corr = mapping_matrix[
            (mapping_matrix > threshold) | (mapping_matrix < -threshold)
        ]
        important_corr = important_corr.stack().reset_index()
        important_corr.columns = ["Feature 1", "Feature 2", "Correlation"]
        important_corr = important_corr[
            important_corr["Feature 1"] != important_corr["Feature 2"]
        ]  # Exclude self-correlations

        print(f"[INFO] Extracted {len(important_corr)} important correlations.")
        return important_corr
    except Exception as e:
        print(f"[ERROR] Failed to extract important correlations: {e}")
        return pd.DataFrame()


def log_mapping_matrix_analysis(matrix, output_file="mapping_matrix_analysis.json"):
    """
    Log insights derived from the mapping matrix into a JSON file.
    Args:
        matrix: Pandas DataFrame containing the mapping matrix correlations.
        output_file: Path to save the analysis.
    """
    try:
        # Analyze and summarize the matrix
        analysis = {
            "strong_correlations": extract_important_correlations(matrix).to_dict(
                orient="records"
            )
        }

        # Save analysis to a JSON file
        with open(output_file, "w") as f:
            json.dump(analysis, f, indent=4)
        print(f"[INFO] Mapping matrix analysis saved to {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to log mapping matrix analysis: {e}")
