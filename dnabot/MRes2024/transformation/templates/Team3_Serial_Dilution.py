from opentrons import protocol_api

metadata = {
    "apiLevel": "2.16",
    "protocolName": "20241127 Trial-5",
    "author": "zlin"
    }

def run(protocol: protocol_api.ProtocolContext):
    # 1. Labware
    tips_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    reservoir = protocol.load_labware('4ti0131_12_reservoir_21000ul', 2)
    plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', 3)
    
    # 2. liquids
    PBS = reservoir['A1']
    Fluorescine = reservoir['A2']

    # 3. Pipettes
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks = [tips_1])
    
    # 4. Global parameters
    # 4.1 Well clearances
    p300.well_bottom_clearance.aspirate = 1  
    p300.well_bottom_clearance.dispense = 5 
    # 4.2 Pipette flow rates
    p300.flow_rate.aspirate = 100 
    p300.flow_rate.dispense = 100
    p300.flow_rate.blow_out = 100
    # 4.3 Self-defined rate fraction
    high=1.8
    normal=1.0
    slow=0.75
    vslow=0.5

    # 5. Pipetting command
    row = plate.rows()[0]
    p300.pick_up_tip()
    # 5.1 PBS addition
    for well in row[1:12]:   
        p300.aspirate(100, PBS, rate=slow)
        p300.dispense(100, well, rate=slow)
        p300.blow_out()
    p300.drop_tip()
    # 5.2 Fluorescine addition
    p300.pick_up_tip()
    p300.aspirate(200, Fluorescine, rate=slow)
    p300.dispense(200, row[0], rate=slow)
    p300.blow_out()
    # 5.3 Serial dilution
    for j in range(10):
        p300.aspirate(100, row[j], rate=slow)
        p300.dispense(100, row[j+1], rate=slow)
        p300.blow_out()
        p300.touch_tip(radius=0.9, v_offset=-5, speed=10)
        p300.mix(3, 50, rate=slow)
    p300.aspirate(100, row[10], rate=slow)
    p300.drop_tip()


        
