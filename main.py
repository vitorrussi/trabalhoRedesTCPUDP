import sys
import os
import os.path
from PyQt4 import QtGui
from PyQt4.uic import loadUiType
from PyQt4.QtCore import *
from PyQt4.QtGui import *
Ui_MainWindow, QMainWindow = loadUiType('main.ui')
Ui_MainWindowHELP, QMainWindowHELP = loadUiType('help.ui')
Ui_MainWindowERROR, QMainWindowERROR = loadUiType('error.ui')

import socket
from threading import Thread
import binascii
import hashlib

textoerror = " "

class Help(QMainWindowHELP, Ui_MainWindowHELP):
    def __init__(self,):
        super(Help, self).__init__()
        self.setupUi(self)

class Error(QMainWindowERROR, Ui_MainWindowERROR):
    def __init__(self,):
        super(Error, self).__init__()
        self.setupUi(self)
    def setErro(self,textoerro):
        for i in textoerro:
            k = str(i)
            for j in k:
                self.Lerro.setText(self.Lerro.text() + j)
            self.Lerro.setText(self.Lerro.text() + '\n')

class Main(QMainWindow, Ui_MainWindow) :
    def __init__(self, ) :
        super(Main, self).__init__()
        self.setupUi(self)

        self.thisDir = os.path.dirname(os.path.abspath(__file__))
        self.PBenviar.clicked.connect(self.enviaMsg)
        self.PBenviarimg.clicked.connect(self.enviaImg)
        self.PBconectar.clicked.connect(self.conectar)
        self.PBfechar.clicked.connect(self.fechaconexao)
        self.PBfecharimg.clicked.connect(self.fechaconexao)
        self.PBouvir.clicked.connect(self.ouvir)
        self.PBouvirimg.clicked.connect(self.ouvirImg)
        self.PBescolherimg.clicked.connect(self.openImage)
        self.PBhelp.clicked.connect(self.help)
        self.Lmsgrecebida = QLabel()
        self.Lmsgrecebida.setAlignment(Qt.AlignTop)
        self.scrollArea.setWidget(self.Lmsgrecebida)
        self.onlyInt = QIntValidator()
        self.LEtimeout.setValidator(self.onlyInt)
        self.PBlimpar.clicked.connect(self.limpar)

        HOST = ''              # Endereco IP do Servidor
        PORT = 5000            # Porta que o Servidor esta
        self.dest = (HOST, PORT)
        self.orig = (HOST, PORT)
        self.origr = (HOST, PORT)
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.servicoOuvir = True #False para UDP e True para TCP
        self.servicoEnviar = True #False para UDP e True para TCP
        self.msg = ''
        self.ouvindo = 0
        self.conectado = False
        self.fecha = False

    def limpar(self):
        self.Lmsgrecebida.setText("")

    def help(self):
        self.w = Help()
        self.w.show()

    def openImage(self) :
        texto = 'Escolha um arquivo'
        path = QtGui.QFileDialog.getOpenFileNameAndFilter(self,
                                                          texto,
                                                          self.thisDir,
                                                          "All (*)")
        print (str(path[0]))
        self.LEimgenviar.setText(str(path[0]))
        return

    def recebeMsg(self, label):
        print 'ouvindo porta Orig = ', self.origr
        orig = self.origr
        self.servicoOuvir = self.Rtcp_2.isChecked()
        if self.servicoOuvir:
            tcp2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            tcp2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tcp2.settimeout(int(self.LEtimeout.text()))
        tcp2.bind(orig)
        self.ouvindo = 1
        if self.servicoOuvir:
            tcp2.listen(1)
            try:
                con, cliente = tcp2.accept()
            except:
                self.ouvindo = 0
                print 'timeout lala'
                return
            print cliente
            self.Lcliente.setText(str(cliente))
        self.fecha = False

        while self.servicoOuvir:
            self.msg = con.recv(1024)
            if not self.msg: break
            print self.msg
            msg2 = ""
            if(self.Rcrc.isChecked()):
                self.msg = str(self.msg).split(":\x00\x00\x00/\x00\x00\x00:\x00\x00\x00:\x00\x00\x00/\x00\x00\x00:\x00\x00\x00")
                print self.msg
                crcenviado = self.msg[1]
                msg2 = self.msg[0]
                crcrecebido = str((binascii.crc32(str(msg2)) & 0xFFFFFFFF))
            else:
                self.msg = str(self.msg).split(":\x00\x00\x00/\x00\x00\x00:\x00\x00\x00:\x00\x00\x00/\x00\x00\x00:\x00\x00\x00")
                print self.msg
                crcenviado = self.msg[1]
                msg2 = self.msg[0]
                crcrecebido = str(hashlib.md5(str(msg2)).hexdigest())
            for i in msg2:
                self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + i)
            if(self.Rcrc.isChecked()):
                for i in ("---CRC recebido = " + crcenviado + " CRC calculado = " + crcrecebido):
                    self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + i)
            else:
                for i in ("---Checksum recebido = " + crcenviado + " Checksum calculado = " + crcrecebido):
                    self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + i)
            self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + '\n')
        try:
            while not self.servicoOuvir:
                self.msg, addr = tcp2.recvfrom(1024) # buffer size is 1024 bytes
                print "received message:", self.msg
                msg2 = ""
                if(self.Rcrc.isChecked()):
                    self.msg = str(self.msg).split(":\x00\x00\x00/\x00\x00\x00:\x00\x00\x00:\x00\x00\x00/\x00\x00\x00:\x00\x00\x00")
                    crcenviado = self.msg[1]
                    msg2 = self.msg[0]
                    crcrecebido = str((binascii.crc32(str(msg2)) & 0xFFFFFFFF))
                else:
                    self.msg = str(self.msg).split(":\x00\x00\x00/\x00\x00\x00:\x00\x00\x00:\x00\x00\x00/\x00\x00\x00:\x00\x00\x00")
                    crcenviado = self.msg[1]
                    msg2 = self.msg[0]
                    crcrecebido = str(hashlib.md5(str(msg2)).hexdigest())
                for i in msg2:
                    self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + i)
                if(self.Rcrc.isChecked()):
                    for i in ("---CRC recebido = " + crcenviado + " CRC calculado = " + crcrecebido):
                        self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + i)
                else:
                    for i in ("---Checksum recebido = " + crcenviado + " Checksum calculado = " + crcrecebido):
                        self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + i)
                self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + '\n')
        except:
            print 'acabo o tempo mas nao entrou no except'
            self.ouvindo = 0
        print 'Finalizando conexao do cliente'
        self.ouvindo = 0
        tcp2.close()
        if self.servicoOuvir: con.close()

    def recebeImg(self, label):
        print ' IMG ouvindo porta Orig = ', self.origr
        orig = self.origr

        self.servicoOuvir = self.Rtcp_2.isChecked()

        if self.servicoOuvir:
            tcp2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            tcp2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tcp2.settimeout(int(self.LEtimeout.text()))
        tcp2.bind(orig)
        self.ouvindo = 1
        if self.servicoOuvir:
            tcp2.listen(1)
            try:
                con, cliente = tcp2.accept()
            except:
                self.ouvindo = 0
                print 'IMG timeout lala'
                return
            print cliente
            self.Lcliente.setText(str(cliente))
        self.fecha = False

        while self.servicoOuvir:
            self.msg = con.recv(1024*1024*4)
            if not self.msg: break
            myfile = open(str(self.LEarq.text()), 'wb')
            msg2 = ""
            if(self.Rcrc.isChecked()):
                self.msg = str(self.msg).split(":/::/:")
                crcenviado = self.msg[1]
                msg2 = self.msg[0]
                crcrecebido = str((binascii.crc32(str(msg2)) & 0xFFFFFFFF))
            else:
                self.msg = str(self.msg).split(":/::/:")
                crcenviado = self.msg[1]
                msg2 = self.msg[0]
                crcrecebido = str(hashlib.md5(str(msg2)).hexdigest())
            if(self.Rcrc.isChecked()):
                for i in ("Arquivo enviado---CRC recebido = " + crcenviado + " CRC calculado = " + crcrecebido):
                    self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + i)
            else:
                for i in ("Arquivo enviado---Checksum recebido = " + crcenviado + " Checksum calculado = " + crcrecebido):
                    self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + i)
            self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + '\n')


            myfile.write(msg2)
            myfile.close()
        try:
            while not self.servicoOuvir:
                self.msg, addr = tcp2.recvfrom(1024*1024*4) # buffer size is 1024 bytes
    #                print "img received message:", self.msg
                myfile = open(str(self.LEarq.text()), 'wb')

                msg2 = ""
                if(self.Rcrc.isChecked()):
                    self.msg = str(self.msg).split(":/::/:")
                    crcenviado = self.msg[1]
                    msg2 = self.msg[0]
                    crcrecebido = str((binascii.crc32(str(msg2)) & 0xFFFFFFFF))
                else:
                    self.msg = str(self.msg).split(":/::/:")
                    crcenviado = self.msg[1]
                    msg2 = self.msg[0]
                    crcrecebido = str(hashlib.md5(str(msg2)).hexdigest())
                if(self.Rcrc.isChecked()):
                    for i in ("Arquivo enviado---CRC recebido = " + crcenviado + " CRC calculado = " + crcrecebido):
                        self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + i)
                else:
                    for i in ("Arquivo enviado---Checksum recebido = " + crcenviado + " Checksum calculado = " + crcrecebido):
                        self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + i)
                self.Lmsgrecebida.setText(self.Lmsgrecebida.text() + '\n')
                myfile.write(msg2)
                myfile.close()
        except:
            print 'IMG acabo o tempo mas nao entrou no except'
            self.ouvindo = 0
        print 'IMG Finalizando conexao do cliente'
        self.ouvindo = 0
        tcp2.close()
        if self.servicoOuvir: con.close()




    def enviaMsg(self):
        if self.Rtcp.isChecked():
            try:
                if self.Rcrc.isChecked():
                    self.tcp.send(self.LEmsgenviar.text() + ":/::/:" + str((binascii.crc32(str(self.LEmsgenviar.text())) & 0xFFFFFFFF)))
                else:
                    self.tcp.send(self.LEmsgenviar.text() + ":/::/:" + str(hashlib.md5(str(self.LEmsgenviar.text())).hexdigest()))
            except:
                error = Error()
                error.show()
                error.setErro(sys.exc_info())
                raise
        else:
           self.orig = (str(self.LEip.text()), int(self.LEporta.text()))
           try:
#               self.udp.sendto(self.LEmsgenviar.text(), self.orig)
               if self.Rcrc.isChecked():
                   self.udp.sendto(self.LEmsgenviar.text() + ":/::/:" + str((binascii.crc32(str(self.LEmsgenviar.text())) & 0xFFFFFFFF)), self.orig)
               else:
                   self.udp.sendto(self.LEmsgenviar.text() + ":/::/:" + str(hashlib.md5(str(self.LEmsgenviar.text())).hexdigest()), self.orig)
           except:
               error = Error()
               error.show()
               error.setErro(sys.exc_info())
               raise

    def enviaImg(self):
        try:
            myfile = open(str(self.LEimgenviar.text()), 'rb')
        except:
            error = Error()
            error.show()
            error.setErro(sys.exc_info())
            raise
        bytes = myfile.read()
        size = len(bytes)
        if self.Rtcp.isChecked():
            try:
#                self.tcp.send(bytes)
                if self.Rcrc.isChecked():
                    self.tcp.send(bytes + ":/::/:" + str((binascii.crc32(str(bytes)) & 0xFFFFFFFF)))
                else:
                    self.tcp.send(bytes + ":/::/:" + str(hashlib.md5(str(bytes)).hexdigest()))
            except:
                error = Error()
                error.show()
                error.setErro(sys.exc_info())
                raise
        else:
           self.orig = (str(self.LEip.text()), int(self.LEporta.text()))
           try:
#               self.udp.sendto(bytes, self.orig)
               if self.Rcrc.isChecked():
                   self.udp.sendto(bytes + ":/::/:" + str((binascii.crc32(str(bytes)) & 0xFFFFFFFF)), self.orig)
               else:
                   self.udp.sendto(bytes + ":/::/:" + str(hashlib.md5(str(bytes)).hexdigest()), self.orig)
           except:
               error = Error()
               error.show()
               error.setErro(sys.exc_info())
               raise

    def conectar(self):
        if self.conectado or self.Rudp.isChecked(): return

        self.orig = (str(self.LEip.text()), int(self.LEporta.text()))
        orig = self.orig
        print 'conectando porta Orig = ', orig
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.connect(orig)
        self.conectado = True

    def ouvir(self):
        if self.ouvindo == 1: return
        self.origr = (str(self.LEip_2.text()), int(self.LEporta_2.text()))
        ouvinte = Thread(target = self.recebeMsg, args = [self.Lmsgrecebida])
        ouvinte.start()

    def ouvirImg(self):
        if self.ouvindo == 1: return
        self.origr = (str(self.LEip_2.text()), int(self.LEporta_2.text()))
        ouvinte = Thread(target = self.recebeImg, args = [self.Lmsgrecebida])
        ouvinte.start()

    def fechaconexao(self):
        self.fecha = True
        self.conectado = False
        self.tcp.close()


def myclose():
    main.fechaconexao()

if __name__ == '__main__' :
    app = QtGui.QApplication(sys.argv)
    app.aboutToQuit.connect(myclose)
    main = Main()
    main.show()
    sys.exit(app.exec_())
