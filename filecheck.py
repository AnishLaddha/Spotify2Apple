import os
def musiccheck():
    base_dir = "~/Music"
    folder = os.path.expanduser(base_dir)
    check = os.path.isdir(folder)
    if check == True:
        base_dir= base_dir + "/iTunes"
        folder = os.path.expanduser(base_dir)
        check = os.path.isdir(folder)
        if check == True:
            base_dir= base_dir + "/iTunes Media/Music"
            folder = os.path.expanduser(base_dir)
            check = os.path.isdir(folder)
            if check == True:
                return True
    return false
def filecheck(song, artist, album):
    base_dir = "~/Music/itunes/iTunes Media/Music"
    base_dir= base_dir + "/" + artist + "/"+album +"/" + song +".mp3"
    file = os.path.expanduser(base_dir)
    check = os.path.isfile(file)
    if check == True:
        return 1
    else:
        return 0

def filemove(song):
    check = os.path.isfile(song)
    path_dir = "~/Music/iTunes/iTunes Media/'Automatically Add to Music'"
    if check == true:
        os.system("mv -f '"+song+"'.mp3 "+path_dir)



    
