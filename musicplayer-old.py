# MUSIC PLAYER
# Author: Quan Nguyen
# Start Date: 05/14/2023

import pygame
import os
from tkinter import *
from tkinter import filedialog
import random
from mutagen.mp3 import MP3


# A class to hold the details of the song
class Song:
    def __init__(self, artist, file):
        self.artist = artist
        self.file = file
        self.prev = None
        self.next = None

        index = file.find('.')
        self.name = file[0:index]
        
        # Get the song length
        song =  MP3(file)
        min, sec = divmod(song.info.length, 60)
        hour, min = divmod(min, 60)
        self.songLength = f"{int(min)}:{int(sec)}"

# A class that used to store all the songs
class Playlist:
    def __init__(self):
        self.head = None
        self.currentSong = None
        self.size = 0
    
    # Insert song into the playlist with specific index
    def InsertSong(self, newSong, index):
        # Traverse the list to go the suitable position to insert the node
        currentNode = self.head

        # Special case: Insert in 1st element
        if index == 0:
            if(currentNode != None):
                newSong.next = currentNode
                currentNode.prev = newSong
                self.head = newSong
            else:
                self.head = newSong
            
            return

        for i in range(index - 1):
            if(currentNode.next != None):
                currentNode = currentNode.next
            else:
                print("Can't Insert: Out of Bound")
                return

        newSong.prev = currentNode
        newSong.next = currentNode.next
        currentNode.next = newSong

    # Append song(s) into the playlist
    def Append(self, newSong):
        currentNode = self.head

        if currentNode == None:
            self.head = newSong
        else:
            while(currentNode.next != None):
                currentNode = currentNode.next
            newSong.prev = currentNode
            currentNode.next = newSong
        
        self.size += 1

    # Remove song(s) from the playlist
    def Remove(self, songName):
        pass

    # Get the song at specific index
    def Get(self, index):
        currentNode = self.head

        if currentNode == None:
            return "The List is Empty"
        else:
            for i in range(index):
                if(currentNode.next != None):
                    currentNode = currentNode.next
            
        self.currentSong = currentNode



