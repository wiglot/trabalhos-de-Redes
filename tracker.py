# -*- coding: utf-8 -*-
from hashlib import md5
from threading import  Thread
import os,  socket

class ConnectPeer(Thread):
    def __init__(self,  port,  control,  position):
        Thread.__init__(self)
        self.__port = port
        self.__control = control
        self.__position = position
        self.__conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
#        self.__conn.settimeout(15)
        self.__conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        while 1:
                try:
                    self.__conn.bind( ("", self.__port) )
                    self.__conn.listen(1)
                    break
                except:
                    self.__port += 1
                    
    def port(self):
        return self.__port
    def run(self):
        try:

            i, addr = self.__conn.accept()
            data = i.recv(12)
            if data.strip() == "I AM HERE":
                i.send("YOU CHANGED?")
                data = i.recv(6)
                if data.strip() == "YES":
                    i.send("TELL ME")
                    data = i.recv(8192)
                    self.__control.addPeerAndFiles(addr,  data.strip())
                    i.send('OK')
                    
                i.send("SAY FILE")
                data = i.recv(256)
                i.send(self.__control.findFile(data.strip()))
                    
            i.close()
            del i
        except:
            pass
        
        conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        conn.connect(('127.0.0.1', (self.__control.configure().getPort())))
        conn.send('FINISH:'+str(self.__position))
        conn.close()
        conn.close()
        self.__conn.close()
        
class Server(Thread):
    def __init__(self):
    	Thread.__init__(self)
        self.__serverPort = 0
        self.__control = 0
        self.__connection = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        
    def run(self):
        configure = self.__control.configure()
        self.__serverPort = configure.getPort()
        self.__connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__connection.bind( ("", self.__serverPort) )
#        self.__connection.settimeout(15)
        self.__connection.listen(1)
        self.__peers = []
        for i in range(0,  configure.getMaxPeers()):
            self.__peers.append(0)
            
        while 1:
            try:
                i, addr = self.__connection.accept()
                data = i.recv(8)
                
                if (data.strip() == "CONNECT"):
                    k = -1
                    try:
                        k = self.__peers.index(0)
                    except:
                        pass  
                    if (k >= 0):
                        print "Peer conectado...",  k
                        peer = ConnectPeer(configure.getInitialPort(),  self.__control,  k)
                        self.__peers[k] = peer
                        peer.start()
                        i.send(str(peer.port()))
#                        print str(peer.port())
                        i.close()
                        
                    else:
                        print "max peers at tracker...!!"
                        i.send("NO CONNECTION")
                elif data.strip() == 'LIST':
                    i.send(self.__control.listOfFiles())
                elif data.strip() == 'I QUIT':
                    i.send("PORT")
                    data = int(i.recv(8).strip())
                    self.__control.removePeerAddress(addr[0],  data)
                    
                else:
                    data = data.split(':')
                    if (data[0] == "FINISH"):
                        self.__peers [int(data[1])] = 0
#                        del self.__peers [int(data[1])]
                        print 'peer desconectado',  int(data[1])
                
                i.close()
            except:
                pass
                
    def setControl(self,  control):
        self.__control = control
    
class Configure:
    def __init__(self):
        self.__filesDir = ""
        self.__maxPeers = 0
        self.__port = 0
        self.__initialPort = 0
    def getMaxPeers(self):
        return self.__maxPeers
        
    def getPort(self):
        return self.__port
    def getInitialPort(self):
        return self.__initialPort
        
    def readConfigure(self, file):
        config = open(file)
        str = config.read()
        
        pos = str.find('maxPeer')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        tmp = ""
        for i in range( (pos+1), posFinal ):
            tmp+= str[i]
        self.__maxPeers = int(tmp)
        
        pos = str.find('port')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        port = ''
        for i in range( (pos+1), posFinal ):
            port+= str[i]
        self.__port = int(port)
        
        pos = str.find('initialPort')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        port = ''
        for i in range( (pos+1), posFinal ):
            port+= str[i]
        self.__initialPort = int(port)


class Files():
    def __init__(self):
        self.__name = ''
        self.__md5Hash = ''
        self.__size = 0
        self.__peer = []
        self.__nextPeer = 0
    def printData(self):
        print self.__name, self.__md5Hash, self.__size

    def setName(self, name):
        self.__name = name
    def setHash(self, md5Hash):
        self.__md5Hash = md5Hash
    def setSize(self, size):
        self.__size = size
    def setNextPeer(self):
        if (self.__nextPeer+1) < len(self.__peer):
            self.__nextPeer += 1
        else:
            self.__nextPeer = 0

    def addPeer(self,  peer):
        self.__peer.append(peer)

    def removePeer(self,  peer):
        if peer in self.__peer:
            self.__peer.remove(peer)
        
    def getName(self):
        return self.__name 
    def getHash(self):
        return self.__md5Hash 
    def getSize(self):
        return self.__size
    def getPeersList(self):
        return self.__peer
    def getNextPeer(self):
        return self.__nextPeer
    def getNumPeers(self):
        return len(self.__peer)

