# DNABOT-FLEX

A fork of the original DNA-BOT project, updated for compatibility with the Opentrons Flex platform. The focus of this branch is to ensure that DNA assembly workflows and automation scripts originally developed for the OT2 are fully functional on Flex, with enhanced features and compatibility.

---

## Project Description

DNABOT-FLEX updates and adapts the original DNA-BOT workflows to utilize the enhanced capabilities of the Opentrons Flex platform. Key objectives include:
- Ensuring compatibility with Flex-specific labware and hardware configurations.
- Utilizing advanced features of the Flex platform, such as liquid level detection and expanded deck positioning.
- Maintaining backward compatibility with OT2 workflows.

This branch aims to bridge gaps in compatibility and unlock Flex-specific functionality while refining script modularity and efficiency.

---

## Task Definition

**Primary Goals**:
1. Update the DNA-BOT workflows and scripts to work seamlessly on the Opentrons Flex platform.
2. Focus on achieving compatibility in the following key steps:
   - **Thermocycler Clip Reactions**
   - **Purification Workflows**
   - **Assembly Processes**

**Key Issues Identified**:
1. **Labware Compatibility**:
   - Some Flex-specific labware definitions are missing or incompatible.
   - Deepwell plate definitions require validation (e.g., Nunk Deepwell plates).
   - Flex uses different deck positioning (A1, B1) than OT2 (1–12).

2. **Liquid Handling and Mixing**:
   - Scripts must support liquid level detection for precision pipetting.
   - Mixing algorithms need optimization to avoid redundant actions and ensure proper resuspension of DNA solutions.

3. **Simulation and Testing**:
   - Scripts must run in simulation mode to validate Flex compatibility before testing on hardware.
   - Debug issues related to labware loading, volumes, and positioning.

---

## Getting Started

Follow these instructions to set up your environment and begin simulation/testing.

### Prerequisites

Ensure you have the following installed:
1. [Python 3.7+](https://www.python.org/)
2. [Conda](https://docs.conda.io/)
3. [Opentrons API v2](https://docs.opentrons.com/)
4. [GitHub Desktop](https://desktop.github.com/) (optional but recommended)

---

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/DNA-BOT-Flex-Fork.git
   cd DNA-BOT-Flex-Fork
   ```

2. **Set Up a Conda Environment**:
   ```bash
   conda create --name dnabot-flex python=3.7
   conda activate dnabot-flex
   pip install -r requirements.txt
   ```

---

### Simulating Scripts

1. **Activate the Environment**:
   ```bash
   conda activate dnabot-flex
   ```

2. **Run a Script in Simulation Mode**:
   Use one of the provided scripts in the `MRes2024` folder (e.g., `clip.py`).
   ```bash
   python -m opentrons.simulate scripts/clip.py
   ```

3. **Validate Output**:
   Check for errors related to labware, commands, or volumes. Resolve issues as needed.

---

## Key Steps for Compatibility

### Step 1: Labware Compatibility
- Update labware definitions to Flex-supported formats (e.g., `4ti0960rig_96_wellplate_200ul`).
- Use generic labware for simulations and switch to specific labware definitions for live testing.

### Step 2: Liquid Handling
- Implement liquid level detection to enhance pipetting precision.
- Test minimum liquid detection thresholds (10 µL, 20 µL) using simulated and live workflows.

### Step 3: Mixing Optimization
- Refactor `.mix()` commands to minimize redundant mixing.
- Validate DNA resuspension using visual markers (e.g., bromophenol blue).

### Step 4: Flex Testing
- Run scripts on Flex hardware, starting with the updated `MRes2024` scripts:
  - Script 1: Clip
  - Script 2: Purification
  - Script 3: Assembly
  - Script 4: Transformation
- Debug real-world issues such as deck positioning and tip alignment.

---

## Contributors

### Current Team:
- **Hector Edu Nseng** - Lead Developer
- **Anthony Sowerbutts** - Developer
- **Wenhan Hu** - Developer
- **Zhouheng Li** - Developer

### Original Authors:
- Geoff Baldwin ([geoffbaldwin](https://github.com/geoffbaldwin))
- Thomas Duigou ([tduigou](https://github.com/tduigou))

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Marko Storch for guidance on Opentrons workflows.
- Original DNA-BOT contributors for their foundational work.
