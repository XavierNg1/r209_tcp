# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
import logging
import c2w.protocol.util as util
import logging
import struct
from twisted.internet import reactor
from c2w.main.constants import ROOM_IDS

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_server_protocol')


class c2wTcpChatServerProtocol(Protocol):

    def __init__(self, serverProxy, clientAddress, clientPort):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param clientAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param clientPort: The port number used by the c2w server,
            given by the user.

        Class implementing the TCP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: clientAddress

            The IP address of the client corresponding to this 
            protocol instance.

        .. attribute:: clientPort

            The port number used by the client corresponding to this 
            protocol instance.

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.

        .. note::
            The IP address and port number of the client are provided
            only for the sake of completeness, you do not need to use
            them, as a TCP connection is already associated with only
            one client.
        """
        #: The IP address of the client corresponding to this 
        #: protocol instance.
        self.clientAddress = clientAddress
        #: The port number used by the client corresponding to this 
        #: protocol instance.
        self.clientPort = clientPort
        #: The serverProxy, which the protocol must use
        #: to interact with the user and movie store in the server.
        self.serverProxy = serverProxy
        #self.lossPr = lossPr
        #Pour verifier si on a recu l'entierete du message
        self.recu = b''
        self.num_sequence=0
        self.usersList=[]
        #self.movies=[]
        self.filattente=[]
        self.username=""
        self.recuList=[]
       



    def ajoutmsg(self,recu,recuList):

        #print('data recue'+str(data))
        #self.recu = self.recu + data
        # on verifie si l integrité du paquet est recu
        #orig=0     

        
        if(len(self.recu)>=4):
            orig=0       
            longueur = util.get_packet_lenght(self.recu) 
            length=len(self.recu)                                   
            #while(length<longueur):
             #   self.recu = self.recu + data
              #  length=len(self.recu)  

            self.recuList.append(self.recu[orig:longueur])
            orig=longueur
            self.recu=self.recu[orig:]
            if longueur<length:
               self.ajoutmsg(self.recu,self.recuList)

            else:
                self.recu=b''
        
        pass


    # fonction pour verifier si on a recu un ack
    def traitementAck(self,numSeq,host_port): 	 
        for p in self.filattente:             	 
            if (p[4]==host_port):
                if (p[0]==numSeq):
                    p[2]=1
                    print(self.num_sequence)
                    #self.filattente.remove(p)
                    print('ack envoye par le client')    

    #pass

	
    def sendAndWaite(self,host_port):   
        for p in self.filattente:
            if (p[4]==host_port):             	 
                if (p[1] <=7):#remission
                    if (p[2] == 0):
                        self.transport.write(p[3],p[4])
                        p[1]+=1
                        print('nombre de message envoye:'+str(p[1]))
                        reactor.callLater(1,self.sendAndWaite,host_port)
                      
                    elif(p[2] == 1):
                        print('avant',self.filattente)
                        print('Le paquet a ete aquitte',p[0])  
                        self.filattente.remove(p)                 
                        print("Dernier num sequnce",self.num_sequence)
                        print('apres',self.filattente)
                else:
                    print('Le paquet envoye est perdu')
                    self.filattente.remove(p)
                        
    #pass

    def dataReceived(self, data):
        """
        :param data: The data received from the client (not necessarily
                     an entire message!)

        Twisted calls this method whenever new data is received on this
        connection.
        """

        
        host_port = (self.clientAddress,self.clientPort)

        for user in self.usersList:
            if (user[1]==host_port):
                self.num_sequence=user[4]
            

        print('data recue'+str(data))
        self.recu = self.recu + data
        print(self.recu)
       
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
            print("------------mon type-------------",packet_type)
            num_sequence_client= util.get_numSequence (packet)         


            if packet_type ==0:  #Reception ACK

                self.traitementAck(num_sequence_client,host_port)

                if self.num_sequence==1:

                    print("********************************ENVOIE LISTE DES FILM**************************")
                        
                    listMovie=util.format_moviesList(self.serverProxy.getMovieList())                   
                    self.filattente.append([1,1,0,listMovie,host_port])
                    self.transport.write(listMovie) 
                    reactor.callLater(1,self.sendAndWaite, host_port)
                    
                    for user in self.usersList:
                        if user[1]==host_port:
                            user[4]+=1

                elif self.num_sequence==2:

                    print("********************************ENVOIE LISTE DES USER**************************")
                    
                   
                    for user in self.serverProxy.getUserList(): #if user.userAddress!=host_port:
                            listUser=util.format_usersList_tcp(self.serverProxy.getUserList(),self.serverProxy.getMovieList(), user.userChatInstance.usersList[0][4])
                            user.userChatInstance.filattente.append([user.userChatInstance.usersList[0][4],1,0,listUser,(user.userChatInstance.usersList[0][1][0], user.userChatInstance.usersList[0][1][1])])
                            user.userChatInstance.transport.write(listUser)
                            reactor.callLater(1,user.userChatInstance.sendAndWaite,(user.userChatInstance.usersList[0][1][0], user.userChatInstance.usersList[0][1][1]))
                            user.userChatInstance.usersList[0][4]+=1

                                      
                    

                #self.recu = b''
            
            elif packet_type ==1:  # Reception login request 
                
                buf=util.format_ack(num_sequence_client)                    
                self.transport.write(buf)
               
                userName=util.get_userName_connection(packet)
                
                
                
                if self.serverProxy.getUserByName(userName)==None and len(userName)<256:
                    iDUser=self.serverProxy.addUser(userName,ROOM_IDS.MAIN_ROOM,self,host_port) #retounre l'ID du client

                    iDRoom=0
                    nameRoom=ROOM_IDS.MAIN_ROOM#MODIF A PRENDRE EN COMPTE 
                    num_sequence_Server=0
                    self.usersList.append([userName,host_port,nameRoom,iDRoom,num_sequence_Server]) #le second 0 esl l'ID de MainROOM
                    
                    
                    buf2=util.format_header(7,0)                 
                    self.transport.write(buf2)
                    self.filattente.append([0,1,0,buf2,host_port])
                    reactor.callLater(1,self.sendAndWaite, host_port)
                    print("--------------JAI ENVOYE 7---------------")

                    for user in self.usersList:
                        if user[1]==host_port:
                            user[4]+=1


                
                elif self.serverProxy.getUserByName(userName)!=None or len(userName)>256:
                    buf=util.format_ack(num_sequence_client)
                    self.transport.write(buf)
                                        

                    buf2=util.format_header(8,0)
                    self.transport.write(buf2)
                    self.filattente.append([0,1,0,buf2,(host_port[0], host_port[1])])                   
                    reactor.callLater(1,self.sendAndWaite, (host_port[0], host_port[1]) )

                
                #self.recu = b''

            elif packet_type ==2 :  # Quitter Application 
                
                
                buf=util.format_ack(num_sequence_client)               
                self.transport.write(buf)
                #for user in self.usersList:
                 #       if (user[1]==host_port):
                  #          user[5]+=1
                self.serverProxy.removeUser(user[0])
                print("--------------DECONNEXION D'UN CLIENT-----------")

                
                if self.serverProxy.getUserList()!=[]:
                    for user in self.serverProxy.getUserList():                        
                        listUser=util.format_usersList_tcp(self.serverProxy.getUserList(),self.serverProxy.getMovieList(), user.userChatInstance.usersList[0][4])
                        user.userChatInstance.filattente.append([user.userChatInstance.usersList[0][4],1,0,listUser,(user.userChatInstance.usersList[0][1][0], user.userChatInstance.usersList[0][1][1])])
                        user.userChatInstance.transport.write(listUser)
                        reactor.callLater(1,user.userChatInstance.sendAndWaite,(user.userChatInstance.usersList[0][1][0], user.userChatInstance.usersList[0][1][1]))
                        user.userChatInstance.usersList[0][4]+=1



                #self.recu = b''

            
            elif packet_type == 3: # Choix de film
                

                buf=util.format_ack(num_sequence_client)
                self.transport.write(buf)
                
                #for user in self.usersList:
                 #       if (user[1]==host_port):
                  #          user[5]+=1

                print("-----------AFFICHER SALLE VOULUE--------",util.get_nom_film(packet))
                nameRoom=util.get_nom_film(packet)
                

                for user in self.usersList:
                   
                    if user[1]==host_port:
                        user[2]=nameRoom
                        for m in self.serverProxy.getMovieList():
                            if nameRoom==m.movieTitle:
                                user[3]=m.movieId
                                self.serverProxy.updateUserChatroom(user[0], nameRoom)
                        
                
                for user in self.serverProxy.getUserList():
                        listUser=util.format_usersList_tcp(self.serverProxy.getUserList(),self.serverProxy.getMovieList(), user.userChatInstance.usersList[0][4])
                        user.userChatInstance.filattente.append([user.userChatInstance.usersList[0][4],1,0,listUser,(user.userChatInstance.usersList[0][1][0], user.userChatInstance.usersList[0][1][1])])
                        user.userChatInstance.transport.write(listUser)
                        reactor.callLater(1,user.userChatInstance.sendAndWaite,(user.userChatInstance.usersList[0][1][0], user.userChatInstance.usersList[0][1][1]))
                        user.userChatInstance.usersList[0][4]+=1

                      
                self.serverProxy.startStreamingMovie(nameRoom)#ne peut pas placer ca la attente de ack dabord

                #self.recu = b''


            elif packet_type==4: # QUITTER SALLE DES FILMS 
                           
                buf=util.format_ack(num_sequence_client)
                self.transport.write(buf)
                
                #for user in self.usersList:
                 #       if (user[1]==host_port):
                      #      user[5]+=1

                
                for user in self.usersList:                   
                    if user[1]==host_port:                     
                        user[2]=ROOM_IDS.MAIN_ROOM
                        user[3]=0                        
                        self.serverProxy.updateUserChatroom(user[0],ROOM_IDS.MAIN_ROOM)                            
                
               
                
                for user in self.serverProxy.getUserList():
                       
                        listUser=util.format_usersList_tcp(self.serverProxy.getUserList(),self.serverProxy.getMovieList(), user.userChatInstance.usersList[0][4])
                        user.userChatInstance.filattente.append([user.userChatInstance.usersList[0][4],1,0,listUser,(user.userChatInstance.usersList[0][1][0], user.userChatInstance.usersList[0][1][1])])
                        user.userChatInstance.transport.write(listUser)
                        reactor.callLater(1,user.userChatInstance.sendAndWaite,(user.userChatInstance.usersList[0][1][0], user.userChatInstance.usersList[0][1][1]))
                        user.userChatInstance.usersList[0][4]+=1

            elif packet_type==9:  # MESSAGE DE CHAT 
                
                print("-------Nouveau Message--------")
                buf=util.format_ack(num_sequence_client)
                self.transport.write(buf)
                #for user in self.usersList:
                 #       if (user[1]==host_port):
                  #          user[5]+=1
                
                sender=util.get_username_fromChat(packet)
                messageRecu=util.get_message(packet)
            
                for user in self.usersList:
                    if user[1]==host_port:
                        roomCible=user[2]
                        print(roomCible)
                
                
                        
                for user in self.serverProxy.getUserList():
                    if user.userChatRoom==roomCible:
                        buf=util.format_chat(user.userChatInstance.usersList[0][4],9,sender,messageRecu)  
                        user.userChatInstance.filattente.append([user.userChatInstance.usersList[0][4],1,0,buf,(user.userChatInstance.usersList[0][1][0], user.userChatInstance.usersList[0][1][1])])
                        user.userChatInstance.transport.write(buf)
                        reactor.callLater(1,user.userChatInstance.sendAndWaite,(user.userChatInstance.usersList[0][1][0], user.userChatInstance.usersList[0][1][1]))
                        user.userChatInstance.usersList[0][4]+=1

            self.num_sequence=0
            #self.recu = b''
            self.recuList=[]
            pass
