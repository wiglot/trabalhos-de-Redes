#!/usr/bin python
# -*- coding: utf-8 -*-

import socket, os                
from threading import Thread
from hashlib import md5

def upd(m, data):
       m.update(data)
       return m

def calculate(fname, block_size):
       fd = open(fname, "rb")
       contents = iter(lambda: fd.read(block_size), "")
       m = reduce(upd, contents, md5())
       fd.close()
       return m.hexdigest()



class Files():
    def __init__(self):
        self.__name = ''
        self.__path = ""
        self.__md5Hash = ''
        self.__size = 0
        self.__peer = []
    def printData(self):
        print self.__name, self.__path, self.__md5Hash, self.__size

    def setName(self, name):
        self.__name = name
    def setPath(self, path):
        self.__path = path 
    def setHash(self, md5Hash):
        self.__md5Hash = md5Hash
    def setSize(self, size):
        self.__size = size
    
    def addPeer(self,  peer):
        self.__peer.append(peer)

    def removePeer(self,  peer):
        if peer in self.__peer:
            self.__peer.remove(peer)
        
    def getName(self):
        return self.__name 
    def getPath(self):
        return self.__path
    def getFullName(self):
        if not self.__path:
            return self.__name
        else:
            return os.path.join(self.__path, self.__name)
    def getHash(self):
        return self.__md5hash 
    def getSize(self):
        return self.__size
    def getPeersList(self):
        return self.__peer

class ConnectedPeer(Thread):
    def __init__(self,  port,  filesList = [],  filesDir = ""):
            Thread.__init__(self)
            self.__port = int(port)
            self.__filesList = filesList
            self.__filesDir = filesDir
            
            self.listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.listening_socket.bind( ("", self.__port) )
            self.listening_socket.listen(1)
            
    def run(self):
        print 'Teste...',  self.__port
        i, addr = self.listening_socket.accept()
        data = i.recv(2048)
        indice = 0
        for indice in range (0,  len(self.__filesList)):
            print indice,  self.__filesList[indice].getName()
            if self.__filesList[indice].getName() == data.strip():
#                indice =  self.__filesList.index(fl)
               
                print indice,  self.__filesList[indice].getName()
                break
            #testa o Hash... Mas pra isso tem que receber o Hash do cliente....
            #Aqui envia arquivo...
        if indice < len(self.__filesList):
            i.send("OK")
            f = open(self.__filesList[indice].getFullName(),  "rb")
            conteudo = f.read()
            i.sendall(conteudo)
            f.close()
        else:
            i.send("NOT FOUND FILE: " + str(data.strip()))
        i.close()
        #Aqui precisa Fechar a porta
        
class ConnectionsHandler(Thread):
    def __init__(self,  port,  filesList):
            Thread.__init__(self)
            self.__peers = []
            self.__port = int (port)
            self.__initialPort = 10000
            self.__filesList = filesList
            self.listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.listening_socket.bind( ("", self.__port) )
            self.listening_socket.listen(1)
            
    def run(self):
            print 'my run...'
            while (1):
                i, addr = self.listening_socket.accept()
                data = i.recv(64)
                if data.strip() in ["CONNECT"]:
                    i.send(str(handler.connectPeer()))
                    i.close()

    def connectPeer(self):
            newPeer = ConnectedPeer(self.__initialPort + len(self.__peers) + 1,  self.__filesList)
            self.__peers.append(newPeer)
            newPeer.start()
            return self.__initialPort + len(self.__peers)


class Configure:
    def __init__(self):
        self.__filesDir = ""
        self.__maxPeersPerFile = 0
        
    def getMaxPeersPerFile(self):
        return self.__maxPeersPerFile


    def readConfigure(self, file):
        config = open(file)
        str = config.read()
        pos = str.find('shared')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        for i in range( (pos+1), posFinal ):
            self.__filesDir+= str[i]
        
#    pos = str.find('maxPeersPerFile')
#    pos =  str.find(' ', pos)
#    posFinal = str.find(';', pos)
#    maxPeer = ''
#    for i in range( (pos+1), posFinal ):
#        maxPeer+= str[i]
#    self.__maxPeersPerFile = int(maxPeer)
    
        return self.__filesDir

def fetchFile(fileName,  peerIp,  peerPort):
    
    conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    connect2 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    
    print 'conecta 1ª vez no peer...'
    conn.connect((peerIp, (peerPort)))
#    self.connect_socket.setblocking(0)
    conn.send("CONNECT")
    data = conn.recv(64)
    peerPort = int(data)
    conn.close()
    print 'conecta na segunda 2ª porta...',  peerPort
    
    connect2.connect((peerIp, (peerPort)))
    print fileName
    connect2.send(str(fileName))
    data = connect2.recv(2)
    if data in ["OK"]:
        print data
        f = open(fileName,"wb")
        while 1:
            data = connect2.recv(1024)
            if not data: break
            f.write(data)
        f.close()    
    else:
        print data + connect2.recv(1024)
    
#    Recebe arquivo.
    
    
block_size = 0x100000
configure = Configure()

filesDir = configure.readConfigure("peer.conf")
filesList = []

for i in os.listdir(filesDir):
    if not os.path.isdir(os.path.join(filesDir, i)):
        arquivo = Files()
        arquivo.setName(i)
        arquivo.setPath(filesDir)
        arquivo.setHash(str(calculate(arquivo.getFullName(), block_size)))
        arquivo.setSize(100)
        filesList.append(arquivo)

handler = ConnectionsHandler(3334,  filesList)
handler.start()

# FUnção para receber os arquivos.
#   def transfer( this ):
#        print '[Media] Starting media transfer for "%s"' % this.filename
#
#        f = open(this.filename,"wb")
#        while 1:
#            data = this.mconn.recv(1024)
#            if not data: break
#            f.write(data)
#        f.close()

