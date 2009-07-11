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
        return self.__md5Hash 
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
        found = 0
        for indice in range (0,  len(self.__filesList)):
            if self.__filesList[indice].getName() == data.strip():
                found = 1
                break
            #Aqui envia arquivo...
        if found == 1:
            i.send("OK")
            f = open(self.__filesList[indice].getFullName(),  "rb")
            conteudo = f.read()
            f.close()
#            print conteudo
            i.sendall(conteudo)
#            print 'enviou'
        else:
            i.send("FILE NOT FOUND: " + str(data.strip()))
        i.close()
        del i
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
                    i.send(str(self.connectPeer()))
                if data .strip() == "ARE YOU ALIVE?":
                    i.send("YES, I AM.")
                i.close()

    def connectPeer(self):
            newPeer = ConnectedPeer(self.__initialPort + len(self.__peers) + 1,  self.__filesList)
            self.__peers.append(newPeer)
            newPeer.start()
            return self.__initialPort + len(self.__peers)


class Configure:
    def __init__(self):
        self.__filesDir = ""
        self.__maxPeers = 0
        self.__port = 0
        self.__serverIP = "0.0.0.0"
        self.__serverPort = 0
        self.__filesList = []
        
    def getMaxPeers(self):
        return self.__maxPeers
    def getFilesDir(self):
        return self.__filesDir
    def getPort(self):
        return self.__port
    def getServerIP(self):
        return self.__serverIP
    def getServerPort(self):
        return self.__serverPort
    def getFilesList(self):
        return self.__filesList
        
    def readConfigure(self, file):
        config = open(file)
        str = config.read()
        pos = str.find('shared')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        for i in range( (pos+1), posFinal ):
            self.__filesDir+= str[i]
        
        pos = str.find('maxPeers')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        tmp = ''
        for i in range( (pos+1), posFinal ):
            tmp+= str[i]
        self.__maxPeers = int(tmp)

        pos = str.find('peerPort')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        tmp = ''
        for i in range( (pos+1), posFinal ):
            tmp+= str[i]
        self.__port = int(tmp)

        pos = str.find('serverIP')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        tmp = ''
        for i in range( (pos+1), posFinal ):
            tmp+= str[i]
        self.__serverIP = tmp

        pos = str.find('serverPort')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        tmp = ''
        for i in range( (pos+1), posFinal ):
            tmp+= str[i]
        self.__serverPort = int(tmp)
        
        for i in os.listdir(self.__filesDir):
            if not os.path.isdir(os.path.join(self.__filesDir, i)):
                arquivo = Files()
                arquivo.setName(i)
                arquivo.setPath(self.__filesDir)
                arquivo.setHash(calculate(arquivo.getFullName(), block_size))
                arquivo.setSize(os.path.getsize(arquivo.getFullName()))
                self.__filesList.append(arquivo)


class FetchFile(Thread):
    def __init__(self):
        Thread.__init__(self)
    def setFileData(self,  fileName,  peerIP, peerPort,  hash):
        self.__fileName = fileName
        self.__peerIP = peerIP
        self.__peerPort = peerPort
        self.__hash = hash
    def run(self):
        print "my thread!"
        self.__fetchFile__()
        print "end of transfer: "+self.__fileName
    def __fetchFile__(self):
        
        conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        connect2 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        
        conn.connect((self.__peerIP, (self.__peerPort)))
        conn.send("CONNECT")
        data = conn.recv(64)
        newPeerPort = int(data)
        conn.close()
        del conn
        
        connect2.connect((self.__peerIP, (newPeerPort)))
        connect2.send(str(self.__fileName))
        data = connect2.recv(2)
        if data =="OK":
            f = open(self.__fileName,"wb")
            while 1:
                data = connect2.recv(1024)
                if not data:
                    break
                f.write(data)
            f.close() 
            #fileHash = "HASH"
            f = open(self.__fileName,  "rb")
            fileHash = str(calculate(self.__fileName,  0x100000))
            f.close()
            if hash != fileHash:
                print "Hash Fail!"
        else:
            print data + connect2.recv(1024)
        connect2.close()
        del connect2
    #    Recebe arquivo.
    
class Peer:
    def __init__(self,  configure):
        self.__configure = configure;
        self.__newFiles = 1
    def startPeer(self):
        self.__handler = ConnectionsHandler(configure.getPort(),  configure.getFilesList())
        self.__handler.start()
        while (1):
            #Espera entrada do usuário para receber o nome do arquivo
            filename = str(raw_input("Digite o nome de um arquivo(quit para sair): "))
            if filename == 'quit':
                del self.__handler
                exit()
#            connServer = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
#            connServer.connect((self.__configure.getServerIP(), (self.__configure.getServerPort())))
#            connServer.send("CONNECT")
#            newPort = int(connServer.recv(8))
#            connServer.close()
#            del connServer
#            
#            newConn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
#            newConn.connect((self.__configure.getServerIP(),  newPort))
#            newConn.send("I AM HERE")
#            data = newConn.recv(16)
#            if data.strip() == "YOU CHANGED?":
#                if self.__newFiles:
#                    newConn.send("YES")
##                    Aqui envia as informações do peer
#                    self.__newFiles = 0
#                else:
#                    newConn.send("NO")
#                data = newConn.recv(12)
#                if data.strip() == "SAY FILE":
#                    newConn.send(filename)
#                    data = newConn.recv(1024)
#                newConn.close()
#                del newConn
                
#                Possivel retorno do servidor...
            data = '127.0.0.1:3333:HASH FAIL'
            data = data.rsplit(':')
            peerIP = data[0]
            peerPort = int(data[1])
            hash = data[2]
                
            #Procura no servidor (tracker) por um peer que contenha o arquivo.
            #pede o arquivo para o peer.
            fetch = FetchFile()
            fetch.setFileData(filename,  peerIP,  peerPort,  "THIS HASH")
            fetch.start()
    
    

block_size = 0x100000
configure = Configure()
configure.readConfigure("peer.conf")

peer = Peer(configure)
peer.startPeer()

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
