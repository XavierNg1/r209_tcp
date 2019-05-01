# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import c2w.protocol.util as util
import logging
import struct
from twisted.internet import reactor

#Generating the token
import random
token = random.getrandbits(24)

from c2w.main.constants import ROOM_IDS


logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_server_protocol')


class c2wUdpChatServerProtocol(DatagramProtocol):

    def __init__(self, serverProxy, lossPr):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param lossPr: The packet loss probability for outgoing packets.  Do
            not modify this value!

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """
        #: The serverProxy, which the protocol must use
        #: to interact with the server (to access the movie list and to 
        #: access and modify the user list).
        self.serverProxy = serverProxy
        self.lossPr = lossPr
        #self.num_sequence=0
        self.usersList=[]
        #self.movies=[]
        self.filattente=[]
        self.username=""
        #self.num_sequence_client=0
        self.num_error=0
        self.retrans_client=0

        
    # fonction pour verifier si on a recu un ack
    def traitementAck(self,numSeq,host_port): 	 
        for p in self.filattente:             	 
            if (p[4]==host_port):
                if (p[0]==numSeq):
                    p[2]=1
                    #print(p[0]) 
                    """
                    for user in self.usersList:
                        if (user[1]==host_port):
                            user[4]+=1
                    """
                    #print(user[4])
                    #self.filattente.remove(p)
                    print('ack envoye par le client')    

    #pass

	#fonction pour envoyer le paquet si jamais on a toujours pas recu d ack
    def sendAndWaite(self,host_port):   
        for p in self.filattente:
            if (p[4]==host_port):             	 
                if (p[1] <=6):#remission
                    if (p[2] == 0):
                        self.transport.write(p[3],p[4])
                        p[1]+=1
                        print('nombre de message envoye:'+str(p[1]))
                        reactor.callLater(1,self.sendAndWaite,p[4])
                        #reactor.run()
                    elif(p[2] == 1):
                        #print('avant',self.filattente)
                        print('Le paquet a ete aquitte',p[0])  
                        self.filattente.remove(p)
                        #self.num_sequence+=1
                        #print("Dernier num sequnce",num_sequence)
                        #print('apres',self.filattente) #reactor.callLater(0,self.sendAndWaite, (host_port[0], host_port[1]) ))

                #"""
                else:
                    d=p
                    self.filattente.remove(p)
                    print (self.usersList)
                    for user in self.usersList:
                        print("---------SUPPRESSION USER------------")
                        if user[1]==host_port:
                            self.usersList.remove(user)
                            print("*******************USER A SUPRIMER****************",user[0])
                            self.serverProxy.removeUser(user[0])
                            #print("/***********************************USER A SUPRIMER",self.usersList)
                            #self.serverProxy.getUserList()
                            #print("/***********************************USER A SUPRIMER",self.serverProxy.getUserList())


                    if self.usersList!=[] and  util.get_type(d[3])!=8:
                        print("tu fais quoi las \n\n",util.get_type(d[3])!=8)                        
                        for user in self.usersList:
                            listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),user[4])
                            self.transport.write(listUser, (user[1][0], user[1][1]))
                            self.filattente.append([user[4],1,0,listUser,(user[1][0], user[1][1])])
                            reactor.callLater(1,self.sendAndWaite, (user[1][0], user[1][1]) )
                              
                            
                #"""            
                
                #"""
                    #break
                            #print('apres',self.filattente) #reactor.callLater(0,self.sendAndWaite, (host_port[0], host_port[1]) ))
            #return self.num_sequence
        #pass

    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport


    def datagramReceived(self, datagram, host_port):
        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.
        
        Twisted calls this method when the server has received a UDP
        packet.  You cannot change the signature of this method.
        """

       # if is not (firstconnection):
        num_sequence_server=0
        num_sequence_client=0
        for user in self.usersList:
            if (user[1]==host_port):                
                num_sequence_server=user[4]                
                num_sequence_client=user[5]

        print('------------server maj-----',num_sequence_server)
        print('------------client maj-----',num_sequence_client)
         
                
                

        packet_type=util.get_type(datagram)
        print("-----------------------PACKECT TYPE---------",packet_type)
        #num_sequence_client=util.get_numSequence(datagram)

        

        if packet_type ==0:  #Reception ACK
            num_sequence=util.get_numSequence(datagram)
            self.traitementAck(num_sequence,host_port)     
            #self.num_sequence+=1      

            
            #for user in self.usersList:
             #   if user[1]==host_port:
              #      print('CHUI LA ')
            existe=False
            
            for user in self.usersList:
                if user[1]==host_port:
                    existe=True
                    
                    
            
            if num_sequence_server==1 and existe==True:
                
                
                
                #self.serverProxy.addUser(userName,ROOM_IDS.MAIN_ROOM,None,host_port)
                

                print("********************************ENVOIE LISTE DES FILM**************************")
                #self.num_sequence=1
                # print(util.format_moviesList(self.serverProxy.getMovieList()))
                listMovie=util.format_moviesList(self.serverProxy.getMovieList())
                #print(util.get_moviesList(util.format_moviesList(self.serverProxy.getMovieList())))
                self.filattente.append([1,1,0,listMovie,(host_port[0], host_port[1])])
                self.transport.write(listMovie, (host_port[0], host_port[1]))
                reactor.callLater(1,self.sendAndWaite, (host_port[0], host_port[1]) )
                for user in self.usersList:
                        if (user[1]==host_port):
                            user[4]+=1

            
            elif num_sequence_server==2 and existe==True:
                print("********************************ENVOIE LISTE DES USER**************************")
                #print(util.format_usersList(self.usersList,self.serverProxy.getMovieList()))
                listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),num_sequence_server)
                #self.filattente.append([2,1,0,listUser,(host_port[0], host_port[1])])
                self.transport.write(listUser, (host_port[0], host_port[1]))
                self.filattente.append([2,1,0,listUser,(host_port[0], host_port[1])])####AJOUTER POUR TESTER LA RETANSMISSION DE LA LIST DES USER
                reactor.callLater(1,self.sendAndWaite, (host_port[0], host_port[1]) )
                for user in self.usersList:
                        if (user[1]==host_port):
                            user[4]+=1
                
                """
                for user in self.usersList:
                    listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),user[4])
                    self.transport.write(listUser, (user[1][0], user[1][1]))
                    self.filattente.append([user[4],1,0,listUser,(user[1][0], user[1][1])])####AJOUTER POUR TESTER LA RETANSMISSION DE LA LIST DES USER
                    reactor.callLater(1,self.sendAndWaite, (user[1][0], user[1][1]) )
                """

                if self.usersList!=[]:
                    #listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),self.num_sequence)
                    for user in self.usersList:
                        if user[1]!=host_port:
                            listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),user[4])
                            print('-----------IL YA UN NOUVEAU-------------')
                            print('---------voivi mon num seq-------',user[4])
                            self.transport.write(listUser, (user[1][0], user[1][1]))
                            self.filattente.append([user[4],1,0,listUser,(user[1][0], user[1][1])])
                            reactor.callLater(1,self.sendAndWaite, (user[1][0], user[1][1]) )
                            user[4]+=1
                            

                    #buf=util.format_chat(self.num_sequence,9,'SERVER','CECI N EST PAS UN CLIP\n')
                    #self.transport.write(buf, (user[1][0], user[1][1]))
    
                    #print(util.get_username_fromChat(buf)," :")

                    #print(util.get_message(buf))
                

                #self.transport.write(listUser, (host_port[0], host_port[1]))
                
                
                
                #reactor.callLater(1,self.sendAndWaite, (host_port[0], host_port[1]) )
                
                #print(util.get_usersList(listUser,util.get_moviesList(util.format_moviesList(self.serverProxy.getMovieList()))))
          #  print(packet_type)
        #if num_sequence_client==self.num_sequence_client:
        num_sequence_client_recu=util.get_numSequence(datagram)
        if num_sequence_client==num_sequence_client_recu and packet_type !=0:
            #num_sequence_client=util.get_numSequence(datagram)
            
            
            if packet_type ==1:  # Reception login request 

                               
                                
                pseudo=True
                userName=util.get_userName_connection(datagram)
                
                for user in self.usersList:                    
                    if userName==user[0] or len(userName)>256:
                        pseudo=False
                        print("chammmmmmmmmmmmmmmmmmmmmmpion chaneg de non")

                print(pseudo)
                
                
                if pseudo==True:

                    buf=util.format_ack(num_sequence_client)                    
                    self.transport.write(buf, (host_port[0], host_port[1]))
                    
                    
                    iDUser=self.serverProxy.addUser(userName,ROOM_IDS.MAIN_ROOM,None,host_port) #retounre l'ID du client

                    iDRoom=0
                    nameRoom="main_room"
                    num_sequence_Server=0
                    num_sequence_client=0
                    #error_counter=0
                    self.usersList.append([userName,host_port,nameRoom,iDRoom,num_sequence_Server,num_sequence_client]) #le second 0 esl l'ID de MainROOM
                    #self.usersList.append([userName,host_port,nameRoom,iDRoom,num_sequence_Server,num_sequence_client,error_counter]) #le 
                    print("*****************LA LIST DES USERS")
                    print(self.usersList)
                   # print(self.serverProxy.getUserList()[0].userChatRoom)
                    #print(self.serverProxy.getUserList())
                    #print("oooooooooooooooooooooooooooooooooooo")
                    #print("******^^^^^^^^^^^^^^**********")
                    print(iDUser)
                    #print("******^^^^^^^^^^^^^^**********")

                    # print(self.serverProxy.getMovieList()[0])
                    
                    for user in self.usersList:
                        if (user[1]==host_port):
                            user[5]+=1
                    
                    """
                    Traitement a effectuer !!!
                    """

                    #sending the ACK message-----------------------APRES ENVOIE ACK +1 AU NUM SÉQUENCE DU CLIENT
                    
                   


                    #sending the connection message
                    #num_seq = 0
                    #num_seq = num_seq << 4
                    #connection_type = 7
                    #seq_and_ack = num_seq + connection_type
                    #ack_length = 4
                    #buf = struct.pack('!hh', ack_length, seq_and_ack)
                    #self.transport.connect(host_port[0], host_port[1])
                    #self.transport.write(answer.encode('utf-8'))

                    buf2=util.format_header(7,0)
                    self.transport.write(buf2, (host_port[0], host_port[1]))
                    self.filattente.append([0,1,0,buf2,(host_port[0], host_port[1])])
                    #print("**********",self.num_sequence)
                    reactor.callLater(1,self.sendAndWaite, (host_port[0], host_port[1]))
                    
                    for user in self.usersList:
                        if (user[1]==host_port):
                            user[4]+=1

                    #reactor.callLater(1,print,self.num_sequence)
                    #reactor.run()
                    #reactor.stop
                    #""" DECOMMENTER POUR FAIRE FONCTIONNER LE TEST MOVIELIST
                    
                    #reactor.callLater(1,self.sendAndWaite, (host_port[0], host_port[1]) )

                    #"""
                        

                    #reactor.callLater(1,self.sendAndWaite, (host_port[0], host_port[1]) )

                    
                    #   print('test',self.filattente)
                        
                    #   print('avant',self.filattente)
                        #self.transport.write(buf2, (host_port[0], host_port[1]))
                        
                        #reactor.run()
                    
                    """
                    Test du Usernanme
                    """

                elif pseudo==False:
                    buf=util.format_ack(num_sequence_client_recu)

                    self.transport.write(buf, (host_port[0], host_port[1]))
                    """
                    for user in self.usersList:
                        if (user[1]==host_port):
                            user[5]+=1

                    """


                    buf2=util.format_header(8,0)
                    self.transport.write(buf2, (host_port[0], host_port[1]))
                    self.filattente.append([0,1,0,buf2,(host_port[0], host_port[1])])#jai mi 1 pour voir
                    #print("**********",self.num_sequence)
                    reactor.callLater(1,self.sendAndWaite, (host_port[0], host_port[1]) )
                    """
                    for user in self.usersList:
                        if (user[1]==host_port):
                            user[4]+=1

                    """

                #"""
            elif packet_type ==2 :  # Quitter Application 


                print("jeveuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuupannnnnnnnnnnn")
                buf=util.format_ack(num_sequence_client)
                print("jeveuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuupannnnnnnnnnnn")
                self.transport.write(buf, (host_port[0], host_port[1]))
                for user in self.usersList:
                        if (user[1]==host_port):
                            user[5]+=1
                print("jeveuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuupannnnnnnnnnnn")
                
            
                for user in self.usersList:
                    print("rttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt")
                    if user[1]==host_port:
                        self.usersList.remove(user)
                        print("/***********************************USER A SUPRIMER",user[0])
                        self.serverProxy.removeUser(user[0])
                       # print("/***********************************USER A SUPRIMER",self.usersList)
                        #self.serverProxy.getUserList()
                      #  print("/***********************************USER A SUPRIMER",self.serverProxy.getUserList())


                if self.usersList!=[]:
                    #listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),self.num_sequence)
                    for user in self.usersList:
                        listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),user[4])
                        self.transport.write(listUser, (user[1][0], user[1][1]))
                        self.filattente.append([user[4],1,0,listUser,(user[1][0], user[1][1])])
                        reactor.callLater(1,self.sendAndWaite, (user[1][0], user[1][1]) )
                        user[4]+=1

            #"""

        
        
            elif packet_type == 3: # Choix de film
                #self.users.append(self.username)

                buf=util.format_ack(num_sequence_client)
                self.transport.write(buf, (host_port[0], host_port[1]))
                for user in self.usersList:
                        if (user[1]==host_port):
                            user[5]+=1

                print("-------------------------------AFFICHER SALLE VOULUE--------",util.get_nom_film(datagram))
                nameRoom=util.get_nom_film(datagram)
                #self.serverProxy.startStreamingMovie(nameRoom)


                for user in self.usersList:
                    print("rttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt")
                    if user[1]==host_port:
                        user[2]=nameRoom
                        #listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),user[4])
                        for m in self.serverProxy.getMovieList():
                            if nameRoom==m.movieTitle:
                                user[3]=m.movieId
                                

                """
                print("********************************ENVOIE LISTE DES USER**************************")
                #print(util.format_usersList(self.usersList,self.serverProxy.getMovieList()))
                listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),self.num_sequence)
                #self.filattente.append([2,1,0,listUser,(host_port[0], host_port[1])])
                self.transport.write(listUser, (host_port[0], host_port[1]))
                self.filattente.append([self.num_sequence,1,0,listUser,(host_port[0], host_port[1])])####AJOUTER POUR TESTER LA RETANSMISSION DE LA LIST DES USER
                reactor.callLater(1,self.sendAndWaite, (host_port[0], host_port[1]) )
                
                
                for user in self.usersList:
                    listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),user[4])
                    self.transport.write(listUser, (user[1][0], user[1][1]))
                    self.filattente.append([user[4],1,0,listUser,(user[1][0], user[1][1])])####AJOUTER POUR TESTER LA RETANSMISSION DE LA LIST DES USER
                    reactor.callLater(1,self.sendAndWaite, (user[1][0], user[1][1]) )
                """

                if self.usersList!=[]:
                    #listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),self.num_sequence)
                    for user in self.usersList:
                        #if user[1]!=host_port:
                            listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),user[4])
                            self.transport.write(listUser, (user[1][0], user[1][1]))
                            self.filattente.append([user[4],1,0,listUser,(user[1][0], user[1][1])])
                            reactor.callLater(1,self.sendAndWaite, (user[1][0], user[1][1]) )
                            user[4]+=1




                self.serverProxy.startStreamingMovie(nameRoom)######ne peut pas placer ca la attente de ack dabord


                
                print(packet_type)
            

            elif packet_type==4: # QUITTER SALLE DES FILMS 
                

                print("Je ne veux plus le regardé ce film")
                buf=util.format_ack(num_sequence_client)
                self.transport.write(buf, (host_port[0], host_port[1]))
                for user in self.usersList:
                        if (user[1]==host_port):
                            user[5]+=1

                
                for user in self.usersList:
                    print("rttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt")
                    if user[1]==host_port:
                        #self.serverProxy.stopStreamingMovie(user[2])
                        #previousRoom=user[2]
                        user[2]="main_room"
                        user[3]=0
                        #listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),self.num_sequence)
                        #self.serverProxy.stopStreamingMovie(previousRoom)
                """        
                vide=0
                for user in self.usersList:
                    if user[2]==previousRoom:
                        vide=1
                        
                if vide==0:
                    self.serverProxy.stopStreamingMovie(previousRoom)

                """
                #self.filattente.append([2,1,0,listUser,(host_port[0], host_port[1])])
                
                
                for user in self.usersList:
                    listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),user[4])
                    self.transport.write(listUser, (user[1][0], user[1][1]))
                    self.filattente.append([user[4],1,0,listUser,(user[1][0], user[1][1])])####AJOUTER POUR TESTER LA RETANSMISSION DE LA LIST DES USER
                    reactor.callLater(1,self.sendAndWaite, (user[1][0], user[1][1]) )
                    user[4]+=1
                
                



            elif packet_type==9:  # MESSAGE DE CHAT 
                print("JE VEUX KOZER")

                buf=util.format_ack(num_sequence_client)
                self.transport.write(buf, (host_port[0], host_port[1]))
                for user in self.usersList:
                        if (user[1]==host_port):
                            user[5]+=1

                
                sender=util.get_username_fromChat(datagram)
                messageRecu=util.get_message(datagram)


                #buf=util.format_chat(self.num_sequence,9,'Server','Désole le site est en maintenace !!!\n')
                
                #buf=util.format_chat(self.num_sequence,9,sender,messageRecu)            
                for user in self.usersList:
                    if user[1]==host_port:
                        roomCible=user[2]

                
                for user in self.usersList:
                    #if user[0]!=sender and user[2]==roomCible:
                    if user[2]==roomCible:
                        buf=util.format_chat(user[4],9,sender,messageRecu)    
                        self.transport.write(buf, (user[1][0], user[1][1]))
                        self.filattente.append([user[4],1,0,buf,(user[1][0], user[1][1])])####AJOUTER POUR TESTER LA RETANSMISSION DE LA LIST DES USER
                        reactor.callLater(1,self.sendAndWaite, (user[1][0], user[1][1]) )
                        user[4]+=1
                        
                #for user in self.usersList:
                #   self.transport.write(listUser, (user[1][0], user[1][1]))
                #  self.filattente.append([user[4],1,0,listUser,(user[1][0], user[1][1])])####AJOUTER POUR TESTER LA RETANSMISSION DE LA LIST DES USER
                # reactor.callLater(1,self.sendAndWaite, (user[1][0], user[1][1]) )



            """    
            #Receiving the login request
            msg_length = struct.unpack('!H', datagram[0:2])[0]
            num_seq_and_type = struct.unpack('!H', datagram[2:4])[0]
            num_seq_msg = num_seq_and_type >> 4
            connection_type = num_seq_and_type & 15
            userName = struct.unpack(str(len(datagram[4:]))+'s', datagram[4:])[0].decode('utf-8')
            print(connection_type)
            print(num_seq_msg)
            #print(self.serverProxy.getMovieList())

            print(userName)
            #print(self.serverProxy.getMovieList())
                    
            #self.serverProxy.addUser(userName,ROOM_IDS.MAIN_ROOM,None,host_port)  
            
            #sending the ACK message
            num_seq = 0
            num_seq = num_seq << 4
            ack_type = 0
            seq_and_ack = num_seq + ack_type
            ack_length = 4
            buf = struct.pack('!hh', ack_length, seq_and_ack)
            #self.transport.connect(host_port[0], host_port[1])
            #self.transport.write(answer.encode('utf-8'))
            self.transport.write(buf, (host_port[0], host_port[1]))
            
            #print(ROOM_IDS.MAIN_ROOM)  
            
            #sending the connection message
            num_seq = 0
            num_seq = num_seq << 4
            connection_type = 7
            seq_and_ack = num_seq + connection_type
            ack_length = 4
            buf = struct.pack('!hh', ack_length, seq_and_ack)
            #self.transport.connect(host_port[0], host_port[1])
            #self.transport.write(answer.encode('utf-8'))
            self.transport.write(buf, (host_port[0], host_port[1]))

            self.transport.write(buf, (host_port[0], host_port[1]))
        """
        
        elif num_sequence_client!=num_sequence_client_recu and packet_type !=0:
                
                    
                
            print("+-+-+-+-+-+-Jai recu un doublon on dirait+-+-+-+-+-+-+-")
            buf=util.format_ack(num_sequence_client_recu)                
            self.transport.write(buf, (host_port[0], host_port[1]))
            """
            error_counter=0
            fo user in usersList:
                if user[1]==host_port:
                    error_counter=user[6]
            
            if error_counter=<7:
                print("+-+-+-+-+-+-Jai recu un doublon on dirait+-+-+-+-+-+-+-")
                buf=util.format_ack(num_sequence_client_recu)                
                self.transport.write(buf, (host_port[0], host_port[1]))

            elif error_counter==7:
                self.usersList.remove(user)
                #print("/***********************************USER A SUPRIMER",user[0])
                self.serverProxy.removeUser(user[0])
                print("/***********************************USER A SUPRIMER",self.usersList)
                #self.serverProxy.getUserList()
                #print("/***********************************USER A SUPRIMER",self.serverProxy.getUserList())
                
                if self.usersList!=[]:
                    #listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),self.num_sequence)
                    for user in self.usersList:
                    listUser=util.format_usersList(self.usersList,self.serverProxy.getMovieList(),user[4])
                    self.transport.write(listUser, (user[1][0], user[1][1]))
                    self.filattente.append([user[4],1,0,listUser,(user[1][0], user[1][1])])
                    reactor.callLater(1,self.sendAndWaite, (user[1][0], user[1][1]))
                    user[4]+=1





    

            """
            
        """
        for user in self.usersList:
            if user[1]==host_port:
                print("mon num sequence")
                #user[4]=num_sequence
                #user[5]=num_sequence_client
                print(user[0])
                print("----------------------------------------------------------")
                print("num sequence du server",user[4])
                print(num_sequence)
                print("num sequence du client attendue ",user[5])

        """
       

           
        #position du pass à revoir 
        pass
