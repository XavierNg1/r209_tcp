# -*- coding: utf-8 -*-
import struct
import re
from c2w.main.constants import ROOM_IDS


def prepare_header(numSeq,code_type):
        return (numSeq << 4 )+ code_type
 

def format_ack(num_sequence):
        num_seq = num_sequence << 4
        ack_type = 0
        seq_and_ack = num_seq + ack_type
        ack_length = 4
        packet = struct.pack('!hh', ack_length, seq_and_ack)
        return packet

       
def format_moviesList(listMovies):
        numSeq=1
        code_type=5
        secondbyte=prepare_header(numSeq,code_type)
        packet_moviesList=[]
        packet_length=4
        for m in listMovies:
                packet_length = packet_length + 9 + len(m.movieTitle.encode('utf-8'))

        packet_moviesList = struct.pack('!hh',packet_length,secondbyte)

        for m in listMovies:
                movie_length =  9 + len(m.movieTitle.encode('utf-8'))
                length_movie = str(len(m.movieTitle))
                port=m.moviePort
                #print("*********************",port)
                ip=m.movieIpAddress
                iD=m.movieId
                ip_Packet=re.findall(r"\d+",ip)
                ip_Packeted=(int(ip_Packet[0])<<24)+(int(ip_Packet[1])<<16)+(int(ip_Packet[2])<<8)+(int(ip_Packet[3]))
                packet_moviesList = packet_moviesList + struct.pack('!Ihhb'+length_movie+'s',ip_Packeted, port, movie_length, iD, m.movieTitle.encode('utf-8'))
               # print("**********************block movie")
               # print(packet_moviesList)
        return packet_moviesList

def formatage(ip):
        iP = str.join(".",(str(ip>>24),str((ip>>16)&15),str((ip>>8)&15),str(ip&15)))
        return iP

def get_moviesList(packet):
        List=[]
        #moviesList=[]
        pLength=get_packet_lenght(packet)
        #cursor=pLength
     
        #print("***************************",pLength)
        deb=0
        mLength=0
        while deb+4<pLength: 
                mLength2 = struct.unpack("!h", packet[mLength+4+6:mLength+4+8])[0]
                
                iP=struct.unpack("!ihhb"+str(mLength2-9)+'s', packet[mLength+4:+mLength+mLength2+4]) #pas encore formate
                mLength+=mLength2
                        
                deb=deb+mLength2
                         
                iP=list(iP)
                iP[4]=iP[4].decode('utf-8')    
                iP[0]=formatage(iP[0])
                mov=(iP[4],iP[0],iP[1],iP[3])
                List.append(mov)
        return List


def format_usersList(usersList,moviesList,numSeq):
        numSeq=numSeq
        code_type=6
        secondbyte=prepare_header(numSeq,code_type)
        packet_usersList=[]
        packet_length=4
        for m in usersList:
                packet_length = packet_length + 2 + len(m[0].encode('utf-8'))

        packet_usersList = struct.pack('!hh',packet_length,secondbyte)
        for m in usersList:
                userName_length =  len(m[0].encode('utf-8'))
                length_userName = str(len(m[0]))
                packet_usersList = packet_usersList + struct.pack('!bb'+length_userName+'s',userName_length,m[3], m[0].encode('utf-8'))
               # print("**********************block movie")
               # print(packet_moviesList)
        return packet_usersList


def format_usersList_tcp(usersList,moviesList,numSeq):
        numSeq=numSeq
        code_type=6
        secondbyte=prepare_header(numSeq,code_type)
        packet_usersList=[]
        packet_length=4
        for m in usersList:
                packet_length = packet_length + 2 + len(m.userName.encode('utf-8'))

        packet_usersList = struct.pack('!hh',packet_length,secondbyte)

        for m in usersList:
                idRoom=0               
                for mv in moviesList:              
                        #print("------------------")
                        #print(m.userChatRoom)
                        #print(mv.movieTitle)
                        #print("------------------")                        
                        if m.userChatRoom==mv.movieTitle:
                                idRoom=mv.movieId                  
                        
                userName_length =  len(m.userName.encode('utf-8'))
                length_userName = str(len(m.userName))
                packet_usersList = packet_usersList + struct.pack('!bb'+length_userName+'s',userName_length,idRoom, m.userName.encode('utf-8'))
                        # print("**********************block movie")
        print(packet_usersList)
        return packet_usersList


