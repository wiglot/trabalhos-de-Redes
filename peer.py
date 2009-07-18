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
    def __init__(self,  port,  configure,  posicao):
            Thread.__init__(self)
            self.__port = int(port)
            self.__filesList = configure.getFilesList()
            self.__filesDir = configure.getFilesDir()
            self.__configure = configure
            self.__posicao = posicao
            
            self.listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            while 1:
                try:
                    self.listening_socket.bind( ("", self.__port) )
                    self.listening_socket.listen(1)
                    break
                except:
                    self.__port += 1

    def run(self):
#        print 'Teste...',  self.__port
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
        self.listening_socket.close()
        
        finish = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        finish.connect(('127.0.0.1', self.__configure.getPort()))
        finish.send('FINISH:'+str(self.__posicao))
        
        
    def getPort(self):
        return self.__port
        
class ConnectionsHandler(Thread):
    def __init__(self,  configure):
            Thread.__init__(self)
            self.__peers = []
            for i in range(0, configure.getMaxPeers()):
                self.__peers.append(0)
            self.__port = configure.getPort()
            self.__initialPort = 12000
            self.__filesList = configure.getFilesList()
            self.__configure = configure
            self.listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.listening_socket.bind( ("", self.__port) )
            self.listening_socket.listen(1)

    def run(self):
            print 'Iniciado serviço de compartilhamento...'
            while (1):
                i, addr = self.listening_socket.accept()
                data = i.recv(64)
                if data.strip() in ["CONNECT"]:
#                    if len(self.__peers) < configure.getMaxPeers():
                    k = -1
                    try:
                        k = self.__peers.index(0)
                    except:
                        i.send("NO CONNECTION")    
                    if (k >= 0):
                        i.send(str(self.connectPeer(k)))
                    
                elif data.strip() == "ARE YOU ALIVE?":
                    i.send("YES, I AM.")
                else:
                    data = data.split(':')
                    if (data[0] == "FINISH"):
                        self.__peers [int(data[1])] = 0
                i.close()

    def connectPeer(self,  position):
            newPeer = ConnectedPeer(self.__initialPort,  self.__configure,  position)
            self.__peers[position] = newPeer
            newPeer.start()
            return newPeer.getPort()

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
        
    def refreshFileList(self):
        del self.__filesList [:]
            
        for i in os.listdir(self.__filesDir):
            if not os.path.isdir(os.path.join(self.__filesDir, i)):
                arquivo = Files()
                arquivo.setName(i)
                arquivo.setPath(self.__filesDir)
                arquivo.setHash(calculate(arquivo.getFullName(), block_size))
                arquivo.setSize(os.path.getsize(arquivo.getFullName()))
                self.__filesList.append(arquivo)
        
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
        
        self.refreshFileList()


class FetchFile(Thread):
    def __init__(self):
        Thread.__init__(self)
    def setFileData(self,  fileName,  peerIP, peerPort,  expectedHash):
        self.__fileName = fileName
        self.__peerIP = peerIP
        self.__peerPort = peerPort
        self.__hash = expectedHash
    def run(self):
#        print "my thread!"
        self.__fetchFile__()
        print "end of transfer: "+self.__fileName
    def __fetchFile__(self):
        conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        try:
            conn.connect((self.__peerIP, (self.__peerPort)))
        except:
            print 'Peer não respondeu,  ele está ligado?'
            return
            
        conn.send("CONNECT")
        data = conn.recv(64)
        if data.strip() == 'NO CONNECTION':
            print 'Peer atingiu limite de conexões. Tente novamente'
#            Pode enviar uma mensagem por socket pro peer pra ele avisar que o peer destino não respondeu...
            return
            
        newPeerPort = int(data)
        conn.close()
        del conn
        
        connect2 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
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
            if self.__hash != fileHash:
                print self.__hash
                print fileHash
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
    def refreshFiles(self):
        self.__newFiles = 1
        self.__configure.refreshFileList()
        
    def startPeer(self):
        self.__handler = ConnectionsHandler(configure)
        self.__handler.start()
        
        while (1):
            #Espera entrada do usuário para receber o nome do arquivo
            filename = str(raw_input("Digite o nome de um arquivo('quit' para sair. 'rehash' novos arquivos): "))
            if filename.upper() == 'QUIT':
                del self.__handler
                try:
                    connServer = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                    connServer.connect((self.__configure.getServerIP(), (self.__configure.getServerPort())))
                    connServer.send("I QUIT")
                    data = connServer.recv(8)
                    if data.strip() == "PORT":
                        connServer.send(str(self.__configure.getPort()))
                except:
                    exit()
                exit()   
            if filename.upper() == 'REHASH':
                self.refreshFiles()
                
            elif filename == '':
                pass
            else:
                try:
                    connServer = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                    newPort = self.__configure.getServerPort()
                    connServer.connect((self.__configure.getServerIP(), (newPort)))
                    if filename.upper() == 'LIST':
    #                    connList = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    #                    connList.connect((self.__configure.getServerIP(), (self.__configure.getServerPort())))
                        connServer.send("LIST")
                        data = ''
                        while 1:
                            newData = connServer.recv(1024)
                            if not newData:
                                break
                            data += newData
                        data = data.split(':')
                        count = 0
                        for i in range(0,  len(data),  4):
                                if len(data)-1 >=3:
                                    print data[i], ' - ' , data[i+1], ' - ',  data[i+2],  ' - ',  data[i+3]
                                    count += 1
                        print count,  ' Files shared.'
                        connServer.close()
                    else:
    #                    connServer = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    #                    connServer.connect((self.__configure.getServerIP(), (self.__configure.getServerPort())))
                        
                        connServer.send("CONNECT")
                        newPort = int(connServer.recv(8))
#                        print newPort
                        connServer.close()
                        
                        newConn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                        newConn.connect((self.__configure.getServerIP(),  newPort))
                        newConn.send("I AM HERE")
                        data = newConn.recv(16)
                        if data.strip() == "YOU CHANGED?":
                            if self.__newFiles:
                                newConn.send("YES")
        #                    Aqui envia as informações do peer
                                data = newConn.recv(16)
                                if data.strip() == 'TELL ME':
                                    self.sendInfo(newConn)
                                    data = newConn.recv(8)
                                    if (data.strip() == 'OK'):
                                        self.__newFiles = 0
                            else:
                                newConn.send("NO")
                            data = newConn.recv(12)
                            if data.strip() == "SAY FILE":
                                newConn.send(filename)
                                data = newConn.recv(1024)
                            newConn.close()
                            del newConn
                        
        #                Possivel retorno do servidor...
                            data = data.rsplit(':')
                            if len(data)==1:
        #                Aquivo não encontrado...
                                print "File not found"
                            else:
                                peerIP = data[0]
                                peerPort = int(data[1])
                                hash = data[2]
                            #pede o arquivo para o peer.
                                fetch = FetchFile()
                                fetch.setFileData(filename,  peerIP,  peerPort,  hash)
                                fetch.start()
                except:
                    print "Can't connect to tracker ",  self.__configure.getServerIP(), ':', newPort
                    print "Change tracker config at 'peer.conf' and try again."
                    pass
                            
    def sendInfo(self,  connection):
        info = str(configure.getPort()) 
        for i in configure.getFilesList():
            info +=':'+ i.getName()
            info +=':'+ str(i.getSize() )
            info +=':'+ i.getHash()
        connection.send(info)
        
        
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

