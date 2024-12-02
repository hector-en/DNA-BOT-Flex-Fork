import os
import sys
import re

class OT2ToFlexTransformer:
    """
    A class to handle the transformation of OT-2 scripts to Flex-compatible scripts
    and vice versa, including labware mappings, pipette updates, and specific configurations.
    """

    def __init__(self):
        # Define mappings for labware and pipettes
        self.labware_map = {
            "opentrons_96_tiprack_300ul": "opentrons_flex_96_tiprack_300ul",
            "nest_96_wellplate_100ul_pcr_full_skirt": "flex_96_wellplate_100ul_pcr_full_skirt"
        }
        self.pipette_map = {
            "p300_single": "p300_single_gen2",
            "p1000_single": "p1000_single_gen2"
        }

        # Define other transformation rules
        self.metadata_transform = {
            "apiLevel": "2.15",
            "protocolName": "Flex-Compatible Transformation Protocol"
        }

    def transform_labware(self, script: str, reverse: bool = False) -> str:
        """
        Update labware definitions in the script.

        Args:
            script (str): Original script content.
            reverse (bool): Reverse the transformation (Flex to OT-2).

        Returns:
            str: Script with updated labware definitions.
        """
        map_to_use = self.labware_map if not reverse else {v: k for k, v in self.labware_map.items()}
        for old, new in map_to_use.items():
            script = script.replace(old, new)
        return script

    def transform_pipettes(self, script: str, reverse: bool = False) -> str:
        """
        Update pipette definitions in the script.

        Args:
            script (str): Original script content.
            reverse (bool): Reverse the transformation (Flex to OT-2).

        Returns:
            str: Script with updated pipette definitions.
        """
        map_to_use = self.pipette_map if not reverse else {v: k for k, v in self.pipette_map.items()}
        for old, new in map_to_use.items():
            script = script.replace(old, new)
        return script

    def transform_metadata(self, script: str, reverse: bool = False) -> str:
        """
        Update metadata in the script.

        Args:
            script (str): Original script content.
            reverse (bool): Reverse the transformation (Flex to OT-2).

        Returns:
            str: Script with updated metadata.
        """
        if not reverse:
            for key, value in self.metadata_transform.items():
                script = re.sub(rf"'{key}': '.*?'", f"'{key}': '{value}'", script)
        else:
            script = re.sub(r"'apiLevel': '.*?'", "'apiLevel': '2.8'", script)
            script = re.sub(r"'protocolName': '.*?'", "'protocolName': 'OT-2 Transformation Protocol'", script)
        return script

    def add_flex_features(self, script: str) -> str:
        """
        Add Flex-specific features, such as liquid detection.

        Args:
            script (str): Original script content.

        Returns:
            str: Script with Flex-specific features added.
        """
        flex_features = """
    # Flex-Specific Enhancements
    def liquid_detection(pipette, well):
        try:
            pipette.aspirate(1, well.bottom(1))
            pipette.dispense(1, well.bottom(1))
            return True
        except Exception as e:
            print(f"Liquid detection failed: {e}")
            return False

    if not liquid_detection(pipette, plate.wells_by_name()['A1']):
        raise RuntimeError('Liquid detection failed for well A1')
        """
        return script.replace("# Transformation Workflow", f"# Transformation Workflow{flex_features}")

    def transform(self, input_file: str, output_file: str, reverse: bool = False):
        """
        Transform a script from OT-2 to Flex or vice versa.

        Args:
            input_file (str): Path to the input script.
            output_file (str): Path to save the transformed script.
            reverse (bool): Reverse the transformation (Flex to OT-2).
        """
        if not os.path.exists(input_file):
            print(f"Error: {input_file} does not exist.")
            return

        print(f"Reading script from: {input_file}")
        with open(input_file, 'r') as infile:
            script = infile.read()

        # Apply transformations
        script = self.transform_metadata(script, reverse=reverse)
        script = self.transform_labware(script, reverse=reverse)
        script = self.transform_pipettes(script, reverse=reverse)

        if not reverse:
            script = self.add_flex_features(script)

        print(f"Writing transformed script to: {output_file}")
        with open(output_file, 'w') as outfile:
            outfile.write(script)

        print("Transformation complete!")

# Main Execution
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python transformation.py <input_script.py> <output_script.py> <direction>")
        print("<direction>: 'ot2_to_flex' or 'flex_to_ot2'")
        sys.exit(1)

    input_script = sys.argv[1]
    output_script = sys.argv[2]
    direction = sys.argv[3]

    transformer = OT2ToFlexTransformer()

    if direction == "ot2_to_flex":
        transformer.transform(input_script, output_script, reverse=False)
    elif direction == "flex_to_ot2":
        transformer.transform(input_script, output_script, reverse=True)
    else:
        print("Invalid direction. Use 'ot2_to_flex' or 'flex_to_ot2'.")
