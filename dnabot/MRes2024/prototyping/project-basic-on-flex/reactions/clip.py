from .base import ReactionBase

class ClipReaction(ReactionBase):
    def run(self, protocol):
        """
        Execute the clip reaction using the provided protocol context.
        Dynamically handles metadata for OT-2 and Flex.
        """
        # Ensure protocol metadata exists
        if not hasattr(protocol, "metadata"):
            protocol.metadata = {}  # Add metadata attribute if missing in simulation

        # Determine if it's Flex or OT-2 based on simulation or external input
        robot_type = "Flex" if protocol.is_simulating() else "OT-2"

        # Populate metadata dynamically based on the robot type
        if robot_type == "Flex":
            protocol.metadata.update({
                "protocolName": "Updated Protocol",
                "description": "Simulate a Clip Reaction on OT-2 or Flex",
            })
            protocol.requirements = {"robotType": "Flex", "apiLevel": "2.20"}
        else:
            protocol.metadata.update({
                "apiLevel": "2.18",
                "protocolName": "Clip Reaction Simulation",
                "description": "Simulate a Clip Reaction on OT-2 or Flex"
            })
            
        

        print(f"Running Clip Reaction on {robot_type}...")

        # Reaction-specific parameters
        thermo_temp = self.parameters['parameters']['thermo_temp']
        clip_dict = self.parameters['parameters']['clips_dict']
        tiprack_slots = self.globals['globals']['default_tipracks']
        plate_type = self.globals['globals']['default_plate_type']

        # Adjust trash slot dynamically
        trash_slot = "A1" if robot_type == "Flex" else "12"
        clip_plate_slot = "2"

        # Load labware
        tipracks = [protocol.load_labware("opentrons_96_tiprack_20ul", slot) for slot in tiprack_slots]
        clip_plate = protocol.load_labware(plate_type, clip_plate_slot)
        #trash = protocol.load_labware("opentrons_1_trash_1100ml_fixed", trash_slot) #flex

        # Load pipette
        pipette = protocol.load_instrument(
            "p20_single_gen2",
            mount='right',
            tip_racks=tipracks
        )

        # Perform pipetting operations
        protocol.comment("Starting Clip Reaction...")
        prefixes = clip_dict['prefixes_wells']
        suffixes = clip_dict['suffixes_wells']
        parts = clip_dict['parts_wells']
        for idx, well in enumerate(prefixes):
            pipette.pick_up_tip()
            pipette.transfer(clip_dict['water_vols'][idx], clip_plate[well], clip_plate[suffixes[idx]], new_tip='never')
            pipette.transfer(clip_dict['parts_vols'][idx], clip_plate[well], clip_plate[parts[idx]], new_tip='never')
            #pipette.drop_tip(trash.wells_by_name()['A1']) #flex
            pipette.drop_tip() #ot-2
        protocol.comment("Clip Reaction Complete!")
        for command in protocol.commands():
            print(command)