def get_usersList(packet,moviesList):
        List=[]
        #moviesList=[]
        pLength=get_packet_lenght(packet)
        #cursor=pLength
     
        #print("***************************",pLength)
        deb=0
        mLength=0
        
        while deb+4<pLength: 
                mLength2 = struct.unpack("!b", packet[mLength+4:mLength+5])[0]
                                
                iP=struct.unpack("!bb"+str(mLength2)+'s', packet[mLength+4:mLength+mLength2+2+4]) #pas encore formate
                mLength+=mLength2+2
                        
                deb=deb+mLength2+2
                         
                iP=list(iP)
                iP[2]=iP[2].decode('utf-8')    
                #iP[0]=formatage(iP[0])
                room=ROOM_IDS.MAIN_ROOM
                
                for m in moviesList:
                        #print("--------------------------")
                        #print(m[3])
                        #print(iP[1])
                        #print("--------------------------")
                        if(m[3]==iP[1]):
                                room=m[0]
                                print("------------LA ROOM EN QUESTION---------",room)
 
                mov=(iP[2],room)
                List.append(mov)
       
        return List




def format_header(header_type,num_sequence):
        num_seq = num_sequence << 4
        seq_and_ack = num_seq + header_type
        ack_length = 4
        packet = struct.pack('!hh', ack_length, seq_and_ack)
        return packet

def format_login(userName):
        num_sequence , connection_type = 0,1
        num_seq = num_sequence << 4 
        packet_length = 4 + len(userName.encode('utf-8'))
        seq_and_connection = num_seq + connection_type
        length_username = str(len(userName))
        packet = struct.pack('!hh'+length_username+'s', packet_length, seq_and_connection, userName.encode('utf-8'))
        return packet

def get_userName_connection(packet):
        msg = struct.unpack(str(len(packet[4:]))+'s', packet[4:])[0].decode('utf-8')
        return msg 

def format_packet(numSeq,code_type,msgToSend):
        num_seq = numSeq<< 4 
        connection_type = code_type
        packet_length = 4 + len(msgToSend.encode('utf-8'))
        seq_and_connection = num_seq + connection_type
        length_username = str(len(msgToSend))
        packet = struct.pack('!hh'+length_username+'s', packet_length, seq_and_connection, msgToSend.encode('utf-8'))
        return packet

def format_chat(numSeq,code_type,userName,msgChat):
        num_seq = numSeq<< 4 
        connection_type = code_type
        packet_length = 4 + 1 + len(userName.encode('utf-8')) + len(msgChat.encode('utf-8'))
        userName_length = len(userName.encode('utf-8'))
        seq_and_connection = num_seq + connection_type
        length_msgChat = str(len(msgChat))
        length_username = str(len(userName))
        packet = struct.pack('!hhb'+length_username+'s'+length_msgChat+'s', packet_length, seq_and_connection, userName_length, userName.encode('utf-8'), msgChat.encode('utf-8'))
        return packet

def get_message(packet):
        #pLength=get_packet_lenght(packet)
        #lenght=get_userName_length(packet)
        pseudo_length=struct.unpack("!b", packet[4:5])[0]
        msg = struct.unpack(str(len(packet[5+pseudo_length:]))+'s', packet[5+pseudo_length:])[0].decode('utf-8')
        return msg 

def get_message_test(packet):
        #pLength=get_packet_lenght(packet)
        #lenght=get_userName_length(packet)
        pseudo_length=struct.unpack("!b", packet[4:5])[0]
        msg = struct.unpack(str(len(packet[5+pseudo_length:]))+'s', packet[5+pseudo_length:])[0]
        return msg 

def get_username_fromChat(packet):
        pseudo_length=struct.unpack("!b", packet[4:5])[0]
        userName = struct.unpack(str(len(packet[5:5+pseudo_length]))+'s', packet[5:5+pseudo_length])[0].decode('utf-8')
        return userName

def get_userName_length(packet):
        pseudo_length = struct.unpack('s', packet[4:5])[0].decode('utf-8')
        return pseudo_length 

#Fonctions de récupération d'éléments d'entête
def get_type(packet):
        num_seq_and_type = struct.unpack('!H', packet[2:4])[0]       
        code_type = num_seq_and_type & 15
        return code_type

def get_numSequence(packet):
        num_seq_and_type = struct.unpack('!H', packet[2:4])[0]
        numSeq = num_seq_and_type >> 4
        return numSeq

def get_packet_lenght(packet):
        packet_length = struct.unpack('!H', packet[0:2])[0]
        return packet_length


def get_users_list(packet):

        return 0


def send_Wait(packet, num_sequence):
        
        return 0


def format_select_film(nomFilm, num_sequence):
       
        code_type=3
        seq_and_connection=prepare_header(num_sequence,code_type)
        packet_length = 4 + len(nomFilm.encode('utf-8'))    
        length_nomFilm = str(len(nomFilm))
        packet = struct.pack('!hh'+length_nomFilm+'s', packet_length, seq_and_connection, nomFilm.encode('utf-8'))
        return packet

def get_nom_film(packet):
        nom = struct.unpack(str(len(packet[4:]))+'s', packet[4:])[0].decode('utf-8')
        return nom 



