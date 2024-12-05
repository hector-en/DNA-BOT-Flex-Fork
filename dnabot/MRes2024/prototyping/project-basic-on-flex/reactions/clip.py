from .base import ReactionBase

class ClipReaction(ReactionBase):
    
    """
    Handles the clip reaction logic, including labware setup and protocol execution.
    Inherits shared functionality from BaseReaction.
    """
    
    def run(self, protocol):
        """
        Execute the clip reaction using the provided protocol context.
        """
        # Initialize reaction-specific settings
        thermo_temp = self.parameters['parameters']['thermo_temp']
        aspirate_speed = self.globals['globals']['pipette_speed']['aspirate']
        dispense_speed = self.globals['globals']['pipette_speed']['dispense']
        clip_dict = self.parameters['parameters']['clips_dict']
        tiprack_slots = self.globals['globals']['default_tipracks']
        plate_type = self.globals['globals']['default_plate_type']

        print(f"Running Clip Reaction at {thermo_temp}°C...")
        print(f"Aspirate Speed: {aspirate_speed}, Dispense Speed: {dispense_speed}")

        # Load labware
        tipracks = [protocol.load_labware("opentrons_96_tiprack_20ul", slot) for slot in tiprack_slots]
        clip_plate = protocol.load_labware(plate_type, '2')

        # Load pipette
        pipette = protocol.load_instrument(
            "p20_single_gen2",
            mount='right',
            tip_racks=tipracks
        )

        # Set pipette speed
        pipette.flow_rate.aspirate = aspirate_speed
        pipette.flow_rate.dispense = dispense_speed

        # Example: Working with the clips_dict
        prefixes = clip_dict['prefixes_wells']
        suffixes = clip_dict['suffixes_wells']
        parts = clip_dict['parts_wells']
        water_vols = clip_dict['water_vols']

        # Perform pipetting operations
        protocol.comment("Starting Clip Reaction...")
        for idx, well in enumerate(prefixes):
            pipette.pick_up_tip()
            pipette.transfer(water_vols[idx], clip_plate[well], clip_plate[suffixes[idx]], new_tip='never')
            pipette.transfer(clip_dict['parts_vols'][idx], clip_plate[well], clip_plate[parts[idx]], new_tip='never')
            pipette.drop_tip()
        protocol.comment("Clip Reaction Complete!")
        for command in protocol.commands():
            print(command)

