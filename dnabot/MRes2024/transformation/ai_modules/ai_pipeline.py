import pandas as pd
from ai_optimizer import AIDiffOptimizer
from mapping_matrix import visualize_mapping_matrix, save_mapping_matrix
from api_generator import generate_optimized_code, save_protocol

class AIPipeline:
    """
    AI-driven pipeline to analyze diffs, map them to experimental results,
    and generate optimized Python protocols.
    """

    def __init__(self, template_file, diff_log, results_file, output_dir="optimized_outputs"):
        self.template_file = template_file
        self.diff_log = diff_log
        self.results_file = results_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.optimizer = AIDiffOptimizer()

    def run(self):
        """
        Run the AI pipeline.
        """
        print("[INFO] Starting AI pipeline...")

        # Step 1: Parse experimental results
        results = self.parse_results(self.results_file)
        z_scores = [result["z_factor"] for result in results.values()]

        # Step 2: Parse diffs
        diffs = self.parse_diff_log(self.diff_log)

        # Step 3: Create a mapping matrix
        mapping_matrix = self.optimizer.create_mapping_matrix(diffs, z_scores)
        save_mapping_matrix(mapping_matrix, self.output_dir / "mapping_matrix.csv")
        visualize_mapping_matrix(mapping_matrix, self.output_dir / "mapping_matrix.png")

        # Step 4: Train the AI model
        features = mapping_matrix.iloc[:, :-1].values  # Exclude Z-factor column
        self.optimizer.train_model(features, z_scores)
        self.optimizer.save_model()

        # Step 5: Generate optimized protocol
        with open(self.template_file, "r") as f:
            template_code = f.read()
        insights = mapping_matrix.corr()["z_factor"].to_dict()  # Correlation insights
        optimized_code = generate_optimized_code(template_code, diffs, insights)

        # Step 6: Save optimized protocol
        save_protocol(optimized_code, self.output_dir / "optimized_protocol.py")
        print("[INFO] AI pipeline complete. Outputs saved.")

    def parse_results(self, results_file):
        """
        Parse experimental results from an Excel file.
        """
        data = pd.read_excel(results_file)
        results = {}
        for _, row in data.iterrows():
            experiment_id = row["Experiment_ID"]
            z_factor = row["Z-Factor"]
            other_metrics = {col: row[col] for col in data.columns if col not in ["Experiment_ID", "Z-Factor"]}
            results[experiment_id] = {"z_factor": z_factor, "metrics": other_metrics}
        return results

    def parse_diff_log(self, diff_log):
        """
        Parse diffs from the diff log file.
        """
        with open(diff_log, "r") as f:
            diffs = f.readlines()
        return diffs
