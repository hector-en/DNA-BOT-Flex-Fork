import opentrons.simulate

#protocol_file = open('c:/users/geoff/github/DNA-BOT/dnabot/template_ot2_scripts/simple_protocol_test.py')
protocol_file = open('/Users/zhuohengli/Desktop/DNA-BOT-Flex-Fork/dnabot/MRes2024/1_MRes_clip_Thermocycler_Gen2_APIv2_19.py')
#protocol_file = open('c:/a_n_other_protocol.py')
opentrons.simulate.simulate(protocol_file) 