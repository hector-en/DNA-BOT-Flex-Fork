import os
import yaml
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import subprocess
from ai_modules.ai_optimizer import SerialDilutionExperiment, BasicAssemblyExperiment
from ai_modules.mapping_matrix import create_mapping_matrix, visualize_mapping_matrix, save_mapping_matrix
from ai_modules.api_generator import generate_optimized_code, save_protocol, save_yaml_configuration


class AIPipeline:
    """
    AI-driven pipeline to analyze diffs, map them to experimental results,
    and generate optimized Python protocols for Serial Dilution and Basic Assembly.
    """

    def __init__(self, template_file, diff_log, results_dir, experiment_type, output_dir="optimized_outputs", configs_dir="configs"):
        """
        Initialize the AI pipeline with required files and directories.
        Args:
            template_file (str or Path): Path to the original protocol template.
            diff_log (str or Path): Path to the diff log file.
            results_dir (str or Path): Directory containing experimental results or assembly data.
            experiment_type (str): Type of experiment ("serial_dilution" or "basic_assembly").
            output_dir (str or Path): Directory to save pipeline outputs.
            configs_dir (str or Path): Directory containing YAML configuration files.
        """
        self.template_file = Path(template_file)
        self.diff_log = Path(diff_log)
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.configs_dir = Path(configs_dir)
        self.experiment_type = experiment_type.lower()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize experiment handler
        if self.experiment_type == "serial_dilution":
            self.experiment = SerialDilutionExperiment(results_dir=self.results_dir, output_dir=self.output_dir)
        elif self.experiment_type == "basic_assembly":
            self.experiment = BasicAssemblyExperiment(results_dir=self.results_dir, output_dir=self.output_dir)
        else:
            raise ValueError("[ERROR] Unsupported experiment type. Use 'serial_dilution' or 'basic_assembly'.")

    def run(self):
        """
        Execute the AI pipeline for protocol optimization.
        """
        try:
            print(f"[INFO] Starting AI pipeline for {self.experiment_type}...")

            # Step 1: Load experimental or assembly data
            data = self.experiment.load_results()

            # Step 2: Visualize data (log-scale for Serial Dilution)
            self.experiment.visualize_results_from_csv(data)

            # Step 3: Extract features and calculate insights (e.g., Z-factors)
            if self.experiment_type == "serial_dilution":
                features = []
                z_scores = []
                for df in self.experiment.results.values():
                    features.append(self.experiment.extract_features(df))
                    z_scores.append(self.experiment.calculate_z_factor("Control", "Test"))

                # Train ML model for Serial Dilution
                model = self.experiment.train_model(np.array(features), np.array(z_scores))
                insights = {"z_factor_mean": np.mean(z_scores)}

            elif self.experiment_type == "basic_assembly":
                assembly_insights = self.experiment.analyze_constructs()
                insights = {"assembly_efficiency": assembly_insights["efficiency"], "error_rate": assembly_insights["error_rate"]}

            # Step 4: Parse diffs from the diff log
            diffs = self.parse_diff_log()
            if not diffs:
                raise ValueError("[ERROR] No valid diff logs found.")

            # Step 5: Create and save the mapping matrix
            mapping_matrix = create_mapping_matrix(diffs, self.experiment.generate_experiment_insights())
            save_mapping_matrix(mapping_matrix, self.output_dir / "mapping_matrix.csv")
            visualize_mapping_matrix(mapping_matrix, self.output_dir / "mapping_matrix.png")

            # Step 6: Generate the optimized protocol
            optimized_code, inferred_insights = generate_optimized_code(
                template_code=self.template_file.read_text(),
                diffs=diffs,
                insights=insights,  # AI or experiment-specific insights
                mapping_matrix=mapping_matrix.to_dict(),  # Mapping matrix for optimization
                api_key=os.environ.get("OPENAI_API_KEY"),
                api_engine="gpt-4"
            )

            # Step 7: Save the optimized protocol
            optimized_protocol_path = self.output_dir / "optimized_protocol.py"
            save_protocol(optimized_code, optimized_protocol_path)

            # Step 8: Allow user to choose a previous YAML file
            previous_yaml = self.select_previous_yaml()

            # Step 9: Generate and save the optimized YAML configuration
            output_yaml_path = self.output_dir / "optimized_protocol.yaml"
            save_yaml_configuration(
                optimized_code=optimized_code,
                insights=inferred_insights,  # Pass AI-inferred insights
                previous_yaml=previous_yaml,  # Selected or loaded YAML configuration
                output_file=output_yaml_path,
                api_key=os.environ.get("OPENAI_API_KEY"),
                api_engine="gpt-4"
            )
            print(f"[INFO] Optimized YAML saved to {output_yaml_path}")

        except Exception as e:
            print(f"[ERROR] AI pipeline failed: {e}")

    def parse_diff_log(self):
        """
        Parse diffs from the diff log file.
        Returns:
            list: List of diff lines.
        """
        if not self.diff_log.exists():
            print(f"[ERROR] Diff log file {self.diff_log} not found.")
            return []

        try:
            with self.diff_log.open("r") as f:
                return f.readlines()
        except Exception as e:
            print(f"[ERROR] Failed to parse diff log: {e}")
            return []

    def select_previous_yaml(self):
        """
        Allow the user to select a previous YAML configuration from the configs directory.
        Returns:
            dict: Parsed YAML content of the selected file, or None if skipped.
        """
        try:
            yaml_files = list(self.configs_dir.glob("*.yaml"))
            if not yaml_files:
                print("[INFO] No YAML files found in the configs directory.")
                return None

            print("[INFO] Available YAML configurations:")
            for idx, file in enumerate(yaml_files, start=1):
                print(f"{idx}: {file.name}")

            choice = input(f"Select a YAML file (1-{len(yaml_files)}) or press Enter to skip: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(yaml_files):
                selected_yaml = yaml_files[int(choice) - 1]
                print(f"[INFO] Loading YAML configuration: {selected_yaml.name}")
                with open(selected_yaml, "r") as yaml_file:
                    return yaml.safe_load(yaml_file)
            else:
                print("[INFO] Skipping YAML configuration selection.")
                return None
        except Exception as e:
            print(f"[ERROR] Failed to select previous YAML configuration: {e}")
            return None
from pathlib import Path
from datetime import datetime

def process_ai_pipeline():
    """
    Execute the AI pipeline for protocol optimization.
    Dynamically updates configurations and manages experiment selection.
    """
    # Define directories and paths
    OUTPUT_DIR = Path("optimized_outputs")  # Directory for optimized outputs
    DIFF_LOG = Path("logs/diff_log.txt")  # File for storing diffs
    TEMPLATE_FILE = Path("templates/protocol_starting_template.py")  #template file - starting point for generating an optimized protocol.
    RESULTS_DIR = Path("results")  # Directory for experimental results
    CONFIGS_DIR = Path("configs")  # Directory for YAML configurations
    TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")  # Timestamp for unique file names

    # Available experiment types
    EXPERIMENT_TYPES = ["serial_dilution", "basic_assembly"]

    # Display experiment options
    print("\n--- AI Pipeline Execution ---")
    for idx, experiment in enumerate(EXPERIMENT_TYPES, start=1):
        print(f"{idx}: {experiment}")
    print("A: Abort the pipeline.")

    # Get user selection
    while True:
        choice = input(f"Select an experiment type (1-{len(EXPERIMENT_TYPES)}) or 'A' to abort: ").strip().upper()
        if choice == "A":
            print("[INFO] Pipeline aborted by user.")
            return
        if choice.isdigit() and 1 <= int(choice) <= len(EXPERIMENT_TYPES):
            experiment_type = EXPERIMENT_TYPES[int(choice) - 1]
            break
        print("[ERROR] Invalid selection. Please try again.")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Run the selected pipeline
    try:
        # Starting pipeline for selected experiment type.
        pipeline = AIPipeline(
            template_file=TEMPLATE_FILE,
            diff_log=DIFF_LOG,
            results_dir=RESULTS_DIR,
            experiment_type=experiment_type,
            output_dir=OUTPUT_DIR,
            configs_dir=CONFIGS_DIR,
        )
        pipeline.run()
        print("[SUCCESS] AI pipeline completed successfully.")
    except Exception as e:
        print(f"[ERROR] Pipeline execution failed: {e}")

if __name__ == "__main__":
    process_ai_pipeline()

    # Start the translation pipeline.py script
    try:
        subprocess.run(["python", "ai_pipeline.py"], check=True)
        print("ai_pipeline.py executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing ai_pipeline.py: {e}")
    except FileNotFoundError:
        print("ai_pipeline.py not found. Please ensure the file exists in the current directory.")
