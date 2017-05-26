class log():
    def __init__(self, filename,wdict=None):
        self.filename = filename
        self.file = {}
        if wdict is None:
            f = open(self.filename)
            for line in f.readlines():
                line = line.strip().split(',')
                self.file[line[0]] = int(line[1])
            print('file from log constructor:',self.file)
        else:
            self.file = wdict


