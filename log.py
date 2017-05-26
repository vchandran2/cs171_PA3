class log():
    def __init__(self, filename):
        self.filename = filename
        self.file = {}
        f = open(self.filename)
        for line in f:
            line.strip().split(',')
            self.file[line[0]] = line[1]
