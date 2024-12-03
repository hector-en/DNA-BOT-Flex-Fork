# Protocol Transformation Between OT-2 and Flex

## Objectives

1. **Protocol Translation**: Convert OT-2 protocols to Flex-compatible versions and vice versa.
2. **Dynamic Adaptation**: Dynamically update labware, pipettes, trash setup, and metadata using mappings in `generic_map.yaml`.
3. **Error Resolution**: Eliminate undefined variables, mismatched labware, and inconsistencies in pipette operations.
4. **Simulation Validation**: Ensure all transformed scripts run without errors using `opentrons.simulate`.

## Key Updates

- Added a transformation script `transform.py` to automate protocol conversions.
- Updated `generic_map.yaml` to include:
  - Comprehensive labware and pipette mappings.
  - Dynamic trash configuration with platform-specific slot definitions.
  - Metadata and variable mappings.
- Fixed runtime errors, such as undefined `trash` and incorrect `drop_tip` locations.
- Enabled verification using `python -m opentrons.simulate <script.py>`.
---
## Usage

### Transform a Protocol
Run the following command:
```bash
python transform.py <input_script.py> <output_script.py> <direction>
```
### Simulate the Transformed Script
Validate the script for errors using the following command:

```bash
python -m opentrons.simulate flex_protocol.py
```
### Measurable Progress
#### Current Completion
 - OT-2 to Flex Translation: 100% complete.
 - Flex to OT-2 Translation: 100% complete.
 - Simulation Validation: Fully implemented and verified.
 - Dynamic Mapping with YAML: Completed.

#### Remaining Tasks
 - Integration with DNABOT Workflows: T+1 day.
 - Physical Testing on OT-2 and Flex: T+2 days.
 - Documentation and Experimental Showcasing: T+3 days.
   - Pipetting: Higher precision and extended volume range for multi-channel pipettes.
   - Enhanced Modularity: Advanced modules like the Flex heater-shaker for complex reactions. 
   - Custom Labware Compatibility: Expanded options for non-standard labware integration.
   

#### Estimated Completion Timeline
All tasks are expected to be completed within 3 working days.

### Next Steps:
1. Physical testing of Flex scripts for mix and transfer accuracy using visible and fluorescent dyes.
2. Coordination with DNABOT users (Liam Hallett, Anthony Barlow) for feedback and iterative improvements.
3. Documentation of processes for end-users.

