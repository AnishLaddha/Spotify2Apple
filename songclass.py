class Song:
    def __init__(self, sname, sartist, coverart, albname, albartist, spotid):
        self.sname = sname
        self.sartist = sartist
        self.coverart = coverart
        self.albname = albname
        self.albartist = albartist
        self.spotid = spotid
    
    def encode(self):
        return self.__dict__
    def __str__(self):
        return self.sname +" by "+ self.sartist+" of "+self.albname+" by "+self.albartist

        
