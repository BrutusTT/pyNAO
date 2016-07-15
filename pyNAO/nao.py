####################################################################################################
#    Copyright (C) 2016 by Ingo Keller                                                             #
#    <brutusthetschiepel@gmail.com>                                                                #
#                                                                                                  #
#    This file is part of pyNao (Python/Yarp Tools for the NAO robot).                             #
#                                                                                                  #
#    pyNao is free software: you can redistribute it and/or modify it under the terms of the       #
#    GNU Affero General Public License as published by the Free Software Foundation, either        #
#    version 3 of the License, or (at your option) any later version.                              #
#                                                                                                  #
#    pyNao is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;            #
#    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.     #
#    See the GNU Affero General Public License for more details.                                   #
#                                                                                                  #
#    You should have received a copy of the GNU Affero General Public License                      #
#    along with pyNao.  If not, see <http://www.gnu.org/licenses/>.                                #
####################################################################################################
import argparse
import math
import time
import sys

import motion
import vision_definitions
from naoqi import ALProxy


import numpy as np

def magn(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)


class Nao(object):

    LArm   = 'LArm'
    RArm   = 'RArm'

    
    OFFSET = { 'HEAD':       np.array([0.0,  0.0,  0.126]),
               'LShoulder':  np.array([0.0,  0.09, 0.106]),
               'RShoulder':  np.array([0.0, -0.09, 0.106]) }
    
    INIT = { 'LArm': [0.16036176681518555, 0.11096803843975067, -0.025403691455721855, -1.1722420454025269, 0.3230745792388916, -0.07219459861516953],
             'RArm': [0.119, -0.133, -0.044,  1.217, 0.415, -0.013] }

    
    ArmLength              = 0.22                   # in meters, rounded down
    Frame                  = motion.FRAME_TORSO
    AxisMask               = 7                      # just control position
    UseSensorValues        = False

    
    def __init__(self, ip, port):
        self._ip            = ip
        self._port          = port
        self._proxy_motion  = None
        self._proxy_posture = None
        self._proxy_cam     = None
        self._stiffness     = 0.0
        self._videoClient   = None

        self.initialize()
        

    def initialize(self):
        self.stiffness = 0.6
        self.postureProxy.goToPosture("StandInit", 0.2) 

    
    @property
    def motionProxy(self):
        if self._proxy_motion is None:
            # Set motionProxy
            try:
                self._proxy_motion = ALProxy("ALMotion", self._ip, self._port)
            except Exception as e:
                print "Could not create proxy to ALMotion"
                print "Error was: ", e
                sys.exit()
        return self._proxy_motion


    @property
    def postureProxy(self):
        if self._proxy_posture is None:
            # Set postureProxy
            try:
                self._proxy_posture = ALProxy("ALRobotPosture", self._ip, self._port)
            except Exception, e:
                print "Could not create proxy to ALRobotPosture"
                print "Error was: ", e
                sys.exit()
        return self._proxy_posture


    @property
    def camProxy(self):
        if self._proxy_cam is None:
            # Set camProxy
            try:
                self._proxy_cam = ALProxy("ALVideoDevice", self._ip, self._port)
            except Exception as e:
                print "Could not create proxy to ALVideoDevice"
                print "Error was: ", e
                sys.exit()
        return self._proxy_cam


    @property
    def stiffness(self):
        return self._stiffness
    

    @stiffness.setter
    def stiffness(self, value):

        # We use the "Body" name to signify the collection of all joints
        self._stiffness = min( max(value, 0.0), 1.0 )
        self.motionProxy.stiffnessInterpolation("Body", self._stiffness, 1.0)


    def moveHead(self, pitch, yaw, sleepTime):
        self.motionProxy.setAngles(["HeadPitch", "HeadYaw"], [pitch, yaw], 0.1)
        time.sleep(sleepTime)


    def moveArm(self, arm, target, sleepTime):
        assert arm in [Nao.LArm, Nao.RArm], "Error: arm needs to be 'LArm' or 'RArm'"

        self.motionProxy.setPosition(arm, Nao.Frame, target, 0.9, Nao.AxisMask)
        time.sleep(sleepTime)

    
    def look(self, vector):
        pitch, yaw      = self.getPitchAndYaw(vector)
        sleepTime       = 2                     # seconds
        self.moveHead(pitch, yaw, sleepTime)    # Move head to look
        self.moveHead(0,     0,   sleepTime)    # Move head back


    def point(self, arm, vector):
        assert arm in [Nao.LArm, Nao.RArm], "Error: arm needs to be 'LArm' or 'RArm'"

        target = self.getTarget(vector, Nao.OFFSET[arm[0] + 'Shoulder'])
        self.moveArm(arm, target,        .1)   # Move arm to point
        self.openHand(arm)
        self.postureProxy.goToPosture("StandInit", 0.2) 



    def getTarget(self, vector, shoulderOffset):

        # vector from shoulder to object
        shoulderObjectVector = vector - shoulderOffset

        # scale vector by arm length
        shoulderObjectVectorMagn = magn(shoulderObjectVector)
        ratio                    = Nao.ArmLength / shoulderObjectVectorMagn
        target                   = [x * ratio for x in shoulderObjectVector]

        # return scaled vector in torso coordinate frame
        return list( np.append(target + shoulderOffset, [0.0, 0.0, 0.0]) )


    def getPitchAndYaw(self, vector):

        # Get unit vector from head to object
        headObjectVector     = vector - Nao.OFFSET['HEAD']
        headObjectUnitVector = [x / magn(headObjectVector) for x in headObjectVector]

        # Compute pitch and yaw of unit vector
        pitch   = -math.asin(headObjectUnitVector[2])
        yaw     = math.acos(headObjectUnitVector[0])
        if headObjectUnitVector[1] < 0:
            yaw *= -1
        return pitch, yaw


    def openHand(self, arm):
        self.motionProxy.openHand(arm[0] + 'Hand')

    
    def closeHand(self, arm):
        self.motionProxy.closeHand(arm[0] + 'Hand')


    def getPosition(self, joint):
        return self.motionProxy.getPosition(joint, Nao.Frame, True)


    def startVision(self):
        self.camProxy.setActiveCamera(1)
        self._videoClient = self.camProxy.subscribe( '_client3', 
                                                     vision_definitions.kQVGA,
                                                     vision_definitions.kRGBColorSpace,
                                                     30 )

    def stopVision(self):
        if self._videoClient:
            self.camProxy.unsubscribe(self._videoClient)


    def getImage(self):
        return self.camProxy.getImageRemote(self._videoClient)


    def __del__(self):
        self.stopVision()


####################################################################################################
#
# Default methods for running the modules standalone 
#
####################################################################################################
def createArgParser():
    """ This method creates a base argument parser. 
    
    @return Argument Parser object
    """
    parser = argparse.ArgumentParser(description='Create a module to control the robot.')
    parser.add_argument( '-i', '--ip', 
                         dest       = 'ip', 
                         default    = '10.0.0.17',
                         help       = 'IP address for the robot.')
    parser.add_argument( '-p', '--port', 
                         dest       = 'port', 
                         default    = 9559,
                         type       = type(0),
                         help       = 'Port for the robot')

    return parser.parse_args()


if __name__ == "__main__":
    args = createArgParser()
    nao  = Nao(args.ip, args.port) 
