from opentrons import protocol_api

# Generating a dictionary with information about the protocol
metadata = {
# double check which api version Geoff's OT2 is using and change the code accordingly
    "protocolName": "iGEM Fluorescin Serial Dilution",
    "description": """This protocol is the outcome of following the
                   Python Protocol API Tutorial located at
                   https://docs.opentrons.com/v2/tutorial.html. It takes a
                   solution and progressively dilutes it by transferring it
                   stepwise across a plate.""",
    "author": "Team1"}

requirements = {"robotType": "OT-2", "apiLevel": "2.19"}
# ^necessary if you’re using API version 2.15 or greater.]

#Coding the Labware & Hardware

# First, creating a new function called 'run' 
def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    reservoir = protocol.load_labware("4ti0131_12_reservoir_21000ul", 2)
    plate = protocol.load_labware("costar3370flatbottomtransparent_96_wellplate_200ul", 3)
#The number (1,2,3) indicates the location on the robot's deck each item is placed

#Pipettes    

    """Next you’ll specify what pipette to use in the protocol. Loading a pipette 
    is done with the load_instrument() method, which takes three arguments: 
    pipette name, the mount it’s installed in, tip rack in use.
    pipettes are loaded in the protocol after tips so that the instrunment
    knows which tip to use with the pipette."""  
#simulation doesn't recognise ot_2_8_channel as a pipette type - put the name of the pipette in here (the example online uses "p300_multi_gen2")    
    left_pipette = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[tips])
    left_pipette.flow_rate.aspirate = 100 
    left_pipette.flow_rate.dispense = 100
    left_pipette.flow_rate.blow_out = 200
    
    left_pipette.well_bottom_clearance.aspirate = 5  # tip is 1 mm above well bottom
    left_pipette.well_bottom_clearance.dispense = 6 
    
# setting fractions of flowrates that can be globally changed rather than changing each value individually
    high=1.8
    normal=1.0
    slow=0.5
    vslow=0.25

    cols = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12"]
# TRANSFERRING FLUORESCIN
# Fluorescin in reservoir A1, PBS in A2.
    left_pipette.pick_up_tip()
    left_pipette.aspirate(200, reservoir['A1'].bottom(1), rate = slow)
    left_pipette.dispense(200, plate['A1'].bottom(2), rate = normal)
    left_pipette.blow_out(plate['A1'].bottom(2))
# This command dispenses in A1, B1, C1...G1, H1 because we are using a multipipette
#saying drop_tip means the robot will automatically put it in the trash just like pick_up_tip - no need to define location!!
    left_pipette.drop_tip()

# TRANSFERRING PBS
    left_pipette.pick_up_tip()
    for i in range(11):
        left_pipette.aspirate(100, reservoir['A2'].bottom(1), rate = slow)
        left_pipette.dispense(100, plate[cols[i+1]].bottom(2), rate = normal)
        left_pipette.blow_out(plate[cols[i+1]].bottom(2))
    left_pipette.drop_tip()
# SERIAL DILUTION
    left_pipette.pick_up_tip()
    for i in range(10):
   #pick up contents of well and tranfer it to next
        left_pipette.aspirate(100, plate[cols[i]].bottom(1), rate = slow)
        left_pipette.dispense(100, plate[cols[i+1]].bottom(2), rate = normal)
        left_pipette.blow_out(plate[cols[i+1]].bottom(2))
    #mix solution up and down 
        # 
        left_pipette.aspirate(100, plate[cols[i+1]].bottom(1), rate = slow)
        left_pipette.dispense(100, plate[cols[i+1]].bottom(2), rate = normal)
        left_pipette.aspirate(100, plate[cols[i+1]].bottom(1), rate = slow)
        left_pipette.dispense(100, plate[cols[i+1]].bottom(2), rate = normal)
        left_pipette.aspirate(100, plate[cols[i+1]].bottom(1), rate = slow)
        left_pipette.dispense(100, plate[cols[i+1]].bottom(2), rate = normal)
        left_pipette.blow_out(plate[cols[i+1]].bottom(2))
    left_pipette.drop_tip()
