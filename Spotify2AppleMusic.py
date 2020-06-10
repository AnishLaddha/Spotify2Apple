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
import eyed3
import youtube_dl
from urllib.request import urlopen
from youtube_search import YoutubeSearch
import shutil
from os import path


client_credentials_manager = SpotifyClientCredentials(client_id='2528e9e7f4fa492aaecfc9e07c18f444',
                                                      client_secret='c1595dd6fe0a406ca075ba7e5733ec79')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

class MainPage(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.tableClick()
        self.url_error_label.setText("")
        self.url_load_button.clicked.connect(self.url_loading_button_click)
        self.remove_from_table_button.clicked.connect(self.remove_button_click)
        self.url_input.returnPressed.connect(self.url_load_button.click)
        self.download_button.clicked.connect(self.download_button_click)
        self.url_input.mousePressEvent = lambda _: self.url_input.selectAll()
        self.credit_url.linkActivated.connect(self.set_credit_url)
        self.credit_url.setText(
            '<a href="https://github.com/AnishLaddha/Spotify2Apple">source code</a>'
        )
        self.video_table.setHorizontalHeaderLabels(["Song", "Artist(s)", "Album", "Album Artist(s)", "Cover Art"])
        self.video_table.setHorizontalHeaderLabels(["Song", "Artist(s)", "Album", "Album Artist(s)", "Cover Art"])



    def set_credit_url(self, url_str):
        """Set source code url on upper right of table."""
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url_str))
    
    def tableClick(self):
        self.video_table.doubleClicked.connect(self.on_click)
        self.video_table.cellClicked.connect(self.cell_was_clicked)

    def remove_button_click(self):
        indexes = self.video_table.selectedIndexes()
        for index in (indexes):
            self.video_table.removeRow(index.row())
        

    def url_loading_button_click(self):
        urlstr = self.url_input.text()
        #print(self.url_input.text())
        if urlstr != "":
            urldict = urlstr.rsplit('/',1)
            if urldict[1] == "":
                urldict = urlstr.rsplit('/',2)
            url = urldict[1]
            split_url = url.split("?",1)
            url = split_url[0]
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
        self.video_table.setHorizontalHeaderLabels(["Song", "Artist(s)", "Album", "Album Artist(s)", "Cover Art"])
        


    def cell_was_clicked(self):
        for currentQTableWidgetItem in self.video_table.selectedItems():
            #print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
            item = self.video_table.item(currentQTableWidgetItem.row(), 4)
            url = str(item.text())
            #print(url)
            self.loadArtwork(url)
        
        
    def on_click(self):
        #print("\n")
        for currentQTableWidgetItem in self.video_table.selectedItems():
            pass

   
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
    

    
    ##
    ##aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ##aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ##aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ##aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    def download_button_click(self):
        space = """
        ...............................................................
        ...............................................................
        ...............................................................
        ...............................................................
          """
        songlist = self.load_tracks_from_table()
        for song in songlist:
            if self.filecheck(song.sname, song.albartist, song.albname) == False:
                print(space)
                print(song.sname)
                print(space)
                yt_link = self.youtubelink(song.sname, song.sartist)
                self.downloader(yt_link, song.sname)
                self.convertor(song.sname)
                self.tagger(song, song.sname)
                self.filemove()

                
    ##aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ##aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ##aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ##aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ##aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    
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
        data.pop()
        for track in data:
            tlist.append(Song(track[0], track[1], track[4], track[2], track[3], ""))
        return tlist
        
    
    
    def filecheck(self,song, artist, album):
        base_dir = "~/Music/Music/Media.localized"
        base_dir= base_dir + "/" + artist + "/"+album +"/" + song +".mp3"
        return os.path.isfile(os.path.expanduser(base_dir))
    def fcheck2(self,song):
        if os.path.isfile(song+".mp3"):
            return True
        else:
            return False
    def filemove(self):
        dir_path = os.path.dirname(os.path.realpath(__file__)) 
  
        for root, dirs, files in os.walk(dir_path): 
            for file in files:  
                if file.endswith('.mp3'): 
                    print(str(file))

                    chdir = str(os.getcwd())
                    shutil.move(chdir+"/"+str(file), os.path.expanduser("~")+'/Music/Music/Media.localized/Automatically Add to Music.localized/'+str(file))
            
#mv -f "Ridin' Solo.mp3" ~/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ Music.localized"
    def youtubelink(self, song, artist):
        i = song +" by "+ artist
        try:
            searchresults = YoutubeSearch(i+" audio" , max_results=1).to_dict()
            searchresult = searchresults[0]
            searchid = searchresult['id']
            if searchid[0] == "-":
               searchid = searchid[1:]
        except:
            searchresults = YoutubeSearch(i+" audio" , max_results=1).to_dict()
            searchresult = searchresults[0]
            searchid = searchresult['id']
            if searchid[0] == "-":
               searchid = searchid[1:]
        return searchid
    
    def convertor(self, name):
        if (path.exists(name+".m4a") == True):
            print('ffmpeg -y -i "'+name+'".m4a -acodec libmp3lame -ab 256k "'+name+'.mp3"'+'&& rm "'+name+'.m4a"')
            os.system('ffmpeg -y -i "'+name+'".m4a -acodec libmp3lame -ab 256k "'+name+'.mp3"'+'&& rm "'+name+'.m4a"')
    #'fmpeg -i "'+name+'".m4a -acodec libmp3lame -ab 256k '+name+'.mp3"'
    def downloader(self, url, name):
        ydl_opts = {
            'outtmpl': '',
            'format': 'm4a',
            'quiet': True,
            
        }
        ydl_opts['outtmpl']= name + ".%(ext)s"
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except:
                try:
                    ydl.download([url])
                except:
                    print("not found")
    def tagger(self, songdata, file):
        if (path.exists(file+".mp3") == True):
            songname = songdata.sname

            songartstr = songdata.sartist
            albumname = songdata.albname

            albartstr = songdata.albartist
            

            coverarturl = songdata.coverart
        
            audiofile = eyed3.load(file+".mp3")

            audiofile.tag.artist = songartstr
            audiofile.tag.album = albumname
            audiofile.tag.album_artist = albartstr
            audiofile.tag.title = songname

            response = urlopen(coverarturl)
            imagedata = response.read()

            audiofile.tag.images.remove(u'')
            audiofile.tag.images.set(3, imagedata , "image/jpeg" ,u"Description")

            audiofile.tag.save()    



if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainPage()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    widget.show()
    sys.exit(app.exec_())    