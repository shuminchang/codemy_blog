#!/bin/bash
# Activate virtual environment
source /var/lib/jenkins/envs/venv/bin/activate

# Change directory to where your Django project is
cd "/var/lib/jenkins/workspace/Shumin Blog"

# Run Django tests using the full path to the Python executable
/var/lib/jenkins/envs/venv/bin/python manage.py test
