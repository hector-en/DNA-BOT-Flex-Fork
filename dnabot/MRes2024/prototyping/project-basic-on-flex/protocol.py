#    protocol.py
#
#    Manages and executes Opentrons protocols in various modes  using global and mode-specific configurations.
#   
#   **Modes Supported:
#       - 'clip'
#       - 'purification'
#       - 'transformation'
#       - 'pcr'
#
#    **Key Features**:
#    **ProtocolMode Class:
#    - Loads global and mode-specific YAML configurations.
#    - Supports simulation or real robot execution.
#    - Dynamically maps modes to their respective reaction classes.
#
#    **initialize_protocol:
#    Sets up the protocol context for simulation or runtime.
#
#    **run:
#    Executes the specified mode by initializing the corresponding reaction class (clip,pcr,...).
#    
#    **Error Handling:
#    Ensures required files are present.
#    Validates mode and initializes the protocol context before execution.
#
#    **Future Scope:
#    Extend with additional reaction classes or runtime arguments for enhanced flexibility. 
# 
#   **Usage Scenarios for protocol.py
#   1. Simulate Reaction: Validate logic without robot.
#      Command: python protocol.py --mode clip --global-config global_config.yaml --mode-config mode_configs/clip.yaml --simulate
#   2. Execute Reaction on Robot: Run protocol on connected Opentrons.
#      Command: python protocol.py --mode purification --global-config global_config.yaml --mode-config mode_configs/purification.yaml
#   3. Add Custom Reaction: Define new reaction logic in `reactions/`, create mode config, and update `reaction_class` mapping.
#      Command: python protocol.py --mode custom --global-config global_config.yaml --mode-config mode_configs/custom.yaml
#   4. Run Unit Tests: Validate reactions and parameters.
#      Command: python -m unittest tests/test_clip_reaction.py
#   **5. Generate Python Protocol File: Simulate and save as .py file.
#      Command: python protocol.py --mode clip --global-config global_config.yaml --mode-config mode_configs/clip.yaml > robot_clip_protocol.py
# 

import yaml
from reactions.clip import ClipReaction
#from reactions.purification import PurificationReaction
#from reactions.transformation import TransformationReaction
#from reactions.pcr import PCRReaction


class ProtocolMode:
    """
    ProtocolMode Class

    Handles the initialization and execution of Opentrons protocols for various modes, such as 'clip', 'purification', 'transformation', and 'pcr'. 
    The class dynamically loads global and mode-specific configurations and runs the appropriate reaction logic.

    Methods:
    1. __init__(global_config, mode_config, api_version="2.13"):
        - Initializes ProtocolMode with the provided configuration files and API version.
        - Parameters:
            global_config (str): Path to the global YAML configuration file.
            mode_config (str): Path to the mode-specific YAML configuration file.
            api_version (str): The API version of the Opentrons robot.

    2. initialize_protocol(simulation=True):
        - Sets up the protocol context for simulation or real robot execution.
        - Parameters:
            simulation (bool): True for simulation; False for robot execution.

    3. run(mode):
        - Executes the specified reaction mode by initializing the corresponding reaction class.
        - Parameters:
            mode (str): Reaction mode to execute (e.g., 'clip').
        - Errors:
            RuntimeError: If the protocol context is not initialized.
            ValueError: If an invalid mode is provided.

    Command-line Interface:
    - Simulate Reaction:
        python protocol.py --mode clip --global-config global_config.yaml --mode-config mode_configs/clip.yaml --simulate
    - Execute Reaction:
        python protocol.py --mode purification --global-config global_config.yaml --mode-config mode_configs/purification.yaml
    - Add Custom Reaction:
        Create new logic in `reactions/`, update `mode_configs/custom.yaml`, and map it in ProtocolMode.
    """


    def __init__(self, global_config, mode_config, api_version="2.15"):
        """
        Initialize with global and mode-specific configurations.

        Args:
            global_config (str): Path to the global YAML configuration file.
            mode_config (str): Path to the mode-specific YAML configuration file.
            api_version (str): Opentrons API version to use.
        """
        # Load global and mode-specific configurations
        with open(global_config, 'r') as global_file:
            self.global_config = yaml.safe_load(global_file)
        with open(mode_config, 'r') as mode_file:
            self.mode_config = yaml.safe_load(mode_file)
        
        self.api_version = api_version
        self.protocol = None  # Protocol context initialized later

    def initialize_protocol(self, simulation=True):
        """
        Initialize protocol context for simulation or robot execution.

        Args:
            simulation (bool): True for simulation; False for robot execution.
        """
        if simulation:
            from opentrons import simulate
            print("Initializing in simulation mode...")
            self.protocol = simulate.get_protocol_api(self.api_version)
        else:
            print("Running on robot. Protocol context will be provided by runtime.")

    def run(self, mode):
        """
        Execute the specified reaction mode.

        Args:
            mode (str): The mode to run (e.g., 'clip').

        Raises:
            RuntimeError: If protocol context is not initialized.
            ValueError: If the specified mode is invalid.
        """        
        if not self.protocol:
            raise RuntimeError("Protocol context is not initialized. Call initialize_protocol first.")

        reaction_class = {
            "clip": ClipReaction
            # Uncomment for other modes:
            # "purification": PurificationReaction,
            # "transformation": TransformationReaction,
            # "pcr": PCRReaction,
        }.get(mode)

        if not reaction_class:
            raise ValueError(f"Invalid mode '{mode}' specified. Valid modes are: clip, purification, transformation, pcr.")

        # Instantiate the reaction class and execute it
        reaction = reaction_class(self.mode_config,self.global_config)
        reaction.run(self.protocol)


if __name__ == "__main__":
    import argparse

    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Run an Opentrons protocol in a specified mode.")
    parser.add_argument("--mode", type=str, required=True, help="The mode to run (e.g., clip, purification, transformation, pcr).")
    parser.add_argument("--global-config", type=str, default="global_config.yaml", help="Path to the global configuration file.")
    parser.add_argument("--mode-config", type=str, required=True, help="Path to the mode-specific configuration file.")
    parser.add_argument("--simulate", action="store_true", help="Run the protocol in simulation mode.")
    args = parser.parse_args()

    # Validate configuration files
    import os
    if not os.path.exists(args.global_config):
        raise FileNotFoundError(f"Global config file not found: {args.global_config}")
    if not os.path.exists(args.mode_config):
        raise FileNotFoundError(f"Mode config file not found: {args.mode_config}")

   # Instantiate the reaction class and execute the reaction
    protocol_mode = ProtocolMode(args.global_config, args.mode_config)
    protocol_mode.initialize_protocol(simulation=args.simulate)
    protocol_mode.run(args.mode) # Protocol is passed here
