from opentrons import protocol_api
import numpy as np
# metadata
metadata = {
    'protocolName': 'DNABOT Step 3: Assembly with thermocycler',
    'description': 'DNABOT Step 3: Assembly with thermocycler',
    'apiLevel': '2.8'
}

# It is possible to run 88 assemblies with this new module. The heat block module is removed. 
# Assembly reactions is set up on thermocycler module.


# test dictionary can be used for simulation 3 or 88 assemblies
#final_assembly_dict={"A1": ['A7', 'B7', 'C7', 'F7'], "B1": ['A7', 'B7', 'D7', 'G7'], "C1": ['A7', 'B7', 'E7', 'H7']}
#tiprack_num=1

#final_assembly_dict={"A1": ["A7", "G7", "H7", "A8", "B8"], "B1": ["A7", "D8", "E8", "F8", "G8"], "C1": ["A7", "D8", "H7", "H8", "B9"], "D1": ["A7", "C9", "E9", "G9", "B8"], "E1": ["A7", "H9", "B10", "E9", "D10"], "F1": ["A7", "C9", "H8", "F10", "D10"], "G1": ["A7", "C9", "H10", "E8", "B9"], "H1": ["A7", "H9", "F8", "H10", "B11"], "A2": ["A7", "G7", "E8", "B10", "G8"], "B2": ["A7", "G7", "D11", "A8", "B9"], "C2": ["A7", "C9", "E9", "G9", "B9"], "D2": ["A7", "G7", "H7", "H8", "B8"], "E2": ["A7", "F11", "H11", "H7", "B12"], "F2": ["A7", "C9", "H8", "H11", "D10"], "G2": ["A7", "G7", "D11", "A8", "B8"], "H2": ["B7", "F11", "B10", "H10", "B11"], "A3": ["B7", "D8", "H7", "H8", "B8"], "B3": ["B7", "C9", "H10", "G9", "B8"], "C3": ["B7", "D12", "H8", "H11", "B11"], "D3": ["B7", "D12", "E9", "E8", "B8"], "E3": ["B7", "D12", "E9", "E8", "B9"], "F3": ["B7", "H9", "B10", "H10", "D10"], "G3": ["B7", "G7", "D11", "H8", "B8"], "H3": ["B7", "D12", "H10", "G9", "B9"], "A4": ["B7", "F11", "F10", "D11", "B12"], "B4": ["B7", "G7", "H7", "A8", "B9"], "C4": ["B7", "G7", "E8", "B10", "B12"], "D4": ["B7", "H9", "H11", "H7", "G8"], "E4": ["B7", "D8", "E8", "F8", "B12"], "F4": ["B7", "D12", "E9", "G9", "B8"], "G4": ["C7", "H9", "B10", "E9", "B11"], "H4": ["C7", "F11", "B10", "H10", "D10"], "A5": ["C7", "H9", "F8", "E9", "B11"], "B5": ["C7", "D12", "H8", "F10", "B11"], "C5": ["C7", "F11", "F8", "H10", "B11"], "D5": ["C7", "F11", "H11", "H7", "G8"], "E5": ["C7", "D8", "D11", "A8", "B9"], "F5": ["C7", "H9", "H11", "H7", "B12"], "G5": ["C7", "C9", "H10", "G9", "B9"], "H5": ["C7", "H9", "F10", "H7", "G8"], "A6": ["C7", "D12", "A8", "H11", "D10"], "B6": ["C7", "C9", "A8", "H11", "B11"], "C6": ["C7", "F11", "H11", "D11", "B12"], "D6": ["C7", "D8", "E8", "B10", "G8"], "E6": ["C7", "C9", "H8", "H11", "B11"], "F6": ["D7", "D8", "G9", "F8", "G8"], "G6": ["D7", "C9", "A8", "F10", "B11"], "H6": ["D7", "F11", "F10", "H7", "B12"], "A7": ["D7", "C9", "A8", "F10", "D10"], "B7": ["D7", "H9", "F8", "E9", "D10"], "C7": ["D7", "G7", "G9", "F8", "B12"], "D7": ["D7", "D12", "A8", "H11", "B11"], "E7": ["D7", "D12", "H10", "G9", "B8"], "F7": ["D7", "H9", "H11", "D11", "B12"], "G7": ["D7", "C9", "H8", "F10", "B11"], "H7": ["D7", "D8", "D11", "H8", "B8"], "A8": ["D7", "C9", "E9", "E8", "B9"], "B8": ["D7", "H9", "F10", "D11", "G8"], "C8": ["D7", "H9", "H11", "D11", "G8"], "D8": ["D7", "D12", "A8", "F10", "D10"], "E8": ["E7", "G7", "G9", "F8", "G8"], "F8": ["E7", "D12", "A8", "F10", "B11"], "G8": ["E7", "H9", "F10", "D11", "B12"], "H8": ["E7", "D8", "E8", "B10", "B12"], "A9": ["E7", "C9", "E9", "E8", "B8"], "B9": ["E7", "F11", "B10", "E9", "D10"], "C9": ["E7", "D12", "H8", "F10", "D10"], "D9": ["E7", "H9", "B10", "H10", "B11"], "E9": ["E7", "D8", "G9", "F8", "B12"], "F9": ["E7", "F11", "B10", "E9", "B11"], "G9": ["E7", "F11", "F8", "E9", "C11"], "H9": ["E7", "G7", "G9", "B10", "B12"], "A10": ["E7", "D8", "G9", "B10", "B12"], "B10": ["E7", "D8", "D11", "A8", "B8"], "C10": ["E7", "F11", "F10", "H7", "G8"], "D10": ["F7", "F11", "F8", "E9", "D10"], "E10": ["F7", "H9", "F10", "H7", "B12"], "F10": ["F7", "D12", "H10", "E8", "B9"], "G10": ["F7", "C9", "H10", "E8", "B8"], "H10": ["F7", "F11", "F8", "H10", "D10"], "A11": ["F7", "D12", "H10", "E8", "B8"], "B11": ["F7", "G7", "H7", "H8", "B9"], "C11": ["F7", "G7", "G9", "B10", "G8"], "D11": ["F7", "D12", "H8", "H11", "D10"], "E11": ["F7", "D9", "A8", "H11", "D10"], "F11": ["F7", "G7", "D11", "H8", "B9"], "G11": ["F7", "F11", "A12", "D11", "G8"], "H11": ["F7", "D8", "D11", "A9", "B9"]}
#tiprack_num=5

