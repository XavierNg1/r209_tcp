# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import c2w.protocol.util as util
import logging
import struct
from twisted.internet import reactor
import time
from c2w.main.constants import ROOM_IDS



#Importing custom classes
from .packets import Packet
from .util import *

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_client_protocol')


class c2wUdpChatClientProtocol(DatagramProtocol):

    def __init__(self, serverAddress, serverPort, clientProxy, lossPr):
        """
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param serverPort: The port number used by the c2w server,
            given by the user.
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attributes:

        .. attribute:: serverAddress

            The IP address of the c2w server.

        .. attribute:: serverPort

            The port number of the c2w server.

        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        #: The IP address of the c2w server.
        self.serverAddress = serverAddress
        #: The port number of the c2w server.
        self.serverPort = serverPort 
        #: The clientProxy, which the protocol must use
        #: to interact with the Graphical User Interface.
        self.clientProxy = clientProxy
        self.lossPr = lossPr
        self.num_sequence=0
        self.num_sequence_server=0
        self.users=[]
        self.numDeconection=0
        self.numJoinRoom=0
        self.numMainRoom=0
        self.listUser=[]
        self.movies=[]
        self.filattente=[]
        self.username=''
        self.num_error=0
        self.error_count=0
        self.retrans_server=0


    # fonction pour verifier si on a recu un ack
    def traitementAck(self,numSeq):
            
        for p in self.filattente :
                if (p[0]==numSeq):
                    p[2]=1
                    #print(p)                    
                    #print(self.filattente)
                    #if numSeq==self.numDeconection and numSeq>=1:
                     #   self.clientProxy.applicationQuit()
                      #  break 
                    self.num_sequence+=1
                    print(self.num_sequence)
                    print('******************ack envoye par le serveur')
                    self.filattente.remove(p)
                            
    #fonction pour envoyer le paquet si jamais on a toujours pas recu d ack
    def sendAndWait(self,host_port):
        for p in self.filattente:
                if (p[4]==host_port):
                    print(self.filattente)  
                    if (p[1] <= 7): # 6+1 correspond au nombre maximum de fois qu'on doit ramener un paquet
                        if (p[2] == 0):
                            self.transport.write(p[3],host_port)
                            p[1]+=1
                            print(self.filattente)
                            print('nombre de message envoye:'+str(p[1]))
                            reactor.callLater(1,self.sendAndWait,host_port)
                        elif(p[2] == 1):
                            print('Le paquet a ete aquitte')  
                            self.filattente.remove(p)   
                            
                            
                    else:
                        print('Le paquet envoye est perdu')
                        self.filattente.remove(p)
                        
                        #EFFECTUER LES COMMANDE DE DECONNECTION ET AFFICAHGE DE MESSAGE DE DECONNEXION 
                        #DANS LE CAS DUNE CONNEXION, DECONNEXION, CHANGEMNT DE ROOM
                        self.clientProxy.connectionRejectedONE("\nLa connexion au serveur à été rompue\nVous devez vous reconnecter")
                        #self.clientProxy.applicationQuit()

        

    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport

    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The client proxy calls this function when the user clicks on
        the login button.
        """
        """
        #Connecting to the server
        #self.transport.connect(self.serverAddress, self.serverPort)
        #The message length taille du paquet 
        msg_length = 4 + len(userName.encode('utf-8'))
        #Combining the sequence number and the type
        #num_seq = self.num_sequence << 4 
        #connection_type = 1
        seq_and_connection = util.prepare_header(self.num_sequence,1)
        #print(bin(seq_and_connection))
        #Packing the username
        length_username = str(len(userName))
        buf = struct.pack('!hh'+length_username+'s', msg_length, seq_and_connection, userName.encode('utf-8'))
        self.transport.write(buf, (self.serverAddress, self.serverPort))
        """
        self.username=userName
        buf=util.format_login(userName)
        self.transport.write(buf, (self.serverAddress, self.serverPort))     
      
        
        self.filattente.append([0,1,0,buf,(self.serverAddress, self.serverPort)])  
        print(self.filattente)
        reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort))    
        
       
        moduleLogger.debug('loginRequest called with username=%s', userName)

        
    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string

        Called by the client proxy  when the user has decided to send
        a chat message

        .. note::
           This is the only function handling chat messages, irrespective
           of the room where the user is.  Therefore it is up to the
           c2wChatClientProctocol or to the server to make sure that this
           message is handled properly, i.e., it is shown only by the
           client(s) who are in the same room.
        """
        buf=util.format_chat(self.num_sequence,9,self.username,message)
        self.transport.write(buf, (self.serverAddress, self.serverPort))

        #self.transport.write(buf, (self.serverAddress, self.serverPort))

        #self.transport.write(buf, (self.serverAddress, self.serverPort))

        self.filattente.append([self.num_sequence,1,0,buf,(self.serverAddress, self.serverPort)])  
        #print(self.filattente)
        reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort))    

        #self.transport.write(buf, (self.serverAddress, self.serverPort))

        #self.transport.write(buf, (self.serverAddress, self.serverPort))
       
        print(util.get_username_fromChat(buf)," :")

        print(util.get_message_test(buf))



        pass

    def sendJoinRoomRequestOIE(self, roomName):
        """
        :param roomName: The room name (or movie title.)

        Called by the client proxy  when the user
        has clicked on the watch button or the leave button,
        indicating that she/he wants to change room.

    
        #A faire envoyer demande de deconnexion
        buf2=util.format_select_film(roomName, self.num_sequence)
        print("jeveuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuupannnnnnnnnnnn")
        self.transport.write(buf2, (self.serverAddress, self.serverPort))
        self.filattente.append([self.num_sequence,1,0,buf2,(self.serverAddress, self.serverPort)])
        reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort))    
        self.numJoinRoom=self.num_sequence
         
         RETRANSMISSION PAS ENCORE GERER+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-++-+-+-+
        
        #print("jeeeeeeeeeeveuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuupannnnnnnnnnnn")

        .. warning:
            The controller sets roomName to
            c2w.main.constants.ROOM_IDS.MAIN_ROOM when the user
            wants to go back to the main room.
        """
        if roomName!=ROOM_IDS.MAIN_ROOM:
        
            buf2=util.format_select_film(roomName, self.num_sequence)
            print("jeveuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuupannnnnnnnnnnn")
            self.transport.write(buf2, (self.serverAddress, self.serverPort))
            self.numJoinRoom=self.num_sequence
            self.filattente.append([self.num_sequence,1,0,buf2,(self.serverAddress, self.serverPort)])
            reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort))    
            #self.clientProxy.joinRoomOKONE()

        else:            
            buf2=util.format_header(4,self.num_sequence)
            #print("jeveuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuupannnnnnnnnnnn")
            self.transport.write(buf2, (self.serverAddress, self.serverPort))
            self.numJoinRoom=self.num_sequence
            self.filattente.append([self.num_sequence,1,0,buf2,(self.serverAddress, self.serverPort)])
            reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort))    
            #self.clientProxy.joinRoomOKONE()
        #"""

        #self.clientProxy.joinRoomOKONE()

        pass

    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """

        #"""
        #A faire envoyer demande de deconnexion
        buf2=util.format_header(2,self.num_sequence)
        print("jeveuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuupannnnnnnnnnnn")
        self.transport.write(buf2, (self.serverAddress, self.serverPort))
        self.numDeconection=self.num_sequence
        self.filattente.append([self.num_sequence,1,0,buf2,(self.serverAddress, self.serverPort)])
        reactor.callLater(1,self.sendAndWait,(self.serverAddress, self.serverPort))    
       
        #""" 

        print("jeeeeeeeeeeveuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuupannnnnnnnnnnn")
        #self.clientProxy.applicationQuit()


        
        pass

    def datagramReceived(self, datagram, host_port):
        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.

        Called **by Twisted** when the client has received a UDP
        packet.       
       
        """
        packet_type=util.get_type(datagram)
        #packet_numSeq= util.get_numSequence (datagram)

        if packet_type ==0:  #Reception d'un ACK
            packet_numSeq= util.get_numSequence (datagram)
            self.traitementAck(packet_numSeq)
            print("*******************ACK DU SERVER",packet_numSeq)
            print("************************MON NUM SEQ",self.num_sequence)
            print("****-----------------*ACK CONNEXION REQUEST****")

            if packet_numSeq==self.numDeconection and packet_numSeq>0:
                self.clientProxy.applicationQuit()

            if packet_numSeq==self.numJoinRoom and packet_numSeq>0:
                self.clientProxy.joinRoomOKONE()

        packet_numSeq= util.get_numSequence (datagram)
        if self.num_sequence_server==packet_numSeq and packet_type !=0:

            self.retrans_server=0
            self.error_count=0
        #
            if packet_type ==5:  # Reception liste des films
                

                buf=util.format_ack(packet_numSeq)
                self.transport.write(buf, (host_port[0], host_port[1]))

                self.num_sequence_server+=1

                #sending the ACK message-----------------------APRES ENVOIE ACK +1 AU NUM SÉQUENCE DU CLIENT AFAIRE


                print("*******************ACK DU SERVER",packet_numSeq)
                print("************************MON NUM SEQ",self.num_sequence)
                self.movies=util.get_moviesList(datagram)
                print(self.movies)
                
                """""""""""""""""""""""" 
                #self.clientProxy.initCompleteONE(self.listUser,self.movies)
                #print(packet_type)  
                """"""""""""


            elif packet_type ==6:  # Reception liste des Users

                if self.listUser==[]:

                    buf=util.format_ack(packet_numSeq)
                    self.transport.write(buf, (host_port[0], host_port[1]))
                    self.num_sequence_server+=1


                    print("********************************Reception USER**************************")
                    #print(util.format_usersList(self.usersList,self.serverProxy.getMovieList()))
                    print(datagram)
                    self.listUser=util.get_usersList(datagram,self.movies)
                    #self.filattente.append([2,1,0,listUser,(host_port[0], host_port[1])])
                    #self.transport.write(listUser, (host_port[0], host_port[1]))
                    print(self.listUser)
                    print(self.movies)
                    #print(listUser)           
                    
                    self.clientProxy.initCompleteONE(self.listUser,self.movies)
                    #print(packet_type)
                    
                else:
                    buf=util.format_ack(packet_numSeq)
                    self.transport.write(buf, (host_port[0], host_port[1]))
                    self.num_sequence_server+=1

                    
                    self.listUser=util.get_usersList(datagram,self.movies)
                    self.clientProxy.setUserListONE(self.listUser)


            elif packet_type == 7: #        --------------  ACCEPTATION DE CONNECTION
                
                #self.users.append(self.username)
                #print(packet_type)            
            # self.clientProxy.initCompleteONE(self.users,self.movies)

                buf=util.format_ack(packet_numSeq)
                self.transport.write(buf, (host_port[0], host_port[1]))  
                self.num_sequence_server+=1

                print("*******************ACK DU SERVER",packet_numSeq)
                print("***********",packet_numSeq)







            elif packet_type==8:
                buf=util.format_ack(packet_numSeq)
                self.transport.write(buf, (host_port[0], host_port[1]))
                #self.num_sequence_server+=1

                self.clientProxy.connectionRejectedONE("\nLe pseudo que vous avez entrez est deja utilisé, ou trop long.\nVeuillez réessayer avec un autre")  

                
                
            elif packet_type==9:  #
                print("Yorobo")

                buf=util.format_ack(packet_numSeq)
                self.transport.write(buf, (host_port[0], host_port[1]))
                self.num_sequence_server+=1


                sender=util.get_username_fromChat(datagram)
                message=util.get_message(datagram)
                if sender!=self.username:
                        self.clientProxy.chatMessageReceivedONE(sender,message)

        #"""
        elif self.num_sequence_server!=packet_numSeq and packet_type !=0:
        #else:
            """     
            print("+-+-+-+-+-+-Jai recu un doublon on dirait+-+-+-+-+-+-+-")
            #self.num_sequence_client
            buf=util.format_ack(packet_numSeq)
            self.transport.write(buf, (host_port[0], host_port[1]))
            #self.num_sequence_client+=1 


            """
          
            if packet_numSeq !=self.num_error:
                if self.error_count!=7:
                    self.retrans_server=0
                    self.error_count=+1
                    print("+-+-+-+-+-+-Jai recu un numSeq innatendue on dirait+-+-+-+-+-+-+-")
                    print(packet_numSeq)
                    print(self.num_sequence_server)
                    #self.num_sequence_client
                    buf=util.format_ack(packet_numSeq)
                    self.transport.write(buf, (host_port[0], host_port[1]))
                    #self.num_sequence_client+=1 
                elif self.error_count==7:
                    self.clientProxy.applicationQuit()
            
            elif packet_numSeq ==self.num_error:
                if self.retrans_server!=7 and self.error_count!=7:
                    self.error_count=+1
                    self.retrans_server+=1
                    print("+-+-+-+-+-+-Jai recu un doublon on dirait+-+-+-+-+-+-+-")
                    #self.num_sequence_client
                    buf=util.format_ack(packet_numSeq)
                    self.transport.write(buf, (host_port[0], host_port[1]))
                    #self.num_sequence_client+=1 

                elif self.retrans_server==7 or self.error_count==7:
                    self.clientProxy.applicationQuit()
                        

            self.num_error=packet_numSeq
            #"""





        #"""
        
        print("num sequence du server attendue",self.num_sequence_server)
        print("num sequence du client ",self.num_sequence)
   
        pass
