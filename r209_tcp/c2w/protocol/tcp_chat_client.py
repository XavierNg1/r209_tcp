# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
import logging
import c2w.protocol.util as util
import logging
import struct
from twisted.internet import reactor
import time
from c2w.main.constants import ROOM_IDS

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_client_protocol')


class c2wTcpChatClientProtocol(Protocol):

    def __init__(self, clientProxy, serverAddress, serverPort):
        """
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param serverPort: The port number used by the c2w server,
            given by the user.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: serverAddress

            The IP address of the c2w server.

        .. attribute:: serverPort

            The port number used by the c2w server.

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        #: The IP address of the c2w server.
        self.serverAddress = serverAddress
        #: The port number used by the c2w server.
        self.serverPort = serverPort
        #: The clientProxy, which the protocol must use
        #: to interact with the Graphical User Interface.
        #Pour verifier la longueur du message
        self.recu = b''
        self.clientProxy = clientProxy
        self.num_sequence=0
        self.users=[]
        self.numDeconection=0
        self.numJoinRoom=0
        self.listUser=[]
        self.movies=[]
        self.filattente=[]
        self.username=''
        self.recuList=[]

    
    def traitementAck(self,numSeq):
            
        for p in self.filattente:
                if (p[0]==numSeq):
                    p[2]=1                   
                    self.num_sequence+=1
                    print(self.num_sequence)
                    print('ack envoye par le serveur')
                    #self.filattente.remove(p)
                            
    
    def sendAndWait(self,host_port):
        for p in self.filattente:
                if (p[4]==host_port):  
                    if (p[1] <= 7): # 7 correspond au nombre maximum de fois qu'on doit ramener un paquet
                        if (p[2] == 0):
                            self.transport.write(p[3])
                            p[1]+=1
                            print('nombre de message envoye:'+str(p[1]))
                            reactor.callLater(1,self.sendAndWait,host_port)#ou sont les parametre 
                        elif(p[2] == 1):
                            print('Le paquet a ete aquitte')  
                            self.filattente.remove(p)                           
                            
                    else:
                        print('Le paquet envoye est perdu')
                        self.filattente.remove(p)
                        

    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The client proxy calls this function when the user clicks on
        the login button.
        """
        self.username=userName
        buf=util.format_login(userName)
        self.transport.write(buf)
        self.filattente.append([self.num_sequence,1,0,buf,(self.serverAddress, self.serverPort)])         
        reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort)) 
       

        moduleLogger.debug('loginRequest called with username=%s', userName)
    


    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string

        Called by the client proxy when the user has decided to send
        a chat message

        .. note::
           This is the only function handling chat messages, irrespective
           of the room where the user is.  Therefore it is up to the
           c2wChatClientProctocol or to the server to make sure that this
           message is handled properly, i.e., it is shown only by the
           client(s) who are in the same room.
        """
        buf=util.format_chat(self.num_sequence,9,self.username,message)
        self.transport.write(buf)
        self.filattente.append([self.num_sequence,1,0,buf,(self.serverAddress, self.serverPort)])      
        #reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort))
        reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort)) 
           

        pass

    def sendJoinRoomRequestOIE(self, roomName):
        """
        :param roomName: The room name (or movie title.)

        Called by the client proxy  when the user
        has clicked on the watch button or the leave button,
        indicating that she/he wants to change room.

        .. warning:
            The controller sets roomName to
            c2w.main.constants.ROOM_IDS.MAIN_ROOM when the user
            wants to go back to the main room.
        """
        if roomName!=ROOM_IDS.MAIN_ROOM:
        
            buf2=util.format_select_film(roomName, self.num_sequence)
            self.transport.write(buf2)
            self.numJoinRoom=self.num_sequence
            self.filattente.append([self.num_sequence,1,0,buf2,(self.serverAddress, self.serverPort)])
            #reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort))    
            reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort)) 
       
           
            
        else:                     
            buf2=util.format_header(4,self.num_sequence)
            self.transport.write(buf2)
            self.numJoinRoom=self.num_sequence
            self.filattente.append([self.num_sequence,1,0,buf2,(self.serverAddress, self.serverPort)])
            #reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort))   
            reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort)) 
       
           
           


        pass

    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """

        buf2=util.format_header(2,self.num_sequence)
        self.transport.write(buf2)
        self.numDeconection=self.num_sequence
        self.filattente.append([self.num_sequence,1,0,buf2,(self.serverAddress, self.serverPort)])
        #reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort))    
        reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort)) 
       
       
        pass

    def ajoutmsg(self,recu,recuList):
        """
        """
        
        if(len(self.recu)>=4):
            orig=0       
            longueur = util.get_packet_lenght(self.recu) 
            length=len(self.recu)                                   
           
            self.recuList.append(self.recu[orig:longueur])
            orig=longueur
            self.recu=self.recu[orig:]
            if longueur<length:
               self.ajoutmsg(self.recu,self.recuList)

            else:
                self.recu=b''
        
        pass

    def dataReceived(self, data):
        """
        :param data: The data received from the client (not necessarily
                     an entire message!)

        Twisted calls this method whenever new data is received on this
        connection.
        """ 
    
        print('data recue : '+str(data))
        self.recu = self.recu + data         

        if(len(self.recu)>=4): 
            orig=0          
            longueur = util.get_packet_lenght(self.recu) 
            length=len(self.recu)                                   
            while(length<longueur):
                self.recu = self.recu + data
                length=len(self.recu)  

            self.recuList.append(self.recu[orig:longueur])
            orig=longueur
            self.recu=self.recu[orig:]
            if longueur<length:
               self.ajoutmsg(self.recu,self.recuList)

            else:
                self.recu=b''
       
        print('-----------------travaillons sur ca------------',self.recuList)
    
        for packet in self.recuList:
            packet_type=util.get_type(packet)
            packet_numSeq= util.get_numSequence (packet)         

            if packet_type ==0:  #----------------------- Reception d'un ACK
            
                self.traitementAck(packet_numSeq)
                
               
                if packet_numSeq==self.numDeconection and packet_numSeq>0:
                    print('-----------------SE BARRER------------')
                    self.clientProxy.applicationQuit()
                if packet_numSeq==self.numJoinRoom and packet_numSeq>0:
                    print('-----------------SE BARRER------------')
                    self.clientProxy.joinRoomOKONE()

                self.recu=b''

            
            if packet_type == 7: # ---------------------------  ACCEPTATION DE CONNECTION

                buf=util.format_ack(packet_numSeq)
                self.transport.write(buf)
                #self.num_sequence_server+=1
                print("----------------LA CONO EST ACCEPTE-----------")
                
                self.recu=b''
            if packet_type ==5:  # ----------------------------Reception liste des films
                
                buf=util.format_ack(packet_numSeq)
                self.transport.write(buf)
                #self.num_sequence_server+=1
              

                print("----------------LES FILMS SONT RECUS-----------")
                self.movies=util.get_moviesList(packet)     

                self.recu=b''                     

            elif packet_type ==6:  # Reception liste des Users

                if self.listUser==[]:

                    buf=util.format_ack(packet_numSeq)
                    self.transport.write(buf)
                    #self.num_sequence_server+=1


                    print("********************************Reception USER**************************")
                   
                    self.listUser=util.get_usersList(packet,self.movies)                         
                    
                    self.clientProxy.initCompleteONE(self.listUser,self.movies)
                    
                elif self.listUser!=[]:

                    print("------------------ACTUALISATION DES USER----------------")
                    buf=util.format_ack(packet_numSeq)
                    self.transport.write(buf)
                    #self.num_sequence_server+=1  
                                      
                    self.listUser=util.get_usersList(packet,self.movies)
                    self.clientProxy.setUserListONE(self.listUser)           
           
                self.recu=b''
            elif packet_type==8:
                buf=util.format_ack(packet_numSeq)
                self.transport.write(buf)
                #self.num_sequence_server+=1

                self.clientProxy.connectionRejectedONE("\nLe pseudo que vous avez entrez est deja utilisé, ou trop long.\nVeuillez réessayer avec un autre") 
                self.recu=b''

            elif packet_type==9:  #
                
                buf=util.format_ack(packet_numSeq)
                self.transport.write(buf)
                #self.num_sequence_server+=1


                sender=util.get_username_fromChat(packet)
                message=util.get_message(packet)
                if sender!=self.username:
                        self.clientProxy.chatMessageReceivedONE(sender,message)
                
                self.recu=b''
        
        self.recuList=[]

        pass   
