import os
import re
import sys
import yaml
import json

class GenericTransformer:
    """
    A class to handle generic transformations between OT-2 and Flex scripts using YAML-based configurations.
    """

    def __init__(self, map_file):
        with open(map_file, 'r') as file:
            self.map = yaml.safe_load(file)

    def ensure_files(self, reverse=False):
        """
        Ensure required files for Flex simulation or OT-2 setup exist.
        Creates dummy files if missing.
        """
        required_files = {
            "belt_calibration.json": {
                "path": "/home/vmuser/.opentrons/belt_calibration.json",
                "content": {"robot_model": "Flex", "calibrations": {}}
            },
            "deck_calibration.json": {
                "path": "/home/vmuser/.opentrons/deck_calibration.json",
                "content": {
                    "robot_model": "Flex",
                    "calibrations": {
                        "A1": {"x": 12.5, "y": 9.0, "z": 4.0},
                        "B1": {"x": 25.0, "y": 9.0, "z": 4.0},
                        "C1": {"x": 37.5, "y": 9.0, "z": 4.0}
                    }
                }
            },
            "robot_settings.json": {
                "path": "/home/vmuser/.opentrons/robot_settings.json",
                "content": {"robot_model": "Flex", "settings": {}} if not reverse else {"robot_model": "OT-2", "settings": {}}
            },
            "pressure_sensor_data.csv": {
                "path": "/data/pressure_sensor_data.csv",
                "content": """timestamp,pressure
2024-12-01T00:00:00Z,0.0
2024-12-01T00:01:00Z,0.1
2024-12-01T00:02:00Z,0.0
2024-12-01T00:03:00Z,0.2
2024-12-01T00:04:00Z,0.0"""
            }
        }

        for file_name, details in required_files.items():
            file_path = details["path"]
            content = details["content"]

            if not os.path.exists(file_path):
                print(f"{file_name} is missing. Creating a default file...")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                if file_name.endswith(".json"):
                    with open(file_path, "w") as f:
                        json.dump(content, f, indent=4)
                elif file_name.endswith(".csv"):
                    with open(file_path, "w") as f:
                        f.write(content)
            else:
                print(f"{file_name} is already present.")

    def apply_metadata_and_requirements(self, script, reverse=False):
            """
            Update metadata and requirements.
            """
            metadata_map = self.map["metadata"]
            if reverse:
                # Revert to OT-2 style metadata
                script = re.sub(r"'protocolName': '.*?'", "'protocolName': 'OT-2 Protocol'", script)
                script = re.sub(r"'description': '.*?'", "'description': 'Simulate a Clip Reaction on OT-2'", script)
                script = re.sub(r"requirements = {.*?}", "", script, flags=re.DOTALL)
            else:
                # Update metadata and add requirements for Flex
                script = re.sub(r"'protocolName': '.*?'", f"'protocolName': '{metadata_map['protocolName']}'", script)
                script = re.sub(r"'description': '.*?'", f"'description': '{metadata_map['description']}'", script)
                script = re.sub(
                    r"(metadata = {.*?})",
                    r"\1\nrequirements = " + json.dumps(self.map["requirements"], indent=4),
                    script,
                    flags=re.DOTALL
                )
            return script
    
    def apply_labware_changes(self, script, reverse=False):
        """Update labware definitions."""
        labware_map = self.map["labware"]
        map_to_use = labware_map if not reverse else {v: k for k, v in labware_map.items()}
        for old, new in map_to_use.items():
            script = script.replace(old, new)
        return script

    def apply_pipette_changes(self, script, reverse=False):
        """Update pipette definitions."""
        pipette_map = self.map["pipettes"]
        map_to_use = pipette_map if not reverse else {v: k for k, v in pipette_map.items()}
        for old, new in map_to_use.items():
            script = script.replace(old, new)
        return script

    def apply_module_changes(self, script, reverse=False):
        """Update module definitions."""
        module_map = self.map["modules"]
        map_to_use = module_map if not reverse else {v: k for k, v in module_map.items()}
        for old, new in map_to_use.items():
            script = script.replace(old, new)
        return script

    def apply_command_changes(self, script, reverse=False):
        """Update command syntax."""
        commands_map = self.map["commands"]
        for command, details in commands_map.items():
            if "from" in details and "to" in details:
                if reverse:
                    script = re.sub(details["to"], details["from"], script)
                else:
                    script = re.sub(details["from"], details["to"], script)
            if not reverse and "insert_after" in details and "code" in details:
                script = script.replace(details["insert_after"], f"{details['insert_after']}\n{details['code']}")
        return script

    def transform(self, input_file, output_file, reverse=False):
        """Transform the script."""
        if not os.path.exists(input_file):
            print(f"Error: {input_file} does not exist.")
            return

        self.ensure_files(reverse)

        with open(input_file, "r") as infile:
            script = infile.read()

        # Apply transformations
        script = self.apply_metadata_and_requirements(script, reverse)
        script = self.apply_labware_changes(script, reverse)
        script = self.apply_pipette_changes(script, reverse)
        script = self.apply_module_changes(script, reverse)
        script = self.apply_command_changes(script, reverse)

        with open(output_file, "w") as outfile:
            outfile.write(script)

        print(f"Transformation complete! Saved to {output_file}.")

# Main Execution
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python transform.py <input_script.py> <output_script.py> <direction>")
        print("<direction>: 'ot2_to_flex' or 'flex_to_ot2'")
        sys.exit(1)

    input_script = sys.argv[1]
    output_script = sys.argv[2]
    direction = sys.argv[3]

    transformer = GenericTransformer("generic_map.yaml")

    if direction == "ot2_to_flex":
        transformer.transform(input_script, output_script, reverse=False)
    elif direction == "flex_to_ot2":
        transformer.transform(input_script, output_script, reverse=True)
    else:
        print("Invalid direction. Use 'ot2_to_flex' or 'flex_to_ot2'.")
