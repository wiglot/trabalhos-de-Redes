# -*- coding: utf-8 -*-
from hashlib import md5
from threading import  Thread
import os,  socket

class ConnectPeer(Thread):
    def __init__(self,  port,  control):
        Thread.__init__(self)
        self.__port = port
        self.__control = control
    def run(self):
        self.__conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.__conn.bind( ("", self.__port) )
        self.__conn.listen(1)
        
        while 1:
            i, addr = self.__conn.accept()
            data = i.recv(12)
            if data.strip() == "I AM HERE":
                i.send("YOU CHANGED?")
                data = i.recv(3)
                if data.strip() == "NO":
                    
                    i.send("SAY FILE")
                    data = i.recv(256)
                    i.send(self.__control.findFile(data.strip()))
                else:
                    print "Receber dados do peer!!!"
            
class Server:
    def __init__(self):
        self.__serverPort = 0
        self.__control = 0
        self.__connection = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        
    def start(self):
        self.__serverPort = self.__control.configure().getPort()
        self.__connection.bind( ("", self.__serverPort) )
        self.__connection.listen(1)
        self.__peers = []
        while 1:
            i, addr = self.__connection.accept()
            data = i.recv(8)
            if (data.strip() == "CONNECT"):
                if len(self.__peers) < self.__control.configure().getMaxPeers():
                    print "Peer conectado..."
                    self.__peers.append("Peer")
                else:
                    print "max peers!!"
                    i.send("NO CONNECTION")
            else:
                data = data.split(':')
                if (data[0] == "FINISH"):
                    del self.__peers [int(data[1])]
            
            i.close()
        
    def setControl(self,  control):
        self.__control = control
    
class Configure:
    def __init__(self):
        self.__filesDir = ""
        self.__maxPeers = 0
        self.__port = 0
    def getMaxPeers(self):
        return self.__maxPeers
        
    def getPort(self):
        return self.__port
        
    def readConfigure(self, file):
        config = open(file)
        str = config.read()
        pos = str.find('shared')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        for i in range( (pos+1), posFinal ):
            self.__filesDir+= str[i]
        
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
        if self.__nextPeer < len(self.__peer):
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

class peer():
    def __init__(self):
        self.__ip = '0.0.0.0'
        self.__port = 0
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
        
    def configure(self):
        return configure
        
    def addPeer(self, peer):
        if peer not in self.__peers:
            self.__peers.append(peer)
        else:
            self.removePeer(peer)
            self.__peers.append(peer)
        for file in peer.getFilesShared():
            self.__files.append(file)
            file.addPeer(peer)
            print file.getName()
    
    def removePeer(self,  peer):
        for f in self.__files:
            if peer in f.getPeersList():
                f.removePeer(peer)

    def findFile(self,  name):
        for file in self.__files:
            if file.getName() == name:
                break
        if file != 0:
            peers = file.getPeersList()
            nextPeer = file.getNextPeer()
            file.setNextPeer()
            return peers[nextPeer].getIP()+':'+str(peers[nextPeer].getPort())+':'+file.getHash()
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

cont = 0
peer = peer()
file = Files()
file1 = Files()
file.setSize(250)
file1.setSize(100)
file.setName("Blah")
file1.setName("Blah1")
files = []
files.append(file)
files.append(file1)
peer.addFilesShared(files)
control = Control(configure)
control.addPeer(peer)
control.addPeer(peer)
print control.findFile('Blah')
print configure.getMaxPeers()

server = Server()
server.setControl(control)
server.start()
