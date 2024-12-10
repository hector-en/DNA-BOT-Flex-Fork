import os
import re
import sys
import yaml
import json
import yaml
import stat
from black import FileMode, format_str
from pathlib import Path

class GenericTransformer:
    """
    A class to handle generic transformations between OT-2 and Flex scripts using YAML-based configurations.
    """

    def __init__(self, map_file):
        """
        Initialize the transformer with a given YAML configuration file.

        Parameters:
            map_file (str): Path to the YAML configuration file.

        Raises:
            FileNotFoundError: If the specified YAML file does not exist.
            ValueError: If the YAML file cannot be loaded or is invalid.
        """
        self.map_file = Path(map_file).resolve()  # Resolve to absolute path
        if not self.map_file.exists():
            raise FileNotFoundError(f"Configuration file '{self.map_file.name}' not found.")

        try:
            with (self.map_file).open("r") as file:
                self.map = yaml.safe_load(file)
                if not isinstance(self.map, dict):
                    raise ValueError(f"Configuration file '{self.map_file}' is not valid YAML.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file '{self.map_file}': {e}")
        
    def prepare_robot_environment(self, direction, yaml_file="configs/robot_config.yaml"):
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
        Dynamically insert labware and module setup into the script using the deckSetup from YAML.
        Supports dynamic slot mappings and handles each section separately.
        """
        deck_setup = self.map.get("deckSetup", {})
        robot_type = "ot2" if reverse else "flex"

        # Handle trash setup
        trash_config = deck_setup.get("trash", {})
        self._handle_trash(script, trash_config, robot_type)

        # Handle tipracks
        tipracks_config = deck_setup.get("tipracks", {})
        self._handle_tipracks(script, tipracks_config, robot_type)

        # Handle tuberacks
        tuberacks_config = deck_setup.get("tuberacks", {})
        self._handle_tuberacks(script, tuberacks_config, robot_type)

        # Handle thermocycler
        thermocycler_config = deck_setup.get("thermocycler", {})
        self._handle_thermocycler(script, thermocycler_config)

        # Handle magnetic block
        magnetic_block_config = deck_setup.get("magnetic_block", {})
        self._handle_magnetic_block(script, magnetic_block_config, robot_type)

        # Handle custom files
        custom_files = self.map.get("customFiles", [])
        self._handle_custom_files(script, custom_files)

        return script

    def _handle_trash(self, script, config, robot_type):
        """
        Handle trash setup dynamically based on robot type.
        """
        slot = self.get_slot(config.get("slot"), robot_type)
        setup_code = config.get("setup_code", {}).get(robot_type, "").format(slot=slot)

        if setup_code and not re.search(re.escape(setup_code), script):
            script = re.sub(
                r"(protocol\.comment\('Gripper required for labware transfer'\))",
                rf"{setup_code}\n    \1",
                script
            )
        return script

    def _handle_tipracks(self, script, config, robot_type):
        """
        Handle tiprack setup dynamically.
        """
        for slot, location in config.get("slot", {}).items():
            name = "opentrons_96_tiprack_20ul" if "20" in location else "opentrons_96_tiprack_300ul"
            variable = f"tiprack_{slot}"
            setup_code = f"{variable} = protocol.load_labware('{name}', '{location}')"

            if not re.search(re.escape(setup_code), script):
                script = re.sub(
                    r"(protocol\.comment\('Gripper required for labware transfer'\))",
                    rf"{setup_code}\n    \1",
                    script
                )
        return script

    def _handle_tuberacks(self, script, config, robot_type):
        """
        Handle tuberacks setup dynamically.
        """
        for name, rack_config in config.items():
            slot = self.get_slot(rack_config.get("slot"), robot_type)
            setup_code = f"{name} = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap', '{slot}')"
            if not re.search(re.escape(setup_code), script):
                script = re.sub(
                    r"(protocol\.comment\('Gripper required for labware transfer'\))",
                    rf"{setup_code}\n    \1",
                    script
                )
                
    def _handle_thermocycler(self, script, config):
        """
        Handle thermocycler setup and configuration dynamically.
        """
        if not config:
            return script

        # Load thermocycler module
        name = next(iter(config.get("name", {}).values()), "thermocyclerModuleV2")
        setup_code = f"tc_mod = protocol.load_module('{name}')"
        if not re.search(re.escape(setup_code), script):
            script = re.sub(
                r"(protocol\.comment\('Gripper required for labware transfer'\))",
                rf"{setup_code}\n    \1",
                script
            )

        # Add lid temperature configuration
        lid_temperature = config.get("lid_temperature")
        if lid_temperature:
            script += f"\n    tc_mod.set_lid_temperature({lid_temperature})"

        # Add block temperature and max volume configuration
        block_temperature = config.get("block_temperature")
        max_volume = config.get("max_volume", 100)  # Default to 100 if not specified
        if block_temperature:
            script += f"\n    tc_mod.set_block_temperature({block_temperature}, block_max_volume={max_volume})"

        # Handle PCR profile execution
        if "pcr_profile" in config:
            pcr_profile = config["pcr_profile"]
            script += "\n    tc_mod.execute_profile(steps={steps}, repetitions={reps})".format(
                steps=pcr_profile["steps"], reps=pcr_profile["repetitions"]
            )

        # Handle post-PCR block temperature and hold time
        if "post_pcr" in config:
            post_pcr = config["post_pcr"]
            script += f"\n    tc_mod.set_block_temperature({post_pcr['temperature']}, hold_time_minutes={post_pcr['hold_time_minutes']}, block_max_volume={max_volume})"

        return script
    
    def _handle_magnetic_block(self, script, config, robot_type):
        """
        Handle magnetic block setup dynamically.
        """
        slot = self.get_slot(config.get("slot"), robot_type)
        name = next(iter(config.get("name", {}).values()), "magneticModuleV1")
        setup_code = f"mag_mod = protocol.load_module('{name}', '{slot}')"
        if not re.search(re.escape(setup_code), script):
            script = re.sub(
                r"(protocol\.comment\('Gripper required for labware transfer'\))",
                rf"{setup_code}\n    \1",
                script
            )
#
    def _handle_custom_files(self, script, custom_files):
        """
        Handle loading custom labware definitions dynamically.
        """
        for custom_file in custom_files:
            path = custom_file.get("path")
            variable = custom_file.get("variable")
            if path and variable:
                setup_code = f"{variable} = protocol.load_labware_from_definition_file('{path}')"
                if not re.search(re.escape(setup_code), script):
                    script = re.sub(
                        r"(protocol\.comment\('Gripper required for labware transfer'\))",
                        rf"{setup_code}\n    \1",
                        script
                    )

    def get_slot(self, slot_mapping, robot_type):
        """
        Retrieve the appropriate slot from a 'key: value' style mapping.
        """
        if not slot_mapping or not isinstance(slot_mapping, dict):
            raise ValueError("Invalid slot mapping format in YAML.")
        return next((slot_mapping[k] if robot_type == "flex" else k for k in slot_mapping), None)


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
        Update command syntax dynamically based on YAML mappings.
        """
        commands_map = self.map.get("commands", {})
        deck_setup = self.map.get("deckSetup", {})
        robot_type = "ot2" if reverse else "flex"

        # Resolve trash configuration
        trash_config = deck_setup.get("trash", {})
        trash_name = trash_config.get("name", "")
        trash_slot = self.get_slot(trash_config.get("slot"), robot_type)
        trash_variable = trash_config.get("variable", "trash")
        drop_tip_location = self.get_slot(trash_config.get("dropTipLocation"), robot_type)

        # Ensure trash setup exists in the script if needed
        trash_setup_code = f"{trash_variable} = protocol.load_labware('{trash_name}', '{trash_slot}')"
        if trash_variable not in script:
            # Standardize indentation
            script = re.sub(
                r"(protocol\.comment\('Gripper required for labware transfer'\))",
                rf"    {trash_setup_code}\n    \1",
                script
            )
        # Handle thermocycler commands separately
        thermocycler_config = deck_setup.get("thermocycler", {})
        script = self._handle_thermocycler_commands(script, thermocycler_config, commands_map, reverse)

        # General command transformations
        for command, details in commands_map.items():
            if command in ["set_block_temperature", "set_lid_temperature"]:
                continue  # Skip thermocycler commands

            from_command = details.get("from", "")
            to_command = details.get("to", "")

            if from_command and to_command:
                if reverse:
                    # Reverse transformation
                    script = re.sub(re.escape(to_command), from_command, script)
                else:
                    # Forward transformation, resolve placeholders dynamically
                    resolved_command = to_command.format(
                        trash_variable=trash_variable,
                        dropTipLocation=drop_tip_location
                    )
                    script = re.sub(re.escape(from_command), resolved_command, script)

        return script
                            
    def _handle_thermocycler_commands(self, script, thermocycler_config, commands_map, reverse):
        """
        Transform thermocycler-specific commands based on YAML mappings with standardized indentation.
        """
        block_temperature = thermocycler_config.get("block_temperature", "")
        lid_temperature = thermocycler_config.get("lid_temperature", "")

        for command in ["set_block_temperature", "set_lid_temperature"]:
            details = commands_map.get(command, {})
            from_command = details.get("from", "")
            to_command = details.get("to", "")

            if from_command and to_command:
                if reverse:
                    # Reverse transformation
                    script = re.sub(re.escape(to_command), from_command, script)
                else:
                    # Standardize indentation for inserted commands
                    resolved_command = to_command.format(
                        block_temperature=block_temperature,
                        lid_temperature=lid_temperature
                    )
                    script = re.sub(re.escape(from_command), f"{resolved_command}", script)

        return script
    
    def fix_indentation_with_black(self, script):
        """
        Use black to reformat the script, ensuring consistent indentation.
        """
        if not isinstance(script, str):
            raise ValueError("Expected script content to be a string.")
        return format_str(script, mode=FileMode())
        
    def transform(self, input_file, output_file, reverse=False):
        """
        Transform the script based on the direction.
        """
        # Get the script's directory
        script_dir= str(Path(__file__).parent)
        # Resolve full paths for input and output files
        input_file_path = f"{script_dir}/{input_file}"
        output_file_path = f"{script_dir}/{output_file}"
        input_file_path = Path(input_file_path)
        output_file_path = Path(output_file_path)


        # Check if the input file exists
       # input_file_path = Path(input_file)  # Convert string to Path
        if not input_file_path.exists():
            print(f"Error: {input_file_path.name} does not exist at {(input_file_path.resolve())._str}")
            return
        
        # Read the input file
        try:
            with input_file_path.open("r") as infile:
                script = infile.read()
        except Exception as e:
            print(f"Error reading input file '{input_file_path.name}': {e}")
            return
    
        # Ensure necessary files exist and are valid
        direction = "-of" if not reverse else "-fo"
        #self.prepare_robot_environment(direction)

        # Apply transformations
        try:
            script = self.setup_deck(script, reverse)
            script = self.apply_metadata_and_requirements(script, reverse)
            script = self.apply_labware_changes(script, reverse)
            script = self.apply_pipette_changes(script, reverse)
            script = self.apply_command_changes(script, reverse)
            script = self.apply_variable_change(script, reverse)
            #  validate and fix inconsistent indentation
            #script = self.fix_indentation_with_black(script)  # Use autopep8
        except Exception as e:
            print(f"Error during transformation: {e}")
            return
        
        # Write the transformed script to the output file
        try:
            output_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists
            with output_file_path.open("w") as outfile:
                outfile.write(script)
            print(f"Transformation complete! Saved to '{output_file_path.resolve()}'")
        except Exception as e:
            print(f"Error writing output file '{output_file_path.name}': {e}")
        print(f"Transformation complete! Saved to {(output_file_path.resolve())._str}")

