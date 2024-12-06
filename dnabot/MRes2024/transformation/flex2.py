from opentrons import protocol_api, simulate

# Metadata
metadata = {
    'protocolName': 'Simulate a Clip Reaction on OT-2 or Flex',
    'description': 'Simulate a Clip Reaction on Flex or Flex'
}
requirements = {
    "robotType": "Flex",
    "apiLevel": "2.19"
}

# Example Clips Dictionary
clips_dict = {
    "prefixes_wells": ["A1", "B1", "C1", "D1"],
    "prefixes_plates": ["2", "2", "2", "2"],
    "suffixes_wells": ["A2", "B2", "C2", "D2"],
    "suffixes_plates": ["2", "2", "2", "2"],
    "parts_wells": ["A3", "B3", "C3", "D3"],
    "parts_plates": ["2", "2", "2", "2"],
    "parts_vols": [1, 1, 1, 1],
    "water_vols": [7.0, 7.0, 7.0, 7.0]
}

def run(protocol: protocol_api.ProtocolContext, simulate=False):
    """
    Run the Clip Reaction protocol, with an optional simulation mode.
    Parameters:
        protocol (ProtocolContext): Context for protocol execution or simulation.
        simulate (bool): If True, run in simulation mode.
    """
    # Deck Setup
    tiprack_50 = protocol.load_labware('opentrons_flex_96_tiprack_50ul', '1')
    plate_96 = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '2')
    trash = protocol.load_labware('opentrons_1_trash_1100ml_fixed', 'A3')
    pipette = protocol.load_instrument('flex_1channel_50', 'right', tip_racks=[tiprack_50])
    protocol.comment('Gripper required for labware transfer')

    # Define wells
    prefixes = plate_96.wells_by_name()
    suffixes = plate_96.wells_by_name()
    parts = plate_96.wells_by_name()

    # Pipetting Logic
    for i in range(len(clips_dict["prefixes_wells"])):
        pipette.pick_up_tip()
        pipette.transfer(
            clips_dict["parts_vols"][i],
            prefixes[clips_dict["prefixes_wells"][i]],
            suffixes[clips_dict["suffixes_wells"][i]],
            new_tip='never'
        )
        pipette.drop_tip(trash['A1'])

    # Output simulation commands
    if simulate:
        print("Simulated Commands:")
        for command in protocol.commands():
            print(command)

# Simulation Example
if __name__ == "__main__":
    # Create a simulated protocol context
    protocol = simulate.get_protocol_api('2.15')
    run(protocol, simulate=True)