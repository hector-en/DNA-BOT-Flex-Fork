from opentrons import protocol_api

# Metadata
metadata = {
    'protocolName': 'Fluorescence Calibration Protocol',
    'author': 'Pablo',
    'description': 'Automates Fluorescence calibrations (assumes fluorescein is used).',
    'apiLevel': '2.15'
}

def run(protocol: protocol_api.ProtocolContext):
    #Labware
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    reservoir = protocol.load_labware('4ti0131_12_reservoir_21000ul' , 2) #A1 PBS, A2 fluorescein
    plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', 3) 

    # rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G','H']
    # columns = [1,2,3,4,5,6,7,8,9,10,11,12]

    #pipettes
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_1])
    # Adjust if needed
    # p300.flow_rate.aspirate = 80
    # p300.flow_rate.dispense = 40
    # p300.flow_rate.blow_out = 150

    # Put 100 PBS in wells A2-A12
    p300.pick_up_tip()
    for i in range(1, 12):
        p300.transfer(
            100,
            reservoir.wells_by_name()['A1'].bottom(7),
            plate.rows_by_name()['A'][i],
            new_tip='never'
        )
    p300.drop_tip()

    # Transfer Reference stock 1X into well A1
    p300.pick_up_tip()
    p300.transfer(
        200,
        reservoir.wells_by_name()['A2'].bottom(5),
        plate.wells_by_name()['A1'],
        new_tip='never'
    )

    # Perform serial dilutions: A1 -> A2, A2 -> A3, ..., A10 -> A11
    for i in range(1, 11):
        p300.transfer(
            100,
            plate.rows_by_name()['A'][i - 1],
            plate.rows_by_name()['A'][i],
            mix_after=(5, 50),
            new_tip='never'
        )

    # Aspirate from the last well (A11)
    p300.aspirate(100, plate.wells_by_name()['A11'])
    #p300.dispense(100, reservoir.wells_by_name()['A5'])

    # Drop the tip after all transfers are complete
    p300.drop_tip()
