import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import seaborn as sns


class BaseExperiment:
    """
    Base class for shared experiment functionalities such as loading data,
    saving results, and generating visualizations.
    """

    def __init__(self, results_dir, output_dir="results_analysis"):
        """
        Initialize the base experiment.
        Args:
            results_dir (str or Path): Directory containing result files.
            output_dir (str or Path): Directory to save outputs (e.g., analysis results, plots).
        """
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def load_results(self, file_extension=".xlsx"):
        """
        Load result files from the directory.
        Args:
            file_extension (str): File extension of result files (e.g., ".xlsx").
        """
        self.results = {}
        for file in self.results_dir.glob(f"*{file_extension}"):
            try:
                self.results[file.name] = pd.read_excel(file)
                print(f"[INFO] Loaded results from {file.name}")
            except Exception as e:
                print(f"[ERROR] Could not load {file.name}: {e}")

    def save_results(self, df, filename):
        """
        Save processed results to a file.
        Args:
            df (pd.DataFrame): DataFrame to save.
            filename (str): Output filename.
        """
        output_path = self.output_dir / filename
        df.to_excel(output_path, index=False)
        print(f"[INFO] Results saved to {output_path}")


class SerialDilutionExperiment(BaseExperiment):
    """
    Class for handling serial dilution experiments.
    """

    def calculate_z_factor(self, row):
        """
        Calculate Z-factor for a single row of serial dilution data.
        """
        try:
            control_mean = row[11]
            control_std = row[11:].std()
            test_mean = row[:11].mean()
            test_std = row[:11].std()

            numerator = 3 * (control_std + test_std)
            denominator = abs(control_mean - test_mean)
            return 1 - (numerator / denominator) if denominator != 0 else -1
        except Exception as e:
            print(f"[ERROR] Failed to calculate Z-factor: {e}")
            return -1

    def visualize_results(self, data, output_file_prefix="serial_dilution"):
        """
        Generate visualization for serial dilution data in log scale.
        """
        try:
            # Plot fluorescence data in log scale
            plt.figure(figsize=(12, 6))
            sns.lineplot(data=np.log1p(data.iloc[:, :12].mean(axis=0)), marker="o")
            plt.title("Fluorescence Data (Log Scale)")
            plt.xlabel("Dilution Step")
            plt.ylabel("Log Fluorescence")
            plt.savefig(self.output_dir / f"{output_file_prefix}_log_fluorescence.png")
            plt.close()

            # Plot Z-Factor histogram
            plt.figure(figsize=(10, 6))
            sns.histplot(data['Z-Factor'], bins=20, kde=True, color='blue')
            plt.axvline(x=0.5, color='red', linestyle='--', label='Lower Threshold (Z=0.5)')
            plt.axvline(x=1.0, color='green', linestyle='--', label='Upper Threshold (Z=1.0)')
            plt.legend()
            plt.title("Z-Factor Distribution")
            plt.savefig(self.output_dir / f"{output_file_prefix}_z_factors.png")
            plt.close()

            print(f"[INFO] Log-scale visualizations saved to {self.output_dir}")
        except Exception as e:
            print(f"[ERROR] Failed to visualize data: {e}")
        
    def extract_features(self, data):
        """
        Extract numerical features for ML analysis.
        Returns:
            np.ndarray: Feature matrix.
        """
        try:
            features = []
            for _, row in data.iterrows():
                features.append([
                    row[:11].mean(),  # Mean fluorescence for test wells
                    row[11],          # Control fluorescence
                    row['Z-Factor']   # Z-Factor
                ])
            return np.array(features)
        except Exception as e:
            print(f"[ERROR] Failed to extract features: {e}")
            return np.array([])

    def train_model(self, features, targets):
        """
        Train a regression model using features and targets.
        Uses a pipeline with standard scaling and RandomForestRegressor.
        """
        try:
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
            ])
            pipeline.fit(features, targets)
            print("[INFO] Model training completed.")
            return pipeline
        except Exception as e:
            print(f"[ERROR] Failed to train model: {e}")
            return None

    def optimize_experiment(self, model, new_data):
        """
        Use the trained model to optimize experimental parameters.
        """
        try:
            features = self.extract_features(new_data)
            predictions = model.predict(features)
            new_data['Predicted Z-Factor'] = predictions
            new_data['Optimization Suggestion'] = new_data['Predicted Z-Factor'].apply(
                lambda x: "Optimize Parameters" if x < 0.5 else "Acceptable"
            )
            self.save_results(new_data, "optimized_serial_dilution.xlsx")
            return new_data
        except Exception as e:
            print(f"[ERROR] Failed to optimize experiment: {e}")
            return new_data


