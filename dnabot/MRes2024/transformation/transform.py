import os
import re
import sys
import yaml
import json
import yaml
import stat
from pathlib import Path

class GenericTransformer:
    """
    A class to handle generic transformations between OT-2 and Flex scripts using YAML-based configurations.
    """

    def __init__(self, map_file):
        # Construct the full path to the map file relative to the current script
        script_dir = Path(__file__).parent  # Get the directory of the current script
        map_file_path = script_dir / map_file

        # Open the map file and load its content
        with map_file_path.open('r') as file:
            self.map = yaml.safe_load(file)
    def prepare_robot_environment(self, direction, yaml_file="robot_config.yaml"):
        """
        Prepare the robot environment by creating or validating required files based on the directionality switch.
        Parameters:
            direction (str): Directionality switch. Use '-of' for Flex and '-fo' for OT-2.
            yaml_file (str): Path to the YAML configuration file.
        """
        # Determine robot type based on the directionality switch
        if direction == "-of":
            robot_type = "flex"
        elif direction == "-fo":
            robot_type = "ot2"
        else:
            raise ValueError(f"Invalid directionality switch: {direction}. Use '-of' for Flex or '-fo' for OT-2.")

        # Load the YAML configuration
        with open(yaml_file, "r") as f:
            config_data = yaml.safe_load(f)

        # Extract the robot configuration
        robot_config = config_data["robot_settings"][robot_type]

        # Dynamically determine the home directory for `.opentrons` files
        base_path = os.path.expanduser("~/.opentrons")
        data_path = os.path.expanduser("~/data")

        # Define files to be generated
        required_files = {
            "belt_calibration.json": {
                "path": os.path.join(base_path, "belt_calibration.json"),
                "content": {
                    "robot_model": robot_config["robot_model"],
                    "calibrations": robot_config["calibrations"].get("belt", {})
                }
            },
            "deck_calibration.json": {
                "path": os.path.join(base_path, "deck_calibration.json"),
                "content": {
                    "robot_model": robot_config["robot_model"],
                    "calibrations": robot_config["calibrations"].get("deck", {})
                }
            },
            "robot_settings.json": {
                "path": os.path.join(base_path, "robot_settings.json"),
                "content": {
                    "robot_model": robot_config["robot_model"],
                    "settings": robot_config.get("settings", {})
                }
            },
            "pressure_sensor_data.csv": {
                "path": os.path.join(data_path, "pressure_sensor_data.csv"),
                "content": "\n".join(
                    [f'{entry["timestamp"]},{entry["pressure"]}' for entry in config_data["pressure_sensor_data"]]
                )
            }
        }

        # Create missing files or skip existing ones
        for file_name, details in required_files.items():
            file_path = details["path"]
            content = details["content"]

            if os.path.exists(file_path):
                print(f"{file_name} already exists at {file_path}. Skipping...")
                continue  # Skip existing files

            # Create missing files
            print(f"{file_name} is missing for {robot_type}. Creating a default file...")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            try:
                # Create JSON or CSV files
                if file_name.endswith(".json"):
                    with open(file_path, "w") as f:
                        json.dump(content, f, indent=4)
                elif file_name.endswith(".csv"):
                    with open(file_path, "w") as f:
                        f.write(content)

                print(f"{file_name} created successfully at {file_path}.")
            except Exception as e:
                print(f"Error creating {file_name} for {robot_type}: {e}")

    def setup_deck(self, script, reverse=False):
        """
        Dynamically insert labware setup into the script using the deckSetup from YAML.
        Ensures no duplicate setups and uses the appropriate slot for OT-2 or Flex.
        """
        deck_setup = self.map.get("deckSetup", {})
        trash_config = deck_setup.get("trash", {})
        # Dynamically determine the trash slot based on the transformation direction
        robot_type = "ot2" if reverse else "flex"
        trash_slot = trash_config.get("slot", {}).get(robot_type)

        if not trash_slot:
            raise ValueError(f"Trash slot not defined for {robot_type} in the YAML configuration.")

        # Format the setup code for the trash
        trash_setup_code = trash_config.get("setup_code", "").format(slot=trash_slot)

        # Ensure the trash setup code is present and valid
        if trash_setup_code and not re.search(re.escape(trash_setup_code), script):
            script = re.sub(
                r"(protocol\.comment\('Gripper required for labware transfer'\))",  # Insert after this known line
                rf"{trash_setup_code}\n    \1",
                script
            )

        # Dynamically insert setup for tipracks and plates
        for labware_type in ["tipracks", "plates"]:
            for item in deck_setup.get(labware_type, []):
                name = item["name"]
                slot = item["slot"]["ot2" if reverse else "flex"]
                variable = item["variable"]

                # Generate labware setup command
                setup_code = f"{variable} = protocol.load_labware('{name}', '{slot}')"

                # Check and insert the setup command if missing
                if not re.search(re.escape(setup_code), script):
                    script = re.sub(
                        r"(protocol\.comment\('Gripper required for labware transfer'\))",  # Insert after the last known setup
                        rf"{setup_code}\n    \1",
                        script
                    )

        return script


    def apply_metadata_and_requirements(self, script, reverse=False):
        """
        Update metadata dynamically for Flex to OT-2 and OT-2 to Flex transformations.
        """
        # Determine the suffix based on the transformation direction
        suffix = " (OT-2 Protocol)" if reverse else " (Flex Protocol)"

        # Extract the original description
        current_description_match = re.search(r"'description':\s*'(.*?)'", script)
        current_description = current_description_match.group(1) if current_description_match else "Simulate a Clip Reaction"

        if reverse:  # Flex to OT-2
            # Extract apiLevel from the metadata or set a default
            current_api_level_match = re.search(r"'apiLevel':\s*'([0-9.]+)'", script)
            api_level = current_api_level_match.group(1) if current_api_level_match else "2.15"

            # Remove requirements if they exist
            script = re.sub(r"requirements = {.*?}\n", "", script, flags=re.DOTALL)

            # Append suffix to protocolName
            script = re.sub(
                r"'protocolName':\s*'([^']+)'",  # Match the protocolName
                r"'protocolName': '\1" + suffix + r"'",  # Preserve name and append suffix
                script
            )

            # Update the description
            updated_description = current_description.replace("Flex", "OT-2")
            script = re.sub(
                r"'description':\s*'([^']+)'",
                f"'description': '{updated_description}',",
                script
            )

            # Add apiLevel back to metadata
            script = re.sub(
                r"(metadata = {.*?)(})",  # Match metadata content and closing brace
                r"\1    'apiLevel': '" + api_level + r"'\2",  # Insert apiLevel before closing brace
                script,
                flags=re.DOTALL
            )
        else:  # OT-2 to Flex
            # Extract apiLevel from the metadata or set a default
            current_api_level_match = re.search(r"'apiLevel':\s*'([0-9.]+)'", script)
            api_level = current_api_level_match.group(1) if current_api_level_match else "2.19"

            # Remove apiLevel from metadata
            script = re.sub(
                r"'apiLevel':\s*'[^']*'(,?\s*)?",  # Match 'apiLevel': '<value>' optionally followed by a comma and whitespace
                "",
                script
            )

            # Append suffix to protocolName
            script = re.sub(
                r"'protocolName':\s*'([^']+)'",  # Match the protocolName
                r"'protocolName': '\1" + suffix + r"'",  # Preserve name and append suffix
                script
            )

            # Update the description
            updated_description = current_description.replace("OT-2", "Flex")
            script = re.sub(
                r"'description':\s*'([^']+)'",
                f"'description': '{updated_description}'",
                script
            )

            # Dynamically add requirements, including 'robotType': 'Flex'
            script = re.sub(
                r"(metadata = {.*?})",
                r"\1\nrequirements = {\n    'apiLevel': '" + api_level + r"',\n    'robotType': 'Flex'\n}",
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
    
    def apply_variable_change(self, script, reverse=False):
        """
        Update variable names dynamically based on the mappings from the YAML file.
        Handles Flex to OT-2 and OT-2 to Flex transformations.
        """
        variable_ids_map = self.map.get("variable_ids", {})
        variables_map = self.map.get("variables", {})

        # Determine the mapping direction
        mapping = variable_ids_map if not reverse else {v: k for k, v in variable_ids_map.items()}

        # Replace variable names using the mappings
        for old_var, new_var in mapping.items():
            script = re.sub(rf"\b{re.escape(old_var)}\b", new_var, script)

        # Replace other variables (e.g., custom ones defined in "variables" section)
        for old_var, new_var in variables_map.items():
            script = re.sub(rf"\b{re.escape(old_var)}\b", new_var, script)

        return script


    def apply_command_changes(self, script, reverse=False):
        """
        Update command syntax dynamically based on mappings from the YAML file.
        Handles OT-2 and Flex-specific transformations.
        """
        commands_map = self.map["commands"]
        trash_config = self.map.get("deckSetup", {}).get("trash", {})

        # Dynamically resolve trash variable, name, slot, and dropTipLocation
        trash_variable = trash_config.get("variable", "trash")
        trash_name = trash_config.get("name", "opentrons_1_trash_1100ml_fixed")
        trash_slot = trash_config["slot"]["ot2" if reverse else "flex"]
        drop_tip_location = trash_config["dropTipLocation"]["ot2" if reverse else "flex"]

        # Ensure trash setup exists in the script
        trash_setup_code = f"{trash_variable} = protocol.load_labware('{trash_name}', '{trash_slot}')"
        if not re.search(re.escape(trash_setup_code), script):
            # Insert trash setup after a known line
            script = re.sub(
                r"(plate_96 = .+)",  # Insert after the plate setup line
                rf"\1\n    {trash_setup_code}",
                script
            )

        # Apply command transformations based on YAML mappings
        for command, details in commands_map.items():
            if "from" in details and "to" in details:
                if reverse:
                    # Reverse transformation
                    script = re.sub(details["to"], details["from"], script)
                else:
                    # Resolve placeholders for forward transformation
                    to_command = details["to"].replace(
                        "{trash_variable}", trash_variable
                    ).replace(
                        "{dropTipLocation}", drop_tip_location
                    )
                    script = re.sub(details["from"], to_command, script)

        # Fix extra parentheses in pipette.drop_tip calls
        script = re.sub(
            r"pipette\.drop_tip\((.*?)\)\(\)",  # Matches calls with trailing ()
            r"pipette.drop_tip(\1)",           # Removes the extra parentheses
            script
        )

        # Dynamically insert extra code after specific commands if specified in the YAML
        for command, details in commands_map.items():
            if not reverse and "insert_after" in details and "code" in details:
                script = re.sub(
                    r"(" + re.escape(details["insert_after"]) + r"\(.*?\))",
                    r"\1\n    " + details["code"],
                    script
                )

        return script

    def transform(self, input_file, output_file, reverse=False):
        """
        Transform the script based on the direction.
        """
        # Get the script's directory
        script_dir = Path(__file__).parent

        # Resolve full paths for input and output files
        input_file_path = script_dir / input_file
        output_file_path = script_dir / output_file

        # Check if the input file exists
        if not input_file_path.exists():
            print(f"Error: {input_file} does not exist at {input_file_path}")
            return

        # Read the input file
        with input_file_path.open("r") as infile:
            script = infile.read()

        # Ensure necessary files exist and are valid
        direction = "-of" if not reverse else "-fo"
        self.prepare_robot_environment(direction)

        # Apply transformations
        script = self.setup_deck(script, reverse)
        script = self.apply_metadata_and_requirements(script, reverse)
        script = self.apply_labware_changes(script, reverse)
        script = self.apply_pipette_changes(script, reverse)
        script = self.apply_command_changes(script, reverse)
        script = self.apply_variable_change(script, reverse)

        # Write the transformed script to the output file
        with output_file_path.open("w") as outfile:
            outfile.write(script)

        print(f"Transformation complete! Saved to {output_file_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python transform.py <direction> <input_script.py> <output_script.py>")
        sys.exit(1)

    input_script = sys.argv[2]
    output_script = sys.argv[3]
    direction = sys.argv[1]

    transformer = GenericTransformer("labware_setup.yaml")
    if direction == "-of":
        transformer.transform(input_script, output_script, reverse=False)
    elif direction == "-fo":
        transformer.transform(input_script, output_script, reverse=True)
    else:
        print("Invalid direction.")