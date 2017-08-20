from setuptools import setup

setup(name='RobotControl',
      version='0.9.0',
      packages=['robotcontrol'],
      entry_points={
          'console_scripts': [
              'autopump = robotcontrol.__main__:main'
          ]
      },
      )
