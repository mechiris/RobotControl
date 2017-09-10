# RobotControl
Robot control for a 6axis Rot2U

# Install instructions
pip install -r requirements.txt
python setup.py develop

# Usage
Run robotcontrol from the command line.  It has guided prompts on setting servos directly, or going to predefined teachpoints in the included excel files

# Testing data post functionality
To test data posting functionality in the absence of a robot, use the provided test harness:
python dataposter_testharness.py

It will log data to /opt/sightmachine/data by default.