class BasicAssemblyExperiment(BaseExperiment):
    """
    Class for handling BASIC DNA assembly experiments.
    Includes efficiency analysis, missing component detection, ML modeling, and visualization.
    """

    def analyze_constructs(self, constructs_file, part_coords_file, linker_coords_file):
        """
        Analyze assembly constructs for efficiency, missing parts, and throughput.
        Args:
            constructs_file (str or Path): File containing construct designs.
            part_coords_file (str or Path): File containing part coordinates.
            linker_coords_file (str or Path): File containing linker coordinates.
        Returns:
            pd.DataFrame: Analysis results with efficiency scores and missing component checks.
        """
        try:
            # Load construct, part, and linker data
            constructs = pd.read_csv(constructs_file)
            parts = pd.read_csv(part_coords_file)
            linkers = pd.read_csv(linker_coords_file)

            # Enrich constructs with part and linker data
            constructs = constructs.merge(parts, how="left", left_on="Part 1", right_on="Part/linker")
            constructs = constructs.merge(linkers, how="left", left_on="Linker 1", right_on="Part/linker")

            # Identify missing components in constructs
            constructs["Missing Components"] = constructs.isnull().sum(axis=1)

            # Calculate random efficiency scores for demonstration (to be replaced with real metrics)
            constructs["Efficiency Score"] = constructs.apply(lambda row: np.random.uniform(0.8, 1.0), axis=1)

            self.save_results(constructs, "basic_assembly_analysis.xlsx")
            return constructs
        except Exception as e:
            print(f"[ERROR] Failed to analyze assembly data: {e}")
            return pd.DataFrame()

    def visualize_constructs(self, constructs, output_file_prefix="basic_assembly"):
        """
        Visualize assembly constructs and efficiency scores.
        Args:
            constructs (pd.DataFrame): DataFrame with construct analysis.
            output_file_prefix (str): Prefix for the saved plot file.
        """
        try:
            # Bar plot of efficiency scores
            plt.figure(figsize=(12, 6))
            sns.barplot(data=constructs, x="Well", y="Efficiency Score", palette="Set2")
            plt.title("Assembly Efficiency Scores per Construct")
            plt.xticks(rotation=90)
            plt.savefig(self.output_dir / f"{output_file_prefix}_efficiency_scores.png")
            plt.close()

            # Countplot of missing components
            plt.figure(figsize=(10, 6))
            sns.countplot(data=constructs, x="Missing Components", palette="Set3")
            plt.title("Distribution of Missing Components Across Constructs")
            plt.savefig(self.output_dir / f"{output_file_prefix}_missing_components.png")
            plt.close()

            print(f"[INFO] Visualizations saved to {self.output_dir}")
        except Exception as e:
            print(f"[ERROR] Failed to visualize constructs: {e}")

    def extract_features(self, constructs):
        """
        Extract numerical features for ML analysis from constructs.
        Args:
            constructs (pd.DataFrame): Construct analysis DataFrame.
        Returns:
            np.ndarray: Feature matrix.
        """
        try:
            features = constructs[["Efficiency Score", "Missing Components"]].values
            return features
        except Exception as e:
            print(f"[ERROR] Failed to extract features: {e}")
            return np.array([])

    def train_model(self, features, targets):
        """
        Train an ML model to predict efficiency scores based on features.
        Args:
            features (np.ndarray): Feature matrix (e.g., missing components, linker usage).
            targets (np.ndarray): Target vector (e.g., efficiency scores).
        Returns:
            RandomForestRegressor: Trained ML model.
        """
        try:
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
            ])
            pipeline.fit(features, targets)
            print("[INFO] ML Model training completed.")
            return pipeline
        except Exception as e:
            print(f"[ERROR] Failed to train ML model: {e}")
            return None

    def optimize_constructs(self, model, new_constructs):
        """
        Use the trained model to optimize assembly constructs.
        Args:
            model (Pipeline): Trained ML model for prediction.
            new_constructs (pd.DataFrame): New constructs to optimize.
        Returns:
            pd.DataFrame: Constructs with predicted efficiency scores and optimization suggestions.
        """
        try:
            features = self.extract_features(new_constructs)
            predictions = model.predict(features)
            new_constructs['Predicted Efficiency'] = predictions
            new_constructs['Optimization Suggestion'] = new_constructs['Predicted Efficiency'].apply(
                lambda x: "Optimize Design" if x < 0.85 else "Acceptable"
            )
            self.save_results(new_constructs, "optimized_basic_assembly.xlsx")
            return new_constructs
        except Exception as e:
            print(f"[ERROR] Failed to optimize constructs: {e}")
            return new_constructs
