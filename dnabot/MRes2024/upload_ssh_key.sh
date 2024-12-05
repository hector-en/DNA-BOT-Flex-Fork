#!/bin/bash
# chmod +x upload_ssh_key.sh
# ./upload_ssh_key.sh <ROBOT_IP>
 
# Variables
FLEX_IP=$1           # The IP address of the robot, provided as the first argument
SSH_KEY="flex_ssh_key.pub" # Path to your public SSH key file
PORT="31950"

# Check if IP address is provided
if [ -z "$FLEX_IP" ]; then
  echo "Usage: $0 <FLEX_IP>"
  exit 1
fi

# Check if the SSH key exists
if [ ! -f "$SSH_KEY" ]; then
  echo "Error: SSH public key file '$SSH_KEY' not found."
  exit 1
fi

# Upload the SSH key
echo "Uploading SSH key to $FLEX_IP..."
curl -H 'Content-Type: application/json' \
     -d "{\"key\":\"$(cat $SSH_KEY)\"}" \
     http://$FLEX_IP:$PORT/server/ssh_keys

if [ $? -eq 0 ]; then
  echo "SSH key uploaded successfully to $FLEX_IP."
else
  echo "Failed to upload SSH key."
  exit 1
fi

