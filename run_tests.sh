#!/bin/bash
# Activate virtual environment
source /var/lib/jenkins/envs/venv/bin/activate

# Change directory to where your Django project is
cd "$WORKSPACE"

# Upgrade pip
/var/lib/jenkins/envs/venv/bin/pip install --upgrade pip

# Install dependencies
/var/lib/jenkins/envs/venv/bin/pip install -r requirements.txt

# Start the Django development server in the background on a specific port
/var/lib/jenkins/envs/venv/bin/python manage.py runserver 8001 > server_log.txt 2>&1 &

# Store the server's PID to terminate it later
SERVER_PID=$!

# Give the server a few seconds to start up
sleep 10

# Check if the server started correctly
if ! ps -p $SERVER_PID > /dev/null; then
    echo "Django server failed to start. Check server_log.txt for details."
    cat server_log.txt
    exit 1
fi

# Run Django tests using the full path to the Python executable
/var/lib/jenkins/envs/venv/bin/python manage.py test

# Terminate the Django development server
kill $SERVER_PID
