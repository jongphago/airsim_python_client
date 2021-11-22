import setup_path
import airsim

import sys
import os
import time

import math
import pprint

print("""This script is designed to flyon the streets of the Neighborhood environment
and assumes the unreal position of the drone is [160, -1500, 120].""")

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

print("arming the drone...")
client.armDisarm(True)

state = client.getMultirotorState()
if state.landed_state == airsim.LandedState.Landed:
    print("taking off...")
    client.takeoffAsync().join()
else:
    client.hoverAsync().join()

time.sleep(1)

state = client.getMultirotorState()
if state.landed_state == airsim.LandedState.Landed:
    print("take off failed...")
    sys.exit(1)

# AirSim uses NED coordinates so negative axis is up.
# z of -5 is 5 meters above the original launch point.
z = -60 # AiHub -40
print("make sure we are hovering at {} meters...".format(-z))
client.moveToZAsync(z, 1).join()

# set segmentation object ID
#  client.simSetSegmentationObjectID("[\w]*", 0, True)
# client.simSetSegmentationObjectID("car[\w]*", 255, True)

# Change camera pitch
# see https://github.com/microsoft/AirSim/blob/master/PythonClient/computer_vision/cv_mode.py
degree = -45
# airsim.wait_key(f'Press any key to set camera-0 gimbal to {degree}-degree pitch')
camera_pose = airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(math.radians(degree), 0, 0)) #radians
client.simSetCameraPose("0", camera_pose)

# Change SUN position
# see https://microsoft.github.io/AirSim/apis/#time-of-day-api
is_enabled = True
client.simSetTimeOfDay(is_enabled, 
                       celestial_clock_speed = 600, 
                       update_interval_secs = 1)

# Image directory
tmp_dir = "C:/Users/jonghyun/Documents/AirSim/Dataset"
print ("Saving images to %s" % tmp_dir)
try:
    pass
    # os.makedirs(tmp_dir)
except OSError:
    if not os.path.isdir(tmp_dir):
        raise

# see https://github.com/Microsoft/AirSim/wiki/moveOnPath-demo
# this method is async and we are not waiting for the result since we are passing timeout_sec=0.
print("flying on path...")
velocity = 12 # 12, AiHub 7.7
for n in range(2):
    result = client.moveOnPathAsync([airsim.Vector3r(125,0,z),
                                    airsim.Vector3r(125,-80,z), # 125, -130, z
                                    airsim.Vector3r(-20,-80,z),
                                    airsim.Vector3r(-20,0,z)],
                            velocity,
                            120,
                            airsim.DrivetrainType.ForwardOnly, 
                            airsim.YawMode(False,0), 20, 1)#.join()

    # take screenshot
    # airsim.wait_key('Press any key to get images')
    for x in range(35): # do few times
        responses = client.simGetImages([
            airsim.ImageRequest("0", airsim.ImageType.Scene),
            airsim.ImageRequest("0", airsim.ImageType.Segmentation)
        ])

        for i, response in enumerate(responses):
            filename = os.path.join(tmp_dir, str(x) + "_" + str(n) + "_" + str(i))
            print("Type %d, size %d, pos %s" % (response.image_type, len(response.image_data_uint8), pprint.pformat(response.camera_position)))
            airsim.write_file(os.path.normpath(filename + '.png'), response.image_data_uint8)

        time.sleep(1)

    # drone will over-shoot so we bring it back to the start point before landing.
    print("moving...")
    client.moveToPositionAsync(0,0,z,1).join()

print("landing...")
client.landAsync().join()
print("disarming...")
client.armDisarm(False)
client.enableApiControl(False)
print("done.")
