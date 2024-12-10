from opentrons import protocol_api

# Metadata
metadata = {
    'protocolName': 'iGEM Serial Dilution_height_optimised',
    'author': 'Jacob, Justin, Luc, Yiming',
    'description': 'Serial dilution of a fluorescent stock solution in a 96-well plate',
    'apiLevel': '2.13'}

def run(protocol: protocol_api.ProtocolContext):
    # labware
        
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 1) # not sure what to do since might need second tip rack

    reservoir = protocol.load_labware('nest_12_reservoir_15ml', 2) # put both liquid in same reservoir, Stock in Column 1 index 0, and PBS in column 2 index 1
    plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 3) 

    p300 = protocol.load_instrument('p300_multi_gen2',  'left', tip_racks=[tiprack_1])


    # Stock into first column
    p300.pick_up_tip()
    p300.transfer(200, reservoir.wells_by_name()["A1"].bottom(-3), plate.wells_by_name()['A1'].bottom(1), new_tip='never')
    p300.drop_tip()
    
    # PBS in colunn 2-12 (index 1-11)
    
    p300.pick_up_tip()
    for i in range(1,12):
        p300.transfer(100, reservoir.wells_by_name()["A2"].bottom(0), plate.rows_by_name()["A"][i], new_tip = "never")
 
    # Serial dilution
    
    for i in range (1,11):
        p300.transfer(100, plate.rows_by_name()["A"][i-1].bottom(1), plate.rows_by_name()["A"][i].bottom(1), mix_after=(3,150), new_tip='never')
    
    # discard 100 from last column
    
    p300.transfer(100, plate.rows_by_name()['A'][10].bottom(1), reservoir.columns()[11], new_tip='never')
