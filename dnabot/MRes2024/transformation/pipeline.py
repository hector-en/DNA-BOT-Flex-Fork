import subprocess
import difflib
import yaml
from pathlib import Path
from datetime import datetime
#from ai_modules.ai_pipeline import AIPipeline

# Directory paths
BASE_DIR = Path(".")  # Ensure paths are relative to the working directory
INPUT_DIR = BASE_DIR / "input_scripts"
EXPECTED_DIR = BASE_DIR / "templates"
TRANSFORMED_DIR = BASE_DIR / "transformed_scripts"
CONFIG_DIR = BASE_DIR / "configs"
LOG_DIR = BASE_DIR / "logs"

# Predefined reaction types
REACTIONS = ["clip", "purification", "assembly", "transformation"]

# Timestamp for unique filenames
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def infer_reaction_from_filename(filename):
    """
    Infer the reaction type from the filename.
    Example: "oldclip.py" -> "clip"
    """
    for reaction in REACTIONS:
        if reaction in filename.lower():  # Case-insensitive matching
            return reaction
    return None


def run_transformation(input_file, output_file, direction, reaction):
    """
    Run transform.py to generate the transformed script.
    """
    input_file = str(input_file.relative_to(BASE_DIR))  # Use relative paths
    output_file = str(output_file.relative_to(BASE_DIR))  # Use relative paths

    cmd = [
        "python", "transform.py",
        "--reaction", reaction,
        direction,
        input_file,
        output_file
    ]

    if not (BASE_DIR / input_file).exists():
        raise FileNotFoundError(f"Error: {input_file} does not exist.")

    try:
        subprocess.run(cmd, check=True)
        print(f"[SUCCESS] Transformation completed for {reaction}: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Transformation failed for {reaction}: {e}")
        raise


def compare_files(file1, file2):
    """
    Compare two files and return differences as a list of strings.
    """
    if not Path(file1).exists():
        print(f"[WARNING] Transformed file '{file1}' is missing. Skipping comparison.")
        return None
    if not Path(file2).exists():
        print(f"[WARNING] Expected output file '{file2}' is missing. Skipping comparison.")
        return None

    with open(file1, "r") as f1, open(file2, "r") as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    diff = difflib.unified_diff(
        lines1, lines2, fromfile=file1, tofile=file2, lineterm=""
    )
    return list(diff)


def parse_diffs(log_file):
    """
    Parse the diffs.log file to extract actionable changes.
    """
    changes = []
    with open(log_file, "r") as file:
        current_file = None
        for line in file:
            if line.startswith("---") or line.startswith("+++"):
                current_file = line.split()[-1]
            elif line.startswith("- ") or line.startswith("+ "):
                changes.append((current_file, line.strip()))
    return changes


def validate_yaml(diffs, yaml_file):
    """
    Validate that the YAML file addresses changes in diffs.log.
    """
    with open(yaml_file, "r") as file:
        yaml_data = yaml.safe_load(file)

    missing_entries = []
    for file, change in diffs:
        if file.endswith(yaml_file.name):
            if "thermocycler" in change and "thermocycler" not in yaml_data.get("deckSetup", {}):
                missing_entries.append(change)
            if "magnetic_block" in change and "magnetic_block" not in yaml_data.get("deckSetup", {}):
                missing_entries.append(change)

    return missing_entries


def validate_transform(diffs, transform_file):
    """
    Validate that transform.py handles all required transformations.
    """
    with open(transform_file, "r") as file:
        transform_code = file.read()

    unsupported_changes = []
    for file, change in diffs:
        if file.endswith("transform.py"):
            if "thermocycler" in change and "_handle_thermocycler" not in transform_code:
                unsupported_changes.append(change)
            if "magnetic_block" in change and "_handle_magnetic_block" not in transform_code:
                unsupported_changes.append(change)

    return unsupported_changes


