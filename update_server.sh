#!/bin/bash

# Stop the backend server
tmux send-keys -t oculus-back C-c

# Pull changes from the Git repository
cd /root/log_new/logs
git pull

# Attach to the tmux session and start uvicorn
tmux attach-session -t oculus-back -d
tmux send-keys -t oculus-back "uvicorn main:app --host 192.168.30.24 --port 5220" C-m