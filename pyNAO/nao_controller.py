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
from pyNAO.BaseModule   import BaseModule, main


class NaoController(BaseModule):
    """ The NaoController class provides a yarp module to control the Nao robot.
    """

    def respond(self, command, reply):
        """ This is the respond hook method which gets called upon receiving a bottle via RPC port.

        @param command - input bottle
        @param reply - output bottle
        @return boolean
        """
        reply = 'nack'

        try:
            if command.get(0).toString() == 'point':
    
                arm   = command.get(1).toString()
    
                if arm not in ['left', 'right']:
                    reply += ' message format for point: point <"left"|"right"> x y z'
    
                else:
                    xyz   = [ command.get(2).asDouble(), 
                              command.get(3).asDouble(),
                              command.get(4).asDouble() ] 
                    self.nao.point('LArm' if arm == 'left' else 'RArm', xyz)
                    reply = 'ack'
    
            elif command.get(0).toString() == 'look':
                    xyz = [ command.get(1).asDouble(), 
                            command.get(2).asDouble(),
                            command.get(3).asDouble(),
                            ] 
                    
                    self.nao.look(xyz)
                    reply = 'ack'
        except Exception as e:
            print e


        # reply with success
#        reply.addString('ack')
        return True


if __name__ == '__main__':
    main(NaoController)
