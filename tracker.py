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
    def port(self):
        return self.__port
    def run(self):

        self.__conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.__conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__conn.bind( ("", self.__port) )
        self.__conn.listen(1)
    
        i, addr = self.__conn.accept()
        try:
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
        
class Server:
    def __init__(self):
        self.__serverPort = 0
        self.__control = 0
        self.__connection = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        
    def start(self):
        configure = self.__control.configure()
        self.__serverPort = configure.getPort()
        self.__connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__connection.bind( ("", self.__serverPort) )
        self.__connection.listen(1)
        self.__peers = []
        while 1:
            i, addr = self.__connection.accept()
            data = i.recv(8)
            if (data.strip() == "CONNECT"):
                if len(self.__peers) < configure.getMaxPeers():
                    print "Peer conectado...",  len(self.__peers)
                    peer = ConnectPeer(configure.getInitialPort()+len(self.__peers) + 1,  self.__control,  len(self.__peers))
                    self.__peers.append(peer)
                    i.send(str(peer.port()))
                    peer.run()
                else:
                    print "max peers!!"
                    i.send("NO CONNECTION")
            elif data.strip() == 'LIST':
                i.send(self.__control.listOfFiles())
            else:
                data = data.split(':')
                if (data[0] == "FINISH"):
                    self.__peers [int(data[1])]
                    del self.__peers [int(data[1])]
                    print 'peer desconectado',  int(data[1])
            
            i.close()
        
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
        print len(data)
        fileList = []
        size = 0
        name = ''
        for i in range(0,  len(data)):
            if i % 3 == 0:
                name = data[i]
                print name
            elif i%3 == 1:
                size = int (data[i])
                print size
            else:
                file = Files()
                file.setSize(size)
                file.setName(name)
                file.setHash(str(data[i]))
                fileList.append(file)
                name = ''
                size = 0
                print file.getName()
        peer = Peer()
        peer.setIP(addr)
        peer.setPort(port)
        print 'Num arquivos compartilhados ',  len(fileList)
        peer.addFilesShared(fileList)
        self.addPeer(peer)
        print peer.getFilesShared()
        
    def addPeer(self, peer):
        noFile = 1
        for i in self.__peers:
            if peer.getPort() ==  i.getPort() and peer.getIP() == i.getIP():
                    self.removePeer(i)
                    break
        self.__peers.append(peer)
        for newFile in peer.getFilesShared():
#            print newFile.getNome()
            for file in self.__files:
                if newFile.getNome() == file.getNome:
                    noFile = 0
                    #break
            if noFile == 1:
                self.__files.append(newFile)
            newFile.addPeer(peer)
            print newFile.getName()
    
    def removePeer(self,  peer):
        for f in self.__files:
            if peer in f.getPeersList():
                f.removePeer(peer)
        

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
