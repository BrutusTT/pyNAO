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
import time
import yarp
from pyNAO.nao import Nao

EMSG_YARP_NOT_FOUND  = "Could not connect to the yarp server. Try running 'yarp detect'."
EMSG_ROBOT_NOT_FOUND = 'Could not connect to the robot at %s:%s'


class BaseModule(yarp.RFModule):
    """ The BaseModule class provides a base class for developing modules for the Nao robot.
    """

    # Default IP Address and Port for the JD Humanoid Robot.
    TCP_IP      = '127.0.0.1'
    TCP_PORT    = 9559


    def __init__(self, ip, port, prefix):
        yarp.RFModule.__init__(self)
        self.ip     = ip
        self.port   = int(port)
        self.prefix = prefix


    def configure(self, rf):

        name = self.__class__.__name__ 
        if self.prefix:
            name = self.prefix + '/' + name

        self.setName(name)

        try:
            self.nao = Nao(self.ip, self.port)
        except:
            raise RuntimeError(EMSG_ROBOT_NOT_FOUND % (self.ip, self.port))

        # RPC Port
        self.rpc_port = yarp.RpcServer()

        # name settings
        port_name = '/%s/%s' % (name, 'rpc')

        if not self.rpc_port.open(port_name):
            raise RuntimeError, EMSG_YARP_NOT_FOUND

        self.attach_rpc_server(self.rpc_port)

        return True


    def interruptModule(self):
        self.rpc_port.interrupt()
        return True


    def close(self):
        self.rpc_port.close()
        return True


    def getPeriod(self):
        return 0.1


    def updateModule(self):
        # XXX: I do not know why we need that, but if method is empty the module gets stuck
        time.sleep(0.000001)
        return True


####################################################################################################
#
# Default methods for running the modules standalone 
#
####################################################################################################
def createArgParser():
    """ This method creates a base argument parser. 
    
    @return Argument Parser object
    """
    parser = argparse.ArgumentParser(description='Create a NaoModule to control the Nao robot.')
    parser.add_argument( '-i', '--ip', 
                         dest       = 'ip', 
                         default    = str(BaseModule.TCP_IP),
                         help       = 'IP address for the Nao robot.')
    parser.add_argument( '-p', '--port', 
                         dest       = 'port', 
                         default    = str(BaseModule.TCP_PORT),
                         help       = 'Port for the Nao robot')
    parser.add_argument( '-n', '--name', 
                         dest       = 'name', 
                         default    = '',
                         help       = 'Name prefix for Yarp port names')

    return parser.parse_args()


def main(module_cls):
    """ This is a main method to run a module from command line. 

    @param module_cls - an BaseModule based class that can be started as a standalone module.
    """
    args = createArgParser()

    yarp.Network.init()

    resource_finder = yarp.ResourceFinder()
    resource_finder.setVerbose(True)

    # resource_finder.configure(argc,argv);

    module = module_cls(args.ip, args.port, args.name)
    module.configure(resource_finder)
    module.runModule(resource_finder)

    yarp.Network.fini()
