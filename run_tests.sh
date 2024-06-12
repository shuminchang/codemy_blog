#!/bin/bash
# Activate virtual environment
source /var/lib/jenkins/envs/venv/bin/activate

# Change directory to where your Django project is
cd "$WORKSPACE"

# Upgrade pip
/var/lib/jenkins/envs/venv/bin/pip install --upgrade pip

# Install dependencies
/var/lib/jenkins/envs/venv/bin/pip install -r requirements.txt

# Start the Django development server in the background
/var/lib/jenkins/envs/venv/bin/python manage.py runserver &

# Store the server's PID to terminate it later
SERVER_PID=$!

# Give the server a few seconds to start up
sleep 5

# Run Django tests using the full path to the Python executable
/var/lib/jenkins/envs/venv/bin/python manage.py test

# Terminate the Django development server
kill $SERVER_PID
