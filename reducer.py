import time
import socket

class Reducer():
    def __init__(self, IP, portnum, ID):
        self.addr = (IP, int(portnum))
        self.ID = ID
        self.word_dict = {}
        self.cli_in = None

    def setup(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(self.addr)
        s.listen(1)
        print('attempting to accept')
        conn, addr_in = s.accept()
        conn.setblocking(0)
        self.cli_in = conn
        print("done with setup")

    def receiveMessages(self):
        filenames = []
        while(True):
            try:
                datar = self.cli_in.recv(1024).decode()
                datar = datar.strip().split('&')
                for data in datar:
                    data = data.strip().split('|')
                    filenames = data[1:3]
                    if (data[0] == 'reduce'):
                        break
                print(filenames)
                self.reduce(filenames)
            except socket.error:
                time.sleep(0.25)

    def run(self):
        self.setup()
        self.receiveMessages()

    def extract(self,filenames):
        for filename in filenames:
            #fills the word_dict
            openfile = open(filename).read()
            #openfile = openfile[offset:]# self.size??]
            openfile = str.lower(openfile)
            split_file = openfile.strip().split()
            for word in split_file:
                word = self.stripWord(word)
                if (word != ''):
                    if word in self.word_dict:
                        self.word_dict[word] += 1
                    else:
                        self.word_dict[word] = 1

    def writeToFile(self,filenames):                                       # writes dict to file
        print(filenames)
        newfilename = filenames[0][0:-8]+ '_reduced.txt'
        newfile = open(newfilename,"w")
        for word in self.word_dict:
            line = word+", "+str(self.word_dict[word])+"\n"
            newfile.write(line)
        newfile.close()

    def stripWord(self, word):
        newWord = ''
        for char in word:
            if char >= 'a' and char <= 'z':
                newWord += char
        return newWord

    def reduce(self,filenames):
        print('starting to reduce')
        self.extract(filenames)
        self.writeToFile(filenames)
        self.word_dict = {}
