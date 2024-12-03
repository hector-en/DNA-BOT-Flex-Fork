#!/bin/bash

# Base project directory
PROJECT_DIR="project-basic-on-flex"

# Create the project directory structure
mkdir -p $PROJECT_DIR/mode_configs
mkdir -p $PROJECT_DIR/reactions

# Create empty files
touch $PROJECT_DIR/protocol_mode.py
touch $PROJECT_DIR/global_config.yaml

# Create empty mode configuration files
touch $PROJECT_DIR/mode_configs/clip.yaml
touch $PROJECT_DIR/mode_configs/purification.yaml
touch $PROJECT_DIR/mode_configs/transformation.yaml
touch $PROJECT_DIR/mode_configs/pcr.yaml

# Create the reactions package structure
touch $PROJECT_DIR/reactions/__init__.py
touch $PROJECT_DIR/reactions/base.py
touch $PROJECT_DIR/reactions/clip.py
touch $PROJECT_DIR/reactions/purification.py
touch $PROJECT_DIR/reactions/transformation.py
touch $PROJECT_DIR/reactions/pcr.py

echo "Project structure created successfully!"

