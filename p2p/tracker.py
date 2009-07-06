# -*- coding: utf-8 -*-
from hashlib import md5
import os


class server:
    def __init__(self):
        __clientPort = 0
        __serverPort = 0
        __peer = 0

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
        
        pos = str.find('maxPeersPerFile')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        maxPeer = ''
        for i in range( (pos+1), posFinal ):
            maxPeer+= str[i]
        self.__maxPeersPerFile = int(maxPeer)
        
        return self.__filesDir


class Files():
    def __init__(self):
        self.__name = ''
        self.__path = ''
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
        return os.path.join(filesDir, i)
    def getHash(self):
        return self.__md5hash 
    def getSize(self):
        return self.__size
    def getPeersList(self):
        return self.__peer

class peer():
    def __init__(self):
        __ip = '0.0.0.0'
        __filesShared = []
    def setIP(self, ip):
        self.__ip = ip
    def addFilesShared(self,  files):
        self.__filesShared.extend(files)
    def getFilesShared(self):
        return self.__filesShared
    def getIP(self):
        return self.__ip



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

filesList = []
filesDir = configure.readConfigure("tracker.conf")

cont = 0
for i in os.listdir(filesDir):
    if not os.path.isdir(os.path.join(filesDir, i)):
        arquivo = Files()
        arquivo.setName(i)
        arquivo.setPath(filesDir)
        arquivo.setHash(str(calculate(arquivo.getFullName(), block_size)))
        arquivo.setSize(100)
        filesList.append(arquivo)

print configure.getMaxPeersPerFile()