if __name__ == "__main__":
    import sys
    from pathlib import Path

    def print_usage_and_exit():
        print("Usage: python transform.py --reaction <clip|purification|assembly|transformation> <direction: -of|-fo> <input_script.py> <output_script.py>")
        sys.exit(1)

    # Ensure sufficient arguments are provided
    if len(sys.argv) != 6 or "--reaction" not in sys.argv:
        print_usage_and_exit()

    # Extract and validate arguments
    try:
        reaction_index = sys.argv.index("--reaction")
        reaction = sys.argv[reaction_index + 1]
        if reaction not in ["clip", "purification", "assembly", "transformation"]:
            raise ValueError(f"Invalid reaction type: '{reaction}'.")

        # Extract remaining arguments explicitly
        direction = sys.argv[reaction_index + 2]
        input_script = sys.argv[reaction_index + 3]
        output_script = sys.argv[reaction_index + 4]

        if direction not in ["-of", "-fo"]:
            raise ValueError(f"Invalid direction: '{direction}'. Use '-of' or '-fo'.")

        # Validate YAML, input, and output paths
        yaml_file = Path(f"configs/{reaction}.yaml").resolve(strict=True)
        input_script_path = Path(input_script).resolve(strict=True)
        output_script_path = Path(output_script).resolve(strict=False)

        if not yaml_file.exists():
            raise FileNotFoundError(f"YAML file '{yaml_file}' for reaction '{reaction}' not found.")
        if not input_script_path.exists():
            raise FileNotFoundError(f"Input script file '{input_script}' not found.")
        if not output_script_path.parent.exists():
            raise FileNotFoundError(f"Output script directory '{output_script_path.parent}' does not exist.")

        # Instantiate the transformer
        transformer = GenericTransformer(yaml_file)

    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        print_usage_and_exit()

    # Perform transformation based on the direction
    try:
        if direction == "-of":
            transformer.transform(input_script, output_script, reverse=False)
        elif direction == "-fo":
            transformer.transform(input_script, output_script, reverse=True)
    except Exception as e:
        print(f"Error during transformation: {e}")
        sys.exit(1) 