def generate_report(reaction, diff_comparison, yaml_validation, transform_validation, log_file, input_file, transformed_file, expected_file=None, append=False):
    """
    Generate a report based on validation results.
    Includes the input, transformed, and (if applicable) expected file paths for context.
    """
    mode = "a" if append else "w"
    with open(log_file, mode) as log:
        log.write(f"\n=== Validation Report for Reaction: {reaction} ===\n")
        log.write(f"Input Script: {input_file}\n")
        log.write(f"Transformed Script: {transformed_file}\n")
        if expected_file:
            log.write(f"Expected Script: {expected_file}\n")
        else:
            log.write("Expected Script: None (No comparison performed)\n")

        log.write("\n--- Step 1: Transform Validation ---\n")
        if diff_comparison:
            log.write("Differences between transformed script and expected output:\n")
            log.writelines(diff_comparison)
        else:
            log.write("Transformed script matches expected output or no comparison performed.\n")

        log.write("\n--- Step 2: YAML Validation ---\n")
        if yaml_validation:
            log.write("Missing or incorrect entries in YAML:\n")
            for entry in yaml_validation:
                log.write(f"- {entry}\n")
        else:
            log.write("All changes are reflected in YAML.\n")

        log.write("\n--- Step 3: Transform.py Validation ---\n")
        if transform_validation:
            log.write("Unsupported changes in transform.py:\n")
            for entry in transform_validation:
                log.write(f"- {entry}\n")
        else:
            log.write("All changes are handled in transform.py.\n")

        print(f"[INFO] Validation report for {reaction} saved to {log_file}")


def control_step(reaction, input_file, transformed_script, expected_file):
    """
    Control step to confirm, skip, or abort the pipeline for a specific reaction.
    Parameters:
        reaction (str): Reaction type (e.g., clip, purification).
        input_file (Path): Input file path.
        transformed_script (Path): Transformed script path.
        expected_file (Path or None): Expected file path.
    Returns:
        bool: True if the reaction should proceed, False to skip.
    """
    print("\n--- Pipeline Execution Control ---")
    print(f"Reaction: {reaction}")
    print(f"Input File: {input_file}")
    print(f"Transformed Script: {transformed_script}")
    print(f"Expected Output File: {expected_file if expected_file else 'Not Found'}")
    print("\nOptions:")
    print("[C]ontinue: Proceed with this reaction.")
    print("[S]kip: Skip this reaction and move to the next.")
    print("[A]bort: Stop the pipeline.")
    
    while True:
        user_choice = input("Enter your choice (C/S/A): ").strip().lower()
        if user_choice == "c":
            return True  # Continue with the pipeline
        elif user_choice == "s":
            print(f"[INFO] Skipping reaction: {reaction}")
            return False  # Skip this reaction
        elif user_choice == "a":
            print("[INFO] Aborting the pipeline.")
            sys.exit(0)  # Abort the entire pipeline
        else:
            print("[WARNING] Invalid choice. Please enter C, S, or A.")

