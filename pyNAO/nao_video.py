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
import time
import sys

import numpy as np

import yarp

from pyNAO.BaseModule         import BaseModule, main
from PIL                      import Image

class NaoVideo(BaseModule):
    """ The NaoVideo class provides a yarp module to retrieve the Nao's video stream. """

    
    def configure(self, rf):
        BaseModule.configure(self, rf)

        self.bufImageOut, self.bufArrayOut = self.createImageBuffer(320, 240)
        self.imgOutPort = yarp.Port()
        self.imgOutPort.open('/NaoVideo/img:o')

        self.nao.startVision()
        return True
    

    def runModule(self, rf = None):

        while True:
            # convert the string array
            self.bufArrayOut[:,:] = np.fromstring(self.nao.getImage()[6], dtype=np.uint8).reshape(240,320,3)
          
            # Send the result to the output port
            self.imgOutPort.write(self.bufImageOut)


    def interruptModule(self):
        self.imgOutPort.interrupt()
        return BaseModule.interruptModule(self)


    def close(self):
        self.nao.stopVision()
        self.imgOutPort.close()
        return BaseModule.close(self)

    
    @staticmethod    
    def createImageBuffer(width = 320, height = 240, channels = 3):
        """ This method creates image buffers with the specified \a width, \a height and number of 
            color channels \a channels.
            
        @param width    - integer specifying the width of the image   (default: 320)
        @param height   - integer specifying the height of the image  (default: 240)
        @param channels - integer specifying number of color channels (default: 3)
        @return image, buffer array
        """
    
        if channels == 1:
            buf_image = yarp.ImageFloat()
            buf_image.resize(width, height)
            
            buf_array = np.zeros((height, width), dtype = np.float32)
            
        else:
            buf_image = yarp.ImageRgb()
            buf_image.resize(width, height)
            
            buf_array = np.zeros((height, width, channels), dtype = np.uint8)
    
        buf_image.setExternal( buf_array, 
                               buf_array.shape[1], 
                               buf_array.shape[0] )
    
        return buf_image, buf_array


if __name__ == '__main__':
    try:
        main(NaoVideo)
    except Exception as e:
        print e