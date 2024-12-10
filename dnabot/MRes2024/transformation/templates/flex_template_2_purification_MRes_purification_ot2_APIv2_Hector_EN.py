from opentrons import protocol_api
# Author:  Hector Edu Nseng

# Rename to 'purification_template' and paste into 'template_ot2_scripts' folder in DNA-BOT to use

metadata = {
     'protocolName': 'DNABOT Step 2: Purification (Flex Protocol)',
     'description': 'Implements magbead purification reactions for BASIC assembly using an opentrons Flex'}
requirements = {
    'apiLevel': '2.19',
    'robotType': 'Flex'
}




# example values produced by DNA-BOT for a single construct containing 5 parts, un-comment and run to test the template:
#sample_number=8
#ethanol_well='A3'

# __LABWARES and __PARAMETERS are expected to be redefined by "generate_ot2_script" method
# Test dict
# __LABWARES={"flex_1channel_50": {"id": "flex_1channel_50"}, "flex_1channel_1000": {"id": "flex_8channel_1000"}, "flex_magnetic_block": {"id": "magneticModuleV1"}, "96_tiprack_20ul": {"id": "opentrons_flex_96_tiprack_50ul"}, "96_tiprack_300ul": {"id": "opentrons_flex_96_tiprack_1000ul"}, "opentrons_24_tuberack_nest_1.5ml_snapcap": {"id": "e14151500starlab_opentrons_24_tuberack_nest_1.5ml_snapcap"}, "96_wellplate_200ul_pcr_step_14": {"id": "4ti0960rig_96_wellplate_200ul"}, "96_wellplate_200ul_pcr_step_23": {"id": "4ti0960rig_96_wellplate_200ul"}, "agar_plate_step_4": {"id": "4ti0960rig_96_wellplate_200ul"}, "flex_12_reservoir_15ml": {"id": "4ti0131_12_reservoir_21000ul"}, "flex_deepwell_plate": {"id": "4ti0136_96_wellplate_2200ul"}}
# __PARAMETERS={"purif_magdeck_height": {"value": 20.0}, "purif_wash_time": {"value": 0.5}, "purif_bead_ratio": {"value": 1.8}, "purif_incubation_time": {"value": 5.0}, "purif_settling_time": {"value": 2.0}, "purif_drying_time": {"value": 5.0}, "purif_elution_time": {"value": 2.0}, "transfo_incubation_temp": {"value": 4.0}, "transfo_incubation_time": {"value": 20.0}}

sample_number=6
ethanol_well='A11'
__LABWARES={"flex_1channel_50": {"id": "flex_1channel_50"}, 
            "flex_1channel_1000": {"id": "flex_8channel_1000"}, 
            "flex_magnetic_block": {"id": "magneticBlockV1"}, 
            "96_tiprack_20ul": {"id": "opentrons_flex_96_tiprack_50ul"}, 
            "96_tiprack_300ul": {"id": "opentrons_flex_96_tiprack_1000ul"}, 
            "opentrons_24_tuberack_nest_1.5ml_snapcap": {"id": "e14151500starlab_opentrons_24_tuberack_nest_1.5ml_snapcap"}, 
            "clip_source_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, 
            "clip_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, 
            "flex_mix_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, 
            "final_assembly_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, 
            "transfo_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, 
            "transfo_plate_wo_thermo": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, 
            "flex_agar_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, 
            "flex_12_reservoir_15ml": {"id": "nest_12_reservoir_15ml"}, 
            "flex_deepwell_plate": {"id": "nest_96_wellplate_2ml_deep"}, 
            "12_corning_wellplate": {"id": "corning_96_wellplate_360ul_flat"}}
__PARAMETERS={"clip_keep_thermo_lid_closed": {"value": "No", "id": "No"}, 
              "premix_linkers": {"value": "Yes", "id": "No"}, 
              "premix_parts": {"value": "Yes", "id": "Yes"}, 
              "linkers_volume": {"value": 20}, "parts_volume": {"value": 20}, 
              "thermo_temp": {"value": 4}, 
              "purif_magdeck_height": {"value": 10.8}, 
              "purif_wash_time": {"value": 0.5}, 
              "purif_bead_ratio": {"value": 1.8}, 
              "purif_incubation_time": {"value": 5}, 
              "purif_settling_time": {"value": 2}, 
              "purif_drying_time": {"value": 5}, 
              "purif_elution_time": {"value": 2}, 
              "transfo_incubation_temp": {"value": 4}, 
              "transfo_incubation_time": {"value": 20}}



