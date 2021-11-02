import airsim

# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

# takeoff
def takeoff(client):
    airsim.wait_key('Press any key to takeoff')
    print("Taking off...")
    client.armDisarm(True)
    client.takeoffAsync().join()

# quit
def quit(client):
    airsim.wait_key('Press any key to reset to original state')
    client.reset()
    client.armDisarm(False)
    client.enableApiControl(False)

takeoff(client)


quit(client)