class MusicPlayer:
    def __init__(self, root):
        self.singleLoop = IntVar()
        self.loop = IntVar()
        self.shuffle = IntVar()
        self.track = StringVar()
        self.status = StringVar()    
        self.pause = False
        self.isRunning = False
        self.stop = True

        # Initiate Playlist object
        self.playlist = Playlist()

        # Instantiate a Pygame (music mixer) object
        pygame.init()
        pygame.mixer.init()
        self.songEnd = False
        self.SONG_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.SONG_END)

        # Using Tkinter module, create a interactive GUI
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("1000x200")
        self.pos = 0
        self.prevIndex = None
        self.currIndex = 0

        self.trackframe = LabelFrame(self.root,text="Song Track",font=("times",15,"bold"),bg="#404040",fg="white",bd=5,relief=GROOVE)
        self.trackframe.place(x=0,y=0,width=600,height=100)
        self.songtrack = Label(self.trackframe,textvariable=self.track,width=20,font=("arial",24,"bold"),bg="#404040",fg="#B0FC38")
        self.songtrack.grid(row=0,column=0,padx=10,pady=5)
        self.songtrack.place(x=self.pos,y=0)
        self.timestatus = Label(self.trackframe,textvariable=self.status,font=("arial",16,"bold"),bg="#404040",fg="#B0FC38")
        self.timestatus.grid(row=0,column=0,padx=10,pady=5)
        self.timestatus.place(x = 450, y = 10)

        self.buttonframe = LabelFrame(self.root,text="Control Panel",font=("times",15,"bold"),bg="#404040",fg="white",bd=5,relief=GROOVE)
        self.buttonframe.place(x=0,y=100,width=600,height=100)

        desiredY = 15
        desiredX = 10

        self.playBtn = Button(self.buttonframe,text="PLAY",command=self.PlayButtonClick,width=5,height=1,font=("arial",10,"bold"),fg="white",bg="#A0A0A0")
        self.playBtn.grid(row=0, column=0, padx=desiredX, pady=desiredY)
        self.stopBtn = Button(self.buttonframe,text="STOP",command=self.Stop,width=5,height=1,font=("arial",10,"bold"),fg="white",bg="#A0A0A0").grid(row=0,column=1,padx=desiredX,pady=desiredY)
        self.skipBtn = Button(self.buttonframe,text="SKIP",command=self.Forward,width=5,height=1,font=("arial",10,"bold"),fg="white",bg="#A0A0A0").grid(row=0,column=3,padx=desiredX,pady=desiredY)
        self.backBtn = Button(self.buttonframe,text="BACK",command=self.Backward,width=5,height=1,font=("arial",10,"bold"),fg="white",bg="#A0A0A0").grid(row=0,column=5,padx=desiredX,pady=desiredY)
        
        self.shuffleBox = Checkbutton(self.buttonframe,text='Shuffle',variable=self.shuffle, onvalue=1, offvalue=0, width=6,height=1,highlightthickness=0)
        self.shuffleBox.config(fg="black",bg="#404040")
        self.shuffleBox.grid(row=0,column=7,padx=desiredX,pady=desiredY)

        self.loopBox = Checkbutton(self.buttonframe,text='Loop',variable=self.loop, onvalue=1, offvalue=0, width=6,height=1,highlightthickness=0)
        self.loopBox.config(fg="black",bg="#404040")
        self.loopBox.grid(row=0,column=9,padx=desiredX,pady=desiredY)

        self.singleLoopBox = Checkbutton(self.buttonframe,text='Single Loop',variable=self.singleLoop, onvalue=1, offvalue=0, width=9,height=1,highlightthickness=0)
        self.singleLoopBox.config(fg="black",bg="#404040")
        self.singleLoopBox.grid(row=0,column=11,padx=desiredX,pady=desiredY)

        songsframe = LabelFrame(self.root,text="Song Playlist",font=("times",15,"bold"),bg="#404040",fg="white",bd=5,relief=GROOVE)
        songsframe.place(x=600,y=0,width=400,height=200)
        scroll_y = Scrollbar(songsframe,orient=VERTICAL)
        self.tracklist = Listbox(songsframe,yscrollcommand=scroll_y.set,selectbackground="#B0FC38",selectmode=SINGLE,font=("arial",12,"bold"),bg="#404040",fg="white",bd=5,relief=GROOVE)

        scroll_y.pack(side=RIGHT,fill=Y)
        scroll_y.config(command=self.tracklist.yview)
        self.tracklist.pack(fill=BOTH)

        # Ask for the folder that contains music files, and add those to the playlist
        folderPath = filedialog.askdirectory(title="Choose a music folder")
        os.chdir(folderPath)
        songtracks = os.listdir()
        for track in songtracks:
            newSong = Song("", track)
            self.playlist.Append(newSong)
            self.tracklist.insert(END, track)
        
    # Play the current song
    def Play(self):
        if(self.pause == 0 and self.isRunning == True):
            print(self.isRunning)
            self.Pause()
            self.playBtn.config(text="PAUSE")
        else:
            self.playBtn.config(text="PLAY")
            pygame.mixer.music.unpause()
            self.pause = False

        # Case: Play the list when first started without current song
        if(self.playlist.currentSong == None):
            if(self.shuffle.get() == 1):
                self.Shuffle()
            else:
                self.playlist.currentSong = self.playlist.head
                self.currIndex = 0

        if(not self.isRunning):
            try:
                pygame.mixer.music.load(self.playlist.currentSong.file)
                print(self.playlist.currentSong.file)
                pygame.mixer.music.play()

                # Hard To Do: Add a fade effect between songs

                self.track.set(self.playlist.currentSong.name)

                if(self.prevIndex is None):
                    self.tracklist.itemconfig(self.currIndex, {'fg': '#B0FC38'})
                else:
                    self.tracklist.itemconfig(self.prevIndex, {'fg': '#fff'})
                    self.tracklist.itemconfig(self.currIndex, {'fg': '#B0FC38'})
                
                self.isRunning = True
                self.stop = False

            except:
                print("Can't play the audio")

    
    # This method is for checking whether the song has ended 
    # --> To move to the next song depends on the option of the user     
    def CheckSongStatus(self, root):
        for event in pygame.event.get():
            if event.type == self.SONG_END:
                self.isRunning = False
                if(not self.stop):
                    if(self.shuffle.get() == 1):
                        self.Shuffle()
                        self.Play()
                    elif(self.playlist.currentSong.next is not None and self.singleLoop.get() == 0):
                        self.playlist.currentSong = self.playlist.currentSong.next
                        self.Play()
                    elif (self.singleLoop.get() == 1):
                        self.Play()
                    elif(self.loop.get() == 1):
                        self.playlist.currentSong = self.playlist.head
                        self.Play()
                    else:
                        pygame.mixer.music.stop()
                        self.stop = True
                break
        
        # root will run this method after every 100 millisecs
        root.after(100, self.CheckSongStatus, root)

    # Pause the current song
    def Pause(self):
        pygame.mixer.music.pause()
        self.pause = True

    # Skip the current song
    def Forward(self):
        self.isRunning = False
        if(self.playlist.currentSong.next is not None):
            self.playlist.currentSong = self.playlist.currentSong.next
            if self.currIndex < (self.playlist.size - 1):
                self.prevIndex = self.currIndex    
                self.currIndex += 1
            self.Play()
        else:
            pygame.mixer.music.stop()
            self.stop = True

    # Play the previous song
    def Backward(self):
        self.isRunning = False
        if(self.playlist.currentSong.prev is not None):
            self.playlist.currentSong = self.playlist.currentSong.prev
            if self.currIndex > 0:
                self.prevIndex = self.currIndex    
                self.currIndex -= 1
            self.Play()
        else:
            pygame.mixer.music.stop()
            self.stop = True
    
    # Shuffle the playlist --> assign the next song to play 
    def Shuffle(self):
        randomIndex = random.randint(0, self.playlist.size - 1)
        self.playlist.Get(randomIndex) 

        if(self.prevIndex is None):
            self.currIndex = randomIndex
        else:
            self.prevIndex = self.currIndex
            self.currIndex = randomIndex        

    # Stop the current song
    def Stop(self):
        pygame.mixer.music.stop()
        self.stop = True

    # When play button clicked, run these methods
    def PlayButtonClick(self):
        self.Play()
        root.after(100, self.CheckSongStatus, root)
        root.after(100, self.MoveText, root)
        root.after(100, self.GetTime, root)

    # Create a scrolling effect for the running track label
    def MoveText(self,root):
        self.pos -= 1  # Update the position
        self.songtrack.place(x=self.pos, y=0)  # Place the label at the updated position

        # Check if the label has reached the end of the frame
        if self.pos <= -(self.songtrack.winfo_width() - 30):
            self.pos = self.timestatus.winfo_width() * 4  # Reset the position to the start of the frame

        root.after(50, self.MoveText, root)

    # Display the song playtime on the GUI
    def GetTime(self, root):
        if self.isRunning:
            currentTime = pygame.mixer.music.get_pos()/1000
            min, sec = divmod(currentTime, 60)
            hour, min = divmod(min, 60)
            currentTime = f"{int(min)}:{int(sec)}"
            self.status.set(f"{currentTime} / {self.playlist.currentSong.songLength}")
        root.after(100, self.GetTime, root)


    
root = Tk()
musicPlayer = MusicPlayer(root)
root.mainloop()