def run(protocol: protocol_api.ProtocolContext):
# added run function for API verison 2
    trash = protocol.load_trash_bin("A3") 
    # updates 
    MAGNETIC_BLOCK_SLOT = "B3"  # Slot for the Magnetic Block
    MIXING_PLATE_SLOT = "2"     # Initial slot of the mixing plate
    LIQUID_WASTE_SLOT = "A3"    # Slot for the liquid waste
    #MAGBLOCK = protocol.load_labware(__LABWARES['flex_magnetic_block']['id'], MAGNETIC_BLOCK_SLOT)
    def move_with_gripper(protocol, labware, source_slot, target_slot):
        """
        Moves labware using the gripper from source_slot to target_slot.
        """
        protocol.comment(f"Moving {labware.name} from slot {source_slot} to slot {target_slot}.")
        # Ensure the target slot is not already occupied
        if target_slot in protocol.loaded_labwares:
            raise ValueError(f"Target slot {target_slot} is already occupied.")
        protocol.move_labware(labware, target_slot)


    def magbead(
            sample_number,
            ethanol_well,
            elution_buffer_well='A1',
            sample_volume=30,
            bead_ratio=__PARAMETERS['purif_bead_ratio']['value'],
            elution_buffer_volume=40,
            incubation_time=__PARAMETERS['purif_incubation_time']['value'],
            settling_time=__PARAMETERS['purif_settling_time']['value'],
                # if using Gen 2 magentic module, need to change time! see: https://docs.opentrons.com/v2/new_modules.html
                # "The GEN2 Magnetic Module uses smaller magnets than the GEN1 version...this means it will take longer for the GEN2 module to attract beads."
                # Recommended Magnetic Module GEN2 bead attraction time:
                    # Total liquid volume <= 50 uL: 5 minutes
                # this template was written with the Gen 1 magnetic module, as it is compatible with API version 2
            drying_time=__PARAMETERS['purif_drying_time']['value'],
            elution_time=__PARAMETERS['purif_elution_time']['value'],
            sample_offset=0,
            tiprack_type=__LABWARES['96_tiprack_300ul']['id']):

        """

        Selected args:
            ethanol_well (str): well in reagent container containing ethanol.
            elution_buffer_well (str): well in reagent container containing elution buffer.
            sample_offset (int): offset the intial sample column by the specified value.

        """


        ### Constants

        # Pipettes
        PIPETTE_ASPIRATE_RATE = 25
        PIPETTE_DISPENSE_RATE = 150
        TIPS_PER_SAMPLE = 9
        PIPETTE_TYPE = __LABWARES['flex_1channel_1000']['id']
            # new constant for easier swapping between pipette types

        # Tiprack
        CANDIDATE_TIPRACK_SLOTS = ['3', '6', '9', '2', '5']

        # Magnetic Module
        MAGDECK_POSITION = '1'

        # Mix Plate
        MIX_PLATE_TYPE = __LABWARES['flex_mix_plate']['id']
            # modified from custom labware as API 2 doesn't support labware.create anymore, so the old add_labware script can't be used
            # also acts as the type of plate loaded onto the magnetic module
        MIX_PLATE_POSITION = '4'

        # Reagents
        REAGENT_CONTAINER_TYPE = __LABWARES['flex_12_reservoir_15ml']['id']
        REAGENT_CONTAINER_POSITION = '7'

        # Beads
        BEAD_CONTAINER_TYPE = __LABWARES['flex_deepwell_plate']['id']
        BEAD_CONTAINER_POSITION = '8'

        # Settings
        LIQUID_WASTE_WELL = 'A5'
        BEADS_WELL = 'A1'
        DEAD_TOTAL_VOL = 5
        SLOW_HEAD_SPEEDS = {'x': 600 // 4, 'y': 400 // 4, 'z': 125 // 10, 'a': 125 // 10}
        DEFAULT_HEAD_SPEEDS = {'x': 400, 'y': 400, 'z': 125, 'a': 100}
        IMMOBILISE_MIX_REPS = 10
        MAGDECK_HEIGHT = __PARAMETERS['purif_magdeck_height']['value']
        AIR_VOL_COEFF = 0.1
        ETHANOL_VOL = 150
        WASH_TIME = __PARAMETERS['purif_wash_time']['value']
        ETHANOL_DEAD_VOL = 50
        ELUTION_MIX_REPS = 20
        ELUTANT_SEP_TIME = 1
        ELUTION_DEAD_VOL = 2

        ### Errors
        if sample_number > 48:
            raise ValueError('sample number cannot exceed 48')


        ### Loading Tiprack

        # Calculates whether one/two/three/four/five tipracks are needed, which are in slots 3, 6, 9, 2, and 5 respectively
        total_tips = sample_number * TIPS_PER_SAMPLE
        tiprack_num = total_tips // 96 + (1 if total_tips % 96 > 0 else 0)
        slots = CANDIDATE_TIPRACK_SLOTS[:tiprack_num]
        tipracks = [protocol.load_labware(tiprack_type, slot) for slot in slots]
            # changed to protocol.load_labware for API version 2


        ### Loading Pipettes

        pipette = protocol.load_instrument(PIPETTE_TYPE, mount="left", tip_racks=tipracks)
        pipette.aspirate_flow_rate=PIPETTE_ASPIRATE_RATE
        pipette.dispense_flow_rate=PIPETTE_DISPENSE_RATE
            # for reference: default aspirate/dispense flow rate for flex_8channel_1000 is 94 ul/s

        ### Define Labware

        # Magnetic Module
        MAGDECK = protocol.load_module(__LABWARES['flex_magnetic_block']['id'], location= MAGDECK_POSITION)
            # 'magneticModuleV1' is the gen 1 magnetic module, use 'magneticModuleV2' for the gen 2 magentic module
            # if using gen 2 module, need to change settling time! (see comments under Constants)
        # Disengage Magnetic Block using Gripper Logic
            # disengages the magnets when it is turned on
        mag_plate = MAGDECK.load_labware(MIX_PLATE_TYPE)

        # Mix Plate
        flex_mix_plate = protocol.load_labware(MIX_PLATE_TYPE, MIX_PLATE_POSITION)

        # Reagents
        reagent_container = protocol.load_labware(REAGENT_CONTAINER_TYPE, REAGENT_CONTAINER_POSITION)

        # Beads Container
        bead_container = protocol.load_labware(BEAD_CONTAINER_TYPE, BEAD_CONTAINER_POSITION)


        ### Calculating Columns

        # Total number of columns
        col_num = sample_number // 8 + (1 if sample_number % 8 > 0 else 0)

        # Columns containing samples in location 1 (magentic module)
            # generates a list of lists: [[A1, B1, C1...], [A2, B2, C2...]...]
        samples = [col for col in mag_plate.columns()[sample_offset : col_num + sample_offset]]

        # Columns to mix beads and samples in location 4 (mix plate)
        mixing = [col for col in flex_mix_plate.columns()[sample_offset:col_num + sample_offset]]

        # Columns to dispense output in location 1 (magnetic module)
            # purified parts are dispensed 6 rows to the right of their initial location
            # this is why the number of samples cannot exceed 48

        output = [col for col in mag_plate.columns()[6 + sample_offset:col_num + 6 + sample_offset]]

        ### Defining Wells for Reagents, Liquid Waste, and Beads

        liquid_waste = reagent_container.wells(LIQUID_WASTE_WELL)
        ethanol = reagent_container.wells(ethanol_well)
        elution_buffer = reagent_container.wells(elution_buffer_well)
        beads = bead_container[BEADS_WELL]

        ### Define bead and mix volume
        bead_volume = sample_volume * bead_ratio
        if bead_volume / 2 > pipette.max_volume:
            mix_vol = pipette.max_volume
        else:
            mix_vol = bead_volume / 2
        total_vol = bead_volume + sample_volume + DEAD_TOTAL_VOL


        ### Steps

        # Mix beads and parts
        for target in range(int(len(samples))):

            # Define constants for movement speeds
            DEFAULT_SPEED = 400  # Default speed for general operations (mm/s)
            SLOW_SPEED = 50      # Slower speed for precise operations (mm/s)
            pipette.default_speed = DEFAULT_SPEED
            
            # Aspirate beads
            pipette.pick_up_tip()
            pipette.aspirate(bead_volume, beads)
            # Perform slow movements for precise aspirate operations
            pipette.move_to(samples[target][0].top(), speed=SLOW_SPEED)

            #protocol.max_speeds.update(SLOW_HEAD_SPEEDS)

            # Aspirte samples
            pipette.aspirate(sample_volume + DEAD_TOTAL_VOL, samples[target][0])

            # Transfer and mix on flex_mix_plate
            pipette.dispense(total_vol, mixing[target][0])
                # similar to above, added [0] because samples[target] returned a list of every well in column 1 rather than just one well
            pipette.mix(IMMOBILISE_MIX_REPS, mix_vol, mixing[target][0])
                # similar to above, added [0] because samples[target] returned a list of every well in column 1 rather than just one well
            pipette.blow_out()
            
            # Reset the pipette's speed to default
            pipette.default_speed = DEFAULT_SPEED

            # Dispose of tip
            #protocol.max_speeds.update(DEFAULT_HEAD_SPEEDS)
            pipette.drop_tip(trash)

        # Immobilise sample
        protocol.delay(minutes=incubation_time)

        # Transfer beads+samples back to magdeck
        for target in range(int(len(samples))):
            pipette.transfer(total_vol, mixing[target], samples[target], blow_out=True, blowout_location='destination well')
            # added blowout_location=destination well because default location of blowout is waste in API version 2

        # Engagae MagDeck and incubate
        # Engage Magnetic Block using Gripper Logic
        protocol.comment("Engaging the Magnetic Block using the Flex Gripper.")
        move_with_gripper(protocol, mag_plate, MIXING_PLATE_SLOT, MAGNETIC_BLOCK_SLOT)  # Move plate to Magnetic Block
        protocol.delay(minutes=settling_time)  # Wait for beads to settle



        protocol.delay(minutes=settling_time)

        # Remove supernatant from magnetic beads
        for target in samples:
            pipette.transfer(total_vol, target, liquid_waste, blow_out=True)

        # Wash beads twice with 70% ethanol
        air_vol = pipette.max_volume * AIR_VOL_COEFF
        for cycle in range(2):
            for target in samples:
                pipette.transfer(ETHANOL_VOL, ethanol, target, air_gap=air_vol)
            protocol.delay(minutes=WASH_TIME)
            for target in samples:
                pipette.transfer(ETHANOL_VOL + ETHANOL_DEAD_VOL, target, liquid_waste, air_gap=air_vol)

        # Dry at room temperature
        protocol.delay(minutes=drying_time)

        # Disengage Magnetic Block using Gripper Logic
        protocol.comment("Disengaging the Magnetic Block using the Flex Gripper.")
        move_with_gripper(protocol, mag_plate, MAGNETIC_BLOCK_SLOT, MIXING_PLATE_SLOT)  # Move plate back from Magnetic Block




        # Mix beads with elution buffer
        if elution_buffer_volume / 2 > pipette.max_volume:
            mix_vol = pipette.max_volume
        else:
            mix_vol = elution_buffer_volume / 2
        for target in samples:
            pipette.transfer(elution_buffer_volume, elution_buffer, target, mix_after=(ELUTION_MIX_REPS, mix_vol))

        # Incubate at room temperature
        protocol.delay(minutes=elution_time)

        # Engage MagDeck (remains engaged for DNA elution)
        # Engage Magnetic Block using Gripper Logic
        protocol.comment("Engaging the Magnetic Block using the Flex Gripper.")
        move_with_gripper(protocol, mag_plate, MIXING_PLATE_SLOT, MAGNETIC_BLOCK_SLOT)  # Move plate to Magnetic Block
        protocol.delay(minutes=settling_time)  # Wait for beads to settle



        protocol.delay(minutes=ELUTANT_SEP_TIME)

        # Transfer purified parts to a new well
        for target, dest in zip(samples, output):
            pipette.transfer(elution_buffer_volume - ELUTION_DEAD_VOL, target,
                             dest, blow_out=False)

        # Disengage Magnetic Block using Gripper Logic
        protocol.comment("Disengaging the Magnetic Block using the Flex Gripper.")
        move_with_gripper(protocol, mag_plate, MAGNETIC_BLOCK_SLOT, MIXING_PLATE_SLOT)  # Move plate back from Magnetic Block

    magbead(sample_number=sample_number, ethanol_well=ethanol_well)
    # removed elution buffer well='A1', added that to where the function is defined
    
