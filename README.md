# RobotControl
This is a codebase that provides menu driven control of a 6axis servo driven robotic arm.  It allows for basic manipulation of manually entered positions, go to teachpoint functionality, and the ability to loop the arm in a sequence of teachpoints. 

The arm is driven using a raspberry pi, affixed w/ the adafruit PWM/Servo shield, a Rot2U robotic arm using MG996R servos.  With that said, it should work for any PWM addressable setup.  Full build details are available here:

# Install instructions
On the raspberry pi:

sudo apt-get install python-pandas #faster that compiling 

pip install -r requirements.txt

python setup.py develop

# Usage
Run 'robotcontrol' from the command line.  It has guided prompts on setting servos directly, or going to predefined teachpoints or sequences in the included excel files
