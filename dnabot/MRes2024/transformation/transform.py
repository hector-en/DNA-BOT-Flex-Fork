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
        Update metadata and requirements dynamically for Flex to OT-2 and OT-2 to Flex transformations.
        """
        metadata_map = self.map["metadata"]
        requirements_map = self.map["requirements"]

        # Extract the original description
        current_description_match = re.search(r"'description':\s*'(.*?)'", script)
        current_description = current_description_match.group(1) if current_description_match else metadata_map.get("description", "Simulate a Clip Reaction")

        if reverse:  # Flex to OT-2
            # Extract apiLevel from requirements or default to "2.15"
            current_api_level = re.search(r'"apiLevel":\s*"[0-9.]+"', script)
            api_level = current_api_level.group(0).split(':')[1].strip(' "').strip() if current_api_level else "2.15"

            # Remove requirements
            script = re.sub(r"requirements = {.*?}\n", "", script, flags=re.DOTALL)

            # Replace metadata with OT-2 specific structure
            script = re.sub(r"'protocolName': '.*?'", "'protocolName': 'OT-2 Protocol'", script)
            updated_description = current_description.replace("Flex", "OT-2")
            script = re.sub(r"'description': '.*?'", f"'description': '{updated_description}',", script)

            # Add apiLevel back to metadata
            script = re.sub(
                r"(metadata = {.*?)(})",  # Match metadata content and closing brace
                r"\1    'apiLevel': '" + api_level + r"'\2",  # Insert apiLevel before closing brace
                script,
                flags=re.DOTALL
            )
        else:  # OT-2 to Flex
            # Extract apiLevel from the metadata section
            current_api_level = re.search(r"apiLevel:\s*'[0-9.]+'", script)
            api_level = current_api_level.group(0).split(':')[1].strip(' "').strip() if current_api_level else requirements_map.get("apiLevel", "2.19")
                        # Remove apiLevel from metadata
            script = re.sub(
                r"'apiLevel':\s*'[^']*'(,?\s*)?",  # Match 'apiLevel': '<value>' optionally followed by a comma and whitespace
                "",
                script
            )            


            # Update metadata and add requirements dynamically
            script = re.sub(r"'protocolName': '.*?'", "'protocolName': '" + metadata_map["protocolName"] + "'", script)
            updated_description = current_description.replace("OT-2", "Flex")
            script = re.sub(r"'description': '.*?'", f"'description': '{updated_description}'", script)


            # Add requirements with extracted apiLevel
            requirements_with_api_level = requirements_map.copy()
            requirements_with_api_level["apiLevel"] = api_level
            script = re.sub(
                r"(metadata = {.*?})",
                r"\1\nrequirements = " + json.dumps(requirements_with_api_level, indent=4),
                script,
                flags=re.DOTALL
            )

        return script


    def apply_labware_changes(self, script, reverse=False):
        """
        Update labware definitions dynamically using mappings and configuration from the YAML file.
        Handles trash setup and drop_tip behavior dynamically.
        """
        labware_map = self.map["labware"]
        variable_map = self.map.get("variables", {})
        deck_setup = self.map.get("deckSetup", {})
        trash_config = deck_setup.get("trash", {})
        trash_variable = trash_config.get("variable", "trash")
        map_to_use = labware_map if not reverse else {v: k for k, v in labware_map.items()}

        # Replace old labware with new labware based on mappings
        for old, new in map_to_use.items():
            script = script.replace(old, new)

        # Replace variable names dynamically
        for old_var, new_var in variable_map.items():
            script = re.sub(rf"\b{old_var}\b", new_var, script)

        # Handle reverse (Flex to OT-2) transformations
        if reverse:
            # Remove trash setup
            trash_pattern = rf"{trash_variable} = protocol\.load_labware\('.*?', '.*?'\)"
            script = re.sub(trash_pattern, "", script)

            # Replace pipette.drop_tip(trash['A1']) with pipette.drop_tip()
            drop_tip_pattern = rf"pipette\.drop_tip\({trash_variable}\['.*?'\]\)"
            script = re.sub(drop_tip_pattern, "pipette.drop_tip()", script)
        else:
            # Handle Flex transformations (add trash setup if missing)
            trash_name = trash_config.get("name")
            trash_slot = trash_config.get("slot", {}).get("flex")
            if trash_name and trash_slot:
                trash_setup = f"{trash_variable} = protocol.load_labware('{trash_name}', '{trash_slot}')"
                if trash_name not in script:
                    script = re.sub(r"(plate_96 = .+)", r"\1\n    " + trash_setup, script)

        return script
    
    def apply_pipette_changes(self, script, reverse=False):
        """
        Update pipette definitions dynamically using YAML mappings.
        """
        pipette_map = self.map["pipettes"]
        map_to_use = pipette_map if not reverse else {v: k for k, v in pipette_map.items()}

        for old, new in map_to_use.items():
            script = script.replace(old, new)
        return script

    def apply_command_changes(self, script, reverse=False):
        """
        Update command syntax dynamically based on mappings from the YAML file.
        """
        commands_map = self.map["commands"]
        trash_config = self.map.get("deckSetup", {}).get("trash", {})
        drop_tip_location = trash_config.get("dropTipLocation", "A1")  # Default to A1
        trash_variable = trash_config.get("variable", "trash")

        for command, details in commands_map.items():
            if "from" in details and "to" in details:
                if reverse:
                    script = re.sub(details["to"], details["from"], script)
                else:
                    script = re.sub(details["from"], details["to"], script)

            # Dynamically replace pipette.drop_tip() with pipette.drop_tip(trash['<location>'])
            if command == "drop_tip" and not reverse:
                drop_tip_pattern = r"pipette\.drop_tip\(\)"
                drop_tip_replacement = f"pipette.drop_tip({trash_variable}['{drop_tip_location}'])"
                script = re.sub(drop_tip_pattern, drop_tip_replacement, script)

            if not reverse and "insert_after" in details and "code" in details:
                # Insert extra code dynamically if defined
                script = re.sub(
                    r"(" + re.escape(details["insert_after"]) + r"\(.*?\))",
                    r"\1\n    " + details["code"],
                    script
                )

        return script

    def transform(self, input_file, output_file, reverse=False):
        """Transform the script."""
        if not os.path.exists(input_file):
            print(f"Error: {input_file} does not exist.")
            return

        self.ensure_files(reverse)

        with open(input_file, "r") as infile:
            script = infile.read()

        script = self.apply_metadata_and_requirements(script, reverse)
        script = self.apply_labware_changes(script, reverse)
        script = self.apply_pipette_changes(script, reverse)
        script = self.apply_command_changes(script, reverse)

        with open(output_file, "w") as outfile:
            outfile.write(script)

        print(f"Transformation complete! Saved to {output_file}.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python transform.py <input_script.py> <output_script.py> <direction>")
        sys.exit(1)

    input_script = sys.argv[1]
    output_script = sys.argv[2]
    direction = sys.argv[3]

    transformer = GenericTransformer("generic_map.yaml")

    if direction == "-of":
        transformer.transform(input_script, output_script, reverse=False)
    elif direction == "-fo":
        transformer.transform(input_script, output_script, reverse=True)
    else:
        print("Invalid direction.")