def process_pipeline():
    """
    Process input and expected files to validate transformations.
    Dynamically updates available expected outputs after each step.
    """
    LOG_DIR.mkdir(exist_ok=True)  # Ensure log directory exists
    validation_log = LOG_DIR / f"validation_{TIMESTAMP}.log"  # Single comprehensive validation log

    def update_expected_files():
        """
        Update the dictionary of expected files dynamically from the `templates` folder.
        """
        return {f: infer_reaction_from_filename(f.name) for f in EXPECTED_DIR.iterdir() if f.suffix == ".py"}

    # Initial load of expected files
    expected_files = update_expected_files()

    # Collect input files
    input_files = {f: infer_reaction_from_filename(f.name) for f in INPUT_DIR.iterdir() if f.suffix == ".py"}

    for input_file, reaction in input_files.items():
        if not reaction:
            print(f"[WARNING] Skipping unknown reaction type in file: {input_file.name}")
            continue

        try:
            # Extract the base name of the input file
            original_name = input_file.stem

            # File paths for this file
            transformed_script = TRANSFORMED_DIR / f"transformed_{reaction}_{original_name}_{TIMESTAMP}.py"
            diffs_log = LOG_DIR / f"diffs_{reaction}_{original_name}_{TIMESTAMP}.log"
            yaml_file = CONFIG_DIR / f"{reaction}.yaml"
            individual_validation_log = LOG_DIR / f"validation_{reaction}_{original_name}_{TIMESTAMP}.log"
           # results_file = BASE_DIR / "results/experimental_results.xlsx"  # New: Path to experimental results

            # Present user options for the expected file
            matching_expected_files = [
                f for f, r in expected_files.items() if r == reaction
            ]

            print(f"\n--- Processing {input_file.name} ({reaction}) ---")
            print(f"[INFO] Available template files for {reaction}:")
            for idx, file in enumerate(matching_expected_files, start=1):
                print(f"{idx}: {file.name}")
            print(f"{len(matching_expected_files) + 1}: None (Skip comparison)")
            print("A: Abort the pipeline")
            print("S: Skip this file")
            print("C: Continue (new template will be created).")

            choice = input("Choose an option: ").strip().upper()
            if choice == "A":
                print("[INFO] Aborting pipeline.")
                return
            elif choice == "S":
                print(f"[INFO] Skipping file: {input_file.name}")
                continue
            elif choice == "C":
                expected_file = None
            else:
                try:
                    selected_index = int(choice)
                    if 1 <= selected_index <= len(matching_expected_files):
                        expected_file = matching_expected_files[selected_index - 1]
                    else:
                        print("[ERROR] Invalid selection. Skipping.")
                        continue
                except ValueError:
                    print("[ERROR] Invalid input. Skipping.")
                    continue

            # Step 1: Run Transformation
            run_transformation(input_file, transformed_script, "-of", reaction)

            # Step 2: Compare Transformed Script with Selected Expected Output
            if expected_file:
                diff_comparison = compare_files(str(transformed_script), str(expected_file))

                # Generate diffs log
                with open(diffs_log, "w") as log_file:
                    if diff_comparison:
                        log_file.writelines(diff_comparison)
                        print(f"[INFO] Diffs log generated for {reaction} ({original_name}): {diffs_log}")
                    else:
                        log_file.write(f"No differences found for {reaction} ({original_name}). Transformed script matches expected output.\n")
                        print(f"[INFO] No differences found for {reaction} ({original_name}).")
            else:
                # No expected file selected: create a template
                expected_template = EXPECTED_DIR / f"first_template_{reaction}_{original_name}_{TIMESTAMP}.py"
                expected_template.write_text(transformed_script.read_text())
                print(f"[INFO] No expected file chosen for {reaction} ({original_name}). Created: {expected_template}")
                diff_comparison = None

                # Write to diffs log indicating that no expected file was selected
                with open(diffs_log, "w") as log_file:
                    log_file.write(f"No expected file selected for {reaction} ({original_name}). Created a template: {expected_template}\n")
                    print(f"[INFO] Diffs log generated for {reaction} ({original_name}): {diffs_log}")

            # Step 3: Validate YAML and transform.py Against diffs.log
            diffs = parse_diffs(diffs_log) if diffs_log.exists() else []
            yaml_validation = validate_yaml(diffs, yaml_file)
            transform_validation = validate_transform(diffs, "transform.py")

            # Step 4: Generate Reports
            generate_report(
                reaction, 
                diff_comparison, 
                yaml_validation, 
                transform_validation, 
                individual_validation_log, 
                input_file=input_file, 
                transformed_file=transformed_script, 
                expected_file=expected_file
            )
            generate_report(
                reaction, 
                diff_comparison, 
                yaml_validation, 
                transform_validation, 
                validation_log, 
                input_file=input_file, 
                transformed_file=transformed_script, 
                expected_file=expected_file, 
                append=True
            )

            # Update expected files dynamically after each step
            expected_files = update_expected_files()

        except Exception as e:
            print(f"[ERROR] Pipeline failed for {reaction} ({original_name}): {e}")

if __name__ == "__main__":
    process_pipeline()
