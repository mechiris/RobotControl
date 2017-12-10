# RobotControl
This is a codebase that provides menu driven control of a 6axis servo driven robotic arm.  It allows for basic manipulation of manually entered positions, go to teachpoint functionality, and the ability to loop the arm in a sequence of teachpoints. 

The arm is driven using a raspberry pi, affixed w/ the adafruit PWM/Servo shield, a Rot2U robotic arm using MG996R servos.  With that said, it should work for any PWM addressable setup.  Full build details are available here:

# Install instructions
On the raspberry pi:

.. code:: bash
    git clone https://github.com/mechiris/RobotControl.git
    sudo apt-get install python-pandas #faster than compiling from scratch
    cd RobotControl
    pip install -r requirements.txt
    python setup.py develop

# Usage

## Run
To run the program, enter the following shell command:
`robotcontrol`
This will pull up a menu with prompts on setting servos directly, going to predefined teachpoints, or sequences that can be setup and saved in csv files.  All menu commanders are text entry followed by return. 

## Menu overview
### 3. Go To Servo Position
Typical usage would be to use the menu option set individual servos until you get the robot to a position of interest.  Enter the servo number, followed by the position of interest.  You can also nudge using the up and down keys. Once the robot is positioned, you can go to the main menu and list out the servo positions. From there you can create a teachpoint. 

### 2. Go To TeachPoint
You can create a teachpoint by editting /robotcontrol/Teachpoints.csv.  This file is structured with the following columns:
* Position,delay,s0,s1,s2,s3,s4,s5
  * Position: the human readable name of the teachpoint, referenced from the menu 
  * delay is how long it takes to move (the class uses some basic smoothing so it doesn't jerk the robot right into position)
  *  s0:s5 are the servo positions.  

Once you save the teachpoint in Teachpoints.csv, you can restart your robotcontrol program it and should be available from the menu. 

Select 2. Go To TeachPoint, and l will list the available teachpoints.  You can then type in the name, and hit enter.  The robot will move to the teachpoint of interest. 

### 1. Run Sequence
Once you have teachpoints created, you can create sequences of these teachpoints. A sequence includes one or more teachpoints in a list, which can be either run once or run continuously.

The robotcontrol/Sequences.csv file has the following structure:
* sequence;teachpoints;delays;loop 
  * Sequence: The name of the sequence, referenced from the menu
  * teachpoints: a comma seperated list of teachpoints to be run
  * delays: a comma seperated list of delays associated with each teachpoint.  Should be the same length as teachpoints.
  * loop: True if you want the sequence to repeat until user interaction.

The columns use a semicolon delimiter, as some of the contents of the cells can have multiple values seperated by a comma. 
Once you save your robotocontrol/Sequences.csv, you can restart the robotcontrol program and reference from the menu:
Select 1. Run Sequence, and l will list the available sequences.  Type in the sequence name of interest.  If the sequence has loop=True, it will run until you hit return again. 





