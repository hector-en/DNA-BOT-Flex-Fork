import os
import re
import sys
import yaml

class GenericTransformer:
    """
    A class to handle generic transformations between OT-2 and Flex scripts using YAML-based configurations.
    """

    def __init__(self, map_file):
        with open(map_file, 'r') as file:
            self.map = yaml.safe_load(file)

    def apply_metadata_changes(self, script, reverse=False):
        """Update metadata in the script."""
        metadata_map = self.map["metadata"]
        if reverse:
            script = re.sub(r"'apiLevel': '.*?'", "'apiLevel': '2.8'", script)
            script = re.sub(r"'protocolName': '.*?'", "'protocolName': 'OT-2 Protocol'", script)
        else:
            script = re.sub(r"'apiLevel': '.*?'", f"'apiLevel': '{metadata_map['apiLevel']}'", script)
            script = re.sub(r"'protocolName': '.*?'", f"'protocolName': '{metadata_map['protocolName']}'", script)
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

        with open(input_file, "r") as infile:
            script = infile.read()

        # Apply transformations
        script = self.apply_metadata_changes(script, reverse)
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
        print("Usage: python transformer.py <input_script.py> <output_script.py> <direction>")
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
