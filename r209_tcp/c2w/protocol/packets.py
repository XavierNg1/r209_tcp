# -*- coding: utf-8 -*-

"""
Class used for defining every  generic packets
that we'll use in our system
"""

from twisted.internet.protocol import Protocol
import logging
import struct

class Packet:

    def  __init__(self, seqNumber, typeMsg):
        self.length = 0
        self.seqNumber = seqNumber
        self.typeMsg = typeMsg

    def getType(self):
        return self.typeMsg
    

    def ackMsg(self, seqNumber):
        self.seqNumber = seqNumber
        self.typeMsg = 0
        self.length = 4
        return

    



