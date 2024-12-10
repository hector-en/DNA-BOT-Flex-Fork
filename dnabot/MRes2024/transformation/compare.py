import difflib
from pathlib import Path

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

if __name__ == "__main__":
    # Example usage
    file1 = "pipeline.py"
    file2 = "pipeline_dependon_results.py"
    differences = compare_files(file1, file2)
    
    if differences is not None:
        print("Differences between files:")
        for line in differences:
            print(line)
    else:
        print("Comparison could not be completed.")
