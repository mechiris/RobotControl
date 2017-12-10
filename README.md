# RobotControl
This is a codebase that provides menu driven control of a 6axis servo driven robotic arm.  It allows for basic manipulation of manually entered positions, go to teachpoint functionality, and the ability to loop the arm in a sequence of teachpoints. 

The arm is driven using a raspberry pi, affixed w/ the adafruit PWM/Servo shield, a Rot2U robotic arm using MG996R servos.  With that said, it should work for any PWM addressable setup.  Full build details are available here:

# Install instructions
On the raspberry pi:

`sudo apt-get install python-pandas #faster that compiling` 

`pip install -r requirements.txt`

`python setup.py develop`

# Usage

## Run
To run the program, enter the following shell command:
`robotcontrol`

It has guided prompts on setting servos directly, or going to predefined teachpoints or sequences in the included excel files. 

Typical usage would be to use the menu option set individual servos until you get the robot to a position of interest.  Once the robot is positioned, you can go to the main menu and list out the servo positions.  From there you can create a teachpoint by editting /robotcontrol/Teachpoints.csv.  This file is structured with the following columns:
Position,delay,s0,s1,s2,s3,s4,s5

Position is the human readable name of the teachpoint, as it will be referenced from the menu selector, delay is how long it takes to move (the class uses some basic smoothing so it doesn't jerk the robot right into position), and s0:s5 are the servo positions.  Once you save the teachpoint in Teachpoints.csv, you can restart your robotcontrol program it and should be available from the menu. 


