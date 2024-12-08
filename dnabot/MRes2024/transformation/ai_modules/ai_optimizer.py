import numpy as np
import pandas as pd
import yaml

class AIDiffOptimizer:
    """
    AI model to map diffs to experimental results and suggest optimizations.
    """

    def __init__(self, model_file="ai_model.pkl"):
        self.model_file = model_file
        self.model = None  # Placeholder for the machine learning model

    def load_or_initialize_model(self):
        """
        Load a trained model or initialize a new one.
        """
        if os.path.exists(self.model_file):
            from joblib import load
            self.model = load(self.model_file)
        else:
            from sklearn.ensemble import RandomForestRegressor
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def train_model(self, features, results):
        """
        Train the AI model with extracted features and experimental results.
        """
        self.model.fit(features, results)

    def predict_impact(self, diff_features):
        """
        Predict the impact of changes based on diff features.
        """
        return self.model.predict([diff_features])

    def create_mapping_matrix(self, diff_log, results):
        """
        Create a multimodal mapping matrix between diffs and experimental results.
        Args:
            diff_log: List of protocol diffs.
            results: Experimental results (e.g., Z-factor).
        Returns:
            mapping_matrix: DataFrame mapping diffs to results.
        """
        mapping = []

        for diff, result in zip(diff_log, results):
            features = self.extract_features_from_diff(diff)
            mapping.append(features + [result])

        # Create DataFrame for easy manipulation
        columns = ["diff_length", "num_inserts", "num_deletes", "mix_changes", "aspirate_changes", "z_factor"]
        mapping_matrix = pd.DataFrame(mapping, columns=columns)
        return mapping_matrix

    def extract_features_from_diff(self, diff):
        """
        Extract numerical features from a code diff.
        """
        return [
            len(diff),                # Length of diff
            diff.count("insert"),     # Insertions
            diff.count("delete"),     # Deletions
            diff.count("mix"),        # Mixing changes
            diff.count("aspirate")    # Aspirations
        ]

    def save_model(self):
        """
        Save the trained model for future use.
        """
        from joblib import dump
        dump(self.model, self.model_file)
