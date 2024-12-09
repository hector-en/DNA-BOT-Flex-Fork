#CHANGES NECESSARY 
#ideas: go to last two of 12-well instead of first two, less far to travel 
# dispense a little higher up; go like 3 above? in the 96 well 
#note there were some bubbles in the blowout ... don't do blowout for PBS 

from opentrons import simulate
from opentrons import protocol_api
metadata = {'apiLevel': '2.19'}
protocol = simulate.get_protocol_api('2.19')

#metadata
metadata = {
     'apiLevel': '2.19',
     'protocolName': 'Simple code test',
     'description': 'use to evaluate simple pipetting and coding commands'
}

def run(protocol: protocol_api.ProtocolContext):
     
    #Labware
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    reservoir = protocol.load_labware('4ti0131_12_reservoir_21000ul', 2)

    plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', 3)

    #pipettes
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_1])

    t = 0.25 #formerly 0.5

    # you can globally change these, rather than adjusting each line of code separately
    high=1.8
    normal=1.0
    slow=0.5
    vslow=0.25

    p300.pick_up_tip() 
    ##PBS stage 
    for i in range (1,12): 
        print(i)
        p300.aspirate(100, reservoir['A12'].bottom(3),rate=slow)
        protocol.delay(seconds=t)
        p300.dispense(100, plate.rows()[0][i].bottom(3),rate=slow)
        p300.blow_out(rate=vslow)
    p300.drop_tip() 

    ##Fluorescein stage 
    p300.pick_up_tip() 
    p300.mix(200,reservoir['A11'].bottom(3),rate=slow)
    for i in range (0,2):
        p300.aspirate(100, reservoir['A11'].bottom(3),rate=slow) #PROBLEM: NOT A2; still doing A1 
        protocol.delay(seconds=t)
        p300.dispense(100, plate.rows()[0][i].bottom(3),rate=slow)
    p300.mix(3, 50, plate.rows()[0][i], 0.5) #note: we only have to mix 2


    ##Dilution stage 
    for i in range (2,12): 
        p300.aspirate(100, plate.rows()[0][i-1].bottom(3),rate=slow)
        protocol.delay(seconds=t)
        if i == 11: 
            p300.drop_tip()  
        else: 
            p300.dispense(100, plate.rows()[0][i].bottom(3),rate=slow)
            p300.mix(3, 50, plate.rows()[0][i].bottom(3),rate=slow)

    for line in protocol.commands(): 
            print(line)