# __LABWARES is expected to be redefined by "generate_ot2_script" method
# Test dict
# __LABWARES={"p20_single": {"id": "p20_single_gen2"}, "p300_multi": {"id": "p300_multi_gen2"}, "mag_deck": {"id": "magneticModuleV1"}, "96_tiprack_20ul": {"id": "opentrons_96_tiprack_20ul"}, "96_tiprack_300ul": {"id": "opentrons_96_tiprack_300ul"}, "24_tuberack_1500ul": {"id": "e14151500starlab_24_tuberack_1500ul"}, "96_wellplate_200ul_pcr_step_14": {"id": "4ti0960rig_96_wellplate_200ul"}, "96_wellplate_200ul_pcr_step_23": {"id": "4ti0960rig_96_wellplate_200ul"}, "agar_plate_step_4": {"id": "4ti0960rig_96_wellplate_200ul"}, "12_reservoir_21000ul": {"id": "4ti0131_12_reservoir_21000ul"}, "96_deepwellplate_2ml": {"id": "4ti0136_96_wellplate_2200ul"}}

final_assembly_dict={"A1": ["A7", "B7", "C7", "D7", "E7"], "B1": ["A7", "B7", "C7", "D7", "E7"], "C1": ["A7", "B7", "C7", "F7"], "D1": ["A7", "B7", "C7", "F7"]}
tiprack_num=1
__LABWARES={"p20_single": {"id": "p20_single_gen2"}, "p300_multi": {"id": "p300_multi_gen2"}, "mag_deck": {"id": "magneticModuleV1"}, "96_tiprack_20ul": {"id": "opentrons_96_tiprack_20ul"}, "96_tiprack_300ul": {"id": "opentrons_96_tiprack_300ul"}, "24_tuberack_1500ul": {"id": "e14151500starlab_24_tuberack_1500ul"}, "clip_source_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, "clip_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, "mix_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, "final_assembly_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, "transfo_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, "transfo_plate_wo_thermo": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, "agar_plate": {"id": "nest_96_wellplate_100ul_pcr_full_skirt"}, "12_reservoir_21000ul": {"id": "nest_12_reservoir_15ml"}, "96_deepwellplate_2ml": {"id": "nest_96_wellplate_2ml_deep"}, "12_corning_wellplate": {"id": "corning_12_wellplate_6.9ml_flat"}}


def run(protocol: protocol_api.ProtocolContext):

    def final_assembly(final_assembly_dict, tiprack_num, tiprack_type=__LABWARES['96_tiprack_20ul']['id']):
        
            # Constants, we update all the labware name in version 2
            #Tiprack
            CANDIDATE_TIPRACK_SLOTS = ['2', '3', '5', '6', '9']
            PIPETTE_MOUNT = 'right'
            #Plate of sample after  purification
            MAG_PLATE_TYPE = __LABWARES['clip_plate']['id']
            MAG_PLATE_POSITION = '1'
            #Tuberack
            TUBE_RACK_TYPE = __LABWARES['24_tuberack_1500ul']['id']
            TUBE_RACK_POSITION = '4'
            #Destination plate
            DESTINATION_PLATE_TYPE = __LABWARES['final_assembly_plate']['id']
            TOTAL_VOL = 15
            PART_VOL = 1.5
            MIX_SETTINGS = (1, 3)
            tiprack_num=tiprack_num+1
            # Errors
            sample_number = len(final_assembly_dict.keys())
            if sample_number > 96:
                raise ValueError('Final assembly nummber cannot exceed 96.')

            slots = CANDIDATE_TIPRACK_SLOTS[:tiprack_num]
            tipracks = [protocol.load_labware(tiprack_type, slot) for slot in slots]
            pipette = protocol.load_instrument(__LABWARES['p20_single']['id'], PIPETTE_MOUNT, tip_racks=tipracks)

            # Define Labware and set temperature
            #magbead_plate = protocol.load_labware(MAG_PLATE_TYPE, MAG_PLATE_POSITION)
            #MAGDECK = protocol.load_module(__LABWARES['mag_deck']['id'], location= 'MAGDECK_POSITION')
            #MAGDECK = protocol.load_module(__LABWARES['mag_deck']['id'], MAGDECK_POSITION)
            #Magnetic module shouldn't be needed in assembly step. Purified clips are not on the magnetic module.
            tube_rack = protocol.load_labware(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
            
            
            #Thermocycler Module
            #tc_mod = protocol.load_module('Thermocycler Module')
            tc_mod = protocol.load_module(module_name="thermocyclerModuleV1")
            destination_plate = tc_mod.load_labware(DESTINATION_PLATE_TYPE)
            tc_mod.set_block_temperature(20)


             # Master mix transfers
            final_assembly_lens = []
            for values in final_assembly_dict.values():
                final_assembly_lens.append(len(values))
            unique_assemblies_lens = list(set(final_assembly_lens))
            master_mix_well_letters = ['A', 'B', 'C', 'D']
            
            for x in unique_assemblies_lens:
                master_mix_well = master_mix_well_letters[(x - 1) // 6] + str(x - 1)
                destination_inds = [i for i, lens in enumerate(final_assembly_lens) if lens == x]
                destination_wells = np.array([key for key, value in list(final_assembly_dict.items())])
                destination_wells = list(destination_wells[destination_inds])
                
                pipette.pick_up_tip()
                for destination_well in destination_wells:# make tube_rack_wells and destination_plate.wells in the same type
                    
                    pipette.transfer(TOTAL_VOL - x * PART_VOL, tube_rack.wells(master_mix_well),
                                     destination_plate.wells(destination_well), new_tip='never')#transfer water and buffer in the pipette

            pipette.drop_tip()

            # Part transfers
            for key, values in list(final_assembly_dict.items()):
                for value in values:# magbead_plate.wells and destination_plate.wells in the same type
                    pipette.transfer(PART_VOL, magbead_plate.wells(value),
                                     destination_plate.wells(key), mix_after=MIX_SETTINGS,
                                     new_tip='always')#transfer parts in one tube



            #Thermocycler Module
            tc_mod.close_lid()
            tc_mod.set_lid_temperature(105)
            tc_mod.set_block_temperature(50, hold_time_minutes=45, block_max_volume=15)
            tc_mod.set_block_temperature(4, hold_time_minutes=2, block_max_volume=30)
            # Increase the hold time at 4 C if necessary
            tc_mod.set_lid_temperature(37)
            tc_mod.open_lid()

    final_assembly(final_assembly_dict=final_assembly_dict, tiprack_num=tiprack_num)