class Peer():
    def __init__(self):
        self.__ip = '127.0.0.1'
        self.__port = 3333
        self.__filesShared = []
    def setIP(self, ip):
        self.__ip = ip
    def setPort(self, port):
        self.__port = port
    def addFilesShared(self,  files):
        self.__filesShared.extend(files)
    def getFilesShared(self):
        return self.__filesShared
    def getIP(self):
        return self.__ip
    def getPort(self):
        return self.__port

class Control():
    def __init__(self,  configure):
        self.__peers = []
        self.__files = []
        self.__configure = configure
        
    def getPeers(self):
    	return self.__peers
    def getFiles(self):
    	return self.__files
    def configure(self):
        return configure
        
    def listOfFiles(self):
        data = ''
        for i in self.__files:
            data += ':' + str(i.getNumPeers())
            data += ':' + i.getName()
            data += ':' + str(i.getSize())
            data += ':' + i.getHash()
        return data.lstrip(':')
        
    def addPeerAndFiles(self, address,  data):
        print 'Receiving new data from peer...'
        data = data.split(':')
        
        addr = address[0]
        port = int(data[0])
        
        print addr + ":"+ str(port)
        del data[0]
#        print len(data)
        fileList = []
        size = 0
        name = ''
        for i in range(0,  len(data)):
            if i % 3 == 0:
                name = data[i]
#                print name
            elif i%3 == 1:
                size = int (data[i])
#                print size
            else:
                file = Files()
                file.setSize(size)
                file.setName(name)
                file.setHash(str(data[i]))
                fileList.append(file)
                name = ''
                size = 0
#                print file.getName()
        peer = Peer()
        peer.setIP(addr)
        peer.setPort(port)
        
        peer.addFilesShared(fileList)
#        print 'Num arquivos compartilhados ',  peer.getFilesShared()
        self.addPeer(peer)
        
    def addPeer(self, peer):
        noFile = 1
        for i in self.__peers:
            if peer.getPort() ==  i.getPort() and peer.getIP() == i.getIP():
                    print 'peer existente, removendo'
                    self.removePeer(i)
#                    break
        print 'adicionando novo peer'
        self.__peers.append(peer)
        
        for newFile in peer.getFilesShared():
            noFile = 1
#            print 'testando novo arquivo', newFile.getName()
            for file in self.__files:
                if newFile.getName() == file.getName():
#                    print 'encontrou um aquivo'
                    file.addPeer(peer)
                    noFile = 0
                    #break
            if noFile:
                self.__files.append(newFile)
                newFile.addPeer(peer)
#            print newFile.getName()
    
    def removePeerAddress(self,  ip,  port):
        for i in self.__peers:
            if i.getIP() == ip and i.getPort() == port:
                self.removePeer(i)
    
    def removePeer(self,  peer):
        self.__peers.remove(peer)
        
        for f in self.__files:
            f.removePeer(peer)
            
#        for f in range(0,  len(self.__files)):
#            if f < len(self.__files):
#                if not  self.__files[f].getPeersList():
#                    del self.__files[f]
#                    f = 0

    def findFile(self,  name):
        found = 0
        file = 0
        for file in range (0,  len(self.__files)):
            if self.__files[file].getName() == name:
                found = 1
                break
        if found == 1:
            peers = self.__files[file].getPeersList()
            nextPeer = self.__files[file].getNextPeer()
            self.__files[file].setNextPeer()
            return peers[nextPeer].getIP()+':'+str(peers[nextPeer].getPort())+':'+self.__files[file].getHash()
        else:
            print 'Arquivo não encontrado'
            return "FILE NOT FOUND"
            

def upd(m, data):
       m.update(data)
       return m

def calculate(fname, block_size):
       fd = open(fname, "rb")
       contents = iter(lambda: fd.read(block_size), "")
       m = reduce(upd, contents, md5())
       fd.close()
       return m.hexdigest()


block_size = 0x100000
configure = Configure()

configure.readConfigure("tracker.conf")

#cont = 0
#peer = peer()
#file = Files()
#file1 = Files()
#file.setSize(250)
#file1.setSize(100)
#file.setName("teste.txt")
#file1.setName("Blah1")
#files = []
#files.append(file)
#files.append(file1)
#peer.addFilesShared(files)
control = Control(configure)
#control.addPeer(peer)
#control.addPeer(peer)
#print control.findFile('Blah')
#print configure.getMaxPeers()

server = Server()
server.setControl(control)
server.start()

while 1:
	read= str(raw_input("$>"))
	if read.upper() in ["EXIT","QUIT","SAIR"]:
		exit()
	elif read.upper() in ["PEER", "PEERS"]:
		for i in control.getPeers():
			print i.getIP(), " - ",i.getPort()
	elif read.upper() in ["FILE", "FILES"]:
		for i in control.getFiles():
			print str(i.getNumPeers()), " - ", i.getName(), " - ", str(i.getSize()), " - ", i.getHash()
