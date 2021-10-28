import airsim

# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

# get state: 
# get imu_data
# get barometer_data
# get magnetometer_data
# gps_data

# takeoff
airsim.wait_key('Press any key to takeoff')
print("Taking off...")
client.armDisarm(True)
client.takeoffAsync().join()





# quit
airsim.wait_key('Press any key to reset to original state')
client.reset()
client.armDisarm(False)
client.enableApiControl(False)