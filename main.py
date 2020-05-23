import os
import sys
import time
from functools import partial
import requests
import qdarkstyle
from PyQt5.QtCore import QThread, QPersistentModelIndex, pyqtSignal
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QIcon, QPixmap

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from songclass import Song
from spot2apple import Ui_MainWindow
import json
import urllib.request


client_credentials_manager = SpotifyClientCredentials(client_id='2528e9e7f4fa492aaecfc9e07c18f444',
                                                      client_secret='c1595dd6fe0a406ca075ba7e5733ec79')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

class MainPage(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.tableClick()
        self.video_table.setHorizontalHeaderLabels(["Song", "Artist(s)", "Album", "Album Artist(s)", "Cover Art"])
        self.url_load_button.clicked.connect(self.url_loading_button_click)
        self.remove_from_table_button.clicked.connect(self.remove_button_click)
        self.url_input.returnPressed.connect(self.url_load_button.click)
        self.download_button.clicked.connect(self.load_tracks_from_table)
        self.url_input.mousePressEvent = lambda _: self.url_input.selectAll()


    def tableClick(self):
        self.video_table.doubleClicked.connect(self.on_click)
        self.video_table.cellClicked.connect(self.cell_was_clicked)

    def remove_button_click(self):
        indexes = self.video_table.selectedIndexes()
        for index in sorted(indexes):
            self.video_table.removeRow(index.row())
        

    def url_loading_button_click(self):
        urlstr = self.url_input.text()
        #print(self.url_input.text())
        if urlstr != "":
            urldict = urlstr.rsplit('/',1)
            if urldict[1] == "":
                urldict = urlstr.rsplit('/',2)
            url = urldict[1]
           # print(url)
        results = sp.playlist_tracks(url)
        tracks = results['items']
        tracklist = self.createDict(tracks)
        self.video_table.clear()
        index = 0
        for i in tracklist:
            self.video_table.setItem(index, 0, QTableWidgetItem(i.sname))
            self.video_table.setItem(index, 1, QTableWidgetItem(', '.join(i.sartist)))
            self.video_table.setItem(index, 2, QTableWidgetItem(i.albname))
            self.video_table.setItem(index, 3, QTableWidgetItem(', '.join(i.albartist)))
            self.video_table.setItem(index, 4, QTableWidgetItem(i.coverart))
            index = index +1
            
        


    def cell_was_clicked(self):
        for currentQTableWidgetItem in self.video_table.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
            item = self.video_table.item(currentQTableWidgetItem.row(), 4)
            url = str(item.text())
            print(url)
            self.loadArtwork(url)
        
        
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.video_table.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
   
    def loadArtwork(self, url):
        data = urllib.request.urlopen(url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.album_artwork.setPixmap(pixmap)
    
    def createDict(self, tdict):
        tracklist = []
        for i in tdict:
            track = i['track']
            album = track['album']
            albumname = album["name"] ##album name 
            albartists = []
            for i in album["artists"]:
                albartists.append(i["name"]) ##album artists
            albimgs = album["images"]
            try:
                albimgt = albimgs[0]
                albimg = albimgt["url"] ## coverart
        
            except:
                albimg = "https://image.shutterstock.com/image-photo/concert-hall-lit-stage-people-600w-1043460649.jpg"
        
            songname = track["name"] ##songname
            spotid = track["id"] ##spotify id
            artistlist = []
        
            for i in track["artists"]:
                artistlist.append(i["name"]) ##song artists
            newsong = Song(songname, artistlist, albimg, albumname, albartists, spotid)
            tracklist.append(newsong)
        return tracklist
    def load_tracks_from_table(self):
        model = self.video_table.model()
        data = []
        for row in range(model.rowCount()):
            data.append([])
            if str(model.data(model.index(row,0))) == "None":
                break
            else:
                for column in range(model.columnCount()):
                    index = model.index(row, column)
                    # We suppose data are strings
                    data[row].append(str(model.data(index)))
        print(data)
        tlist = []
        for track in data:
            tlist.append(Song(track[0], track[1], track[4], track[2], track[3]))
        
    
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

        
        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainPage()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    widget.show()
    sys.exit(app.exec_())    