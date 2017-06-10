import socket
import time


class Mapper():
    def __init__(self,IP,portnum,ID):
        self.addr = (IP,int(portnum))
        self.ID = ID
        self.word_dict = {}
        self.cli_in = None

    def setup(self):
        print("setting up at: ", self.addr)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(self.addr)
        s.listen(1)
        print('attempting to accept')
        conn, addr_in = s.accept()
        conn.setblocking(0)
        self.cli_in = conn
        print("done with setup")

    def receiveMessages(self):
        while(True):
            try:
                datar = self.cli_in.recv(1024).decode()
                datar = datar.strip().split('&')
                print(datar)
                for data in datar:
                    data = data.strip().split('|')
                    if len(data) == 3:
                        filename = data[0]
                        offset = data[1]
                        size = data[2]
                        self.map(filename, offset, size)
            except socket.error:
                time.sleep(0.25)


    def extract(self,filename,offset,size):                              #fills the word_dict
        openfile = open(filename)
        openfile.seek(int(offset))
        openfile = openfile.read(int(size))
        openfile = str.lower(openfile)
        split_file = openfile.strip().split()
        for word in split_file:
            word = self.stripWord(word)
            if (word != ''):
                if word in self.word_dict:
                    self.word_dict[word] += 1
                else:
                    self.word_dict[word] = 1

    def writeToFile(self,filename):                                       #writes dict to file
        newfilename = filename[0:-4]+ "_I_"+str(self.ID)[-2]+'.txt'
        newfile = open(newfilename,"w")
        for word in self.word_dict:
            for i in range(int(self.word_dict[word])):
                line = word+", 1\n"
                newfile.write(line)
        newfile.close()

    def stripWord(self, word):
        newWord = ''
        for char in word:
            if char >= 'a' and char <= 'z':
                newWord += char
        return newWord

    def run(self):
        self.setup()
        self.receiveMessages()

    def map(self,filename,offset,size):
        print('starting to map', filename)
        self.extract(filename,offset,size)
        self.writeToFile(filename)
        self.word_dict = {}
