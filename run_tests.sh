#!/bin/bash
# Activate virtual environment
# Change the path as needed to where your virtual environment is located
source /var/lib/jenkins/envs/venv/bin/activate

# Change directory to where your Django project is
# This should be where your manage.py file is located
cd "/var/lib/jenkins/workspace/Shumin Blog"

# Run Django tests
python manage.py test
