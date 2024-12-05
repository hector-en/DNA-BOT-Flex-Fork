#!/bin/bash

# chmod +x test_ssh_connection.sh
# ./test_ssh_connection.sh <ROBOT_IP>

# Variables
FLEX_IP=$1           # The IP address of the robot, provided as the first argument
SSH_KEY="flex_ssh_key" # Path to your private SSH key file
USER="root"

# Check if IP address is provided
if [ -z "$FLEX_IP" ]; then
  echo "Usage: $0 <FLEX_IP>"
  exit 1
fi

# Check if the SSH private key exists
if [ ! -f "$SSH_KEY" ]; then
  echo "Error: SSH private key file '$SSH_KEY' not found."
  exit 1
fi

# Test SSH connection
echo "Testing SSH connection to $FLEX_IP..."
ssh -i $SSH_KEY $USER@$FLEX_IP "whoami"

if [ $? -eq 0 ]; then
  echo "SSH connection successful to $FLEX_IP."
else
  echo "SSH connection failed."
  exit 1
fi

