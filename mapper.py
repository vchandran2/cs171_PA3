import sys

class Mapper():
    def __init__(self,IP,portnum,ID):
        self.addr = (IP,int(portnum))
        self.ID = ID
        self.word_dict = {}

    def extract(self,filename,offset):                                         #fills the word_dict
        openfile = open(filename).read()
        #openfile = openfile[offset:]# self.size??]
        openfile = str.lower(openfile)
        split_file = openfile.strip().split()
        for word in split_file:
            word = self.stripWord(word)
            if word in self.word_dict:
                self.word_dict[word] += 1
            else:
                self.word_dict[word] = 1

    def writeToFile(self,filename):                                       #writes dict to file
        newfilename = filename[0:-4]+ "_I_"+str(self.ID)+'.txt'
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

    def map(self,filename,offset):
        self.extract(filename,offset)
        self.writeToFile(filename)
        self.word_dict = {}
