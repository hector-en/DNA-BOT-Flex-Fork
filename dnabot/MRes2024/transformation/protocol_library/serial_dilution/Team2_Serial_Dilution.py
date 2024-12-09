from opentrons import protocol_api
from opentrons import simulate
import numpy as np

# metadata
metadata = {
    'apiLevel': '2.15',
    'protocolName': 'First_Protocol_23',
    'description': 'test for friday 27 nov',
    }

protocol = simulate.get_protocol_api('2.15')

def run(protocol: protocol_api.ProtocolContext):

    reservoir = protocol.load_labware("4ti0131_12_reservoir_21000ul", 1)
    plate = protocol.load_labware("costar3370flatbottomtransparent_96_wellplate_200ul", 2)
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 3)

    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[tips])

    p300.well_bottom_clearance.aspirate = 4
    p300.well_bottom_clearance.dispense = 5
    #

    p300.flow_rate.aspirate = 100 
    p300.flow_rate.dispense = 100
    p300.flow_rate.blow_out = 200

    high=1.8
    normal=1.0
    slow=0.5
    vslow=0.25

    p300.pick_up_tip()

    col = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

    #pbs
    for i in range(11):
        p300.aspirate(100, reservoir['A1'].bottom(7), rate=slow)
        p300.dispense(100, plate[col[i+1]].bottom(2), rate=vslow, push_out=2)
        #p300.blow_out(plate[col[i+1]].bottom(7))

    p300.drop_tip()
    p300.pick_up_tip()

    #stock
    p300.aspirate(200, reservoir['A2'].bottom(3), rate=slow)
    p300.dispense(200, plate['A1'].bottom(2), rate=vslow)
    p300.blow_out(plate['A1'].bottom(7))

    #dilute
    for x in range(10):
        p300.aspirate(100, plate[col[x]].bottom(1), rate=slow)
        #p300.touch_tip(plate[col[x]].bottom(3))
        p300.dispense(100, plate[col[x+1]].bottom(2), rate=vslow)
        p300.mix(3, 50, plate[col[x+1]].bottom(2), rate=slow)
        p300.blow_out(plate[col[x+1]].bottom(7))

    p300.aspirate(100, plate['A11'].bottom(1), rate=slow)
    p300.drop_tip()

#for line in protocol.commands(): 
#    print(line)
