import sys

class Reducer():
    def __init__(self, IP, portnum, ID):
        self.addr = (IP, int(portnum))
        self.ID = ID
        self.word_dict = {}

    def extract(self,filenames):
        filenames = filenames.strip().split()
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

    def writeToFile(self,filenames):                                       #writes dict to file
        filenames = filenames.strip().split()
        newfilename = filenames[0][0:-4]+ '_reduced.txt'
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
        self.extract(filenames)
        self.writeToFile(filenames)
        self.word_dict = {}
