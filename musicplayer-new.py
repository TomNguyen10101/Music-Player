# MUSIC PLAYER
# Author: Quan Nguyen
# Start Date: 05/14/2023

import customtkinter
from tkinter import StringVar
from tkinter import PhotoImage
from tkinter import Listbox
from tkinter import CENTER
from tkinter import SINGLE
from tkinter import FLAT
from tkinter import END
from mutagen.mp3 import MP3
from tkinter import filedialog
import pygame
import os
import random

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

# A class to hold the details of the song
class Song:
    def __init__(self, file, artist=None):
        self.artist = artist
        self.file = file
        self.prev = None
        self.next = None
        self.name = os.path.basename(file).replace(".mp3","")
        
        # Get the song length
        song =  MP3(file)
        min, sec = divmod(song.info.length, 60)
        hour, min = divmod(min, 60)
        self.lengthInSec = song.info.length
        self.songLength = f"{int(min)}:{int(sec)}"

# A class that used to store all the songs
class Playlist:
    def __init__(self):
        self.head = None
        self.currentSong = None
        self.size = 0
        self.songList = []
    
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
                return

        newSong.prev = currentNode
        newSong.next = currentNode.next
        currentNode.next = newSong

    # Append song(s) into the playlist
    def Append(self, newSong) -> bool:
        # Prevent duplication
        if newSong.file in self.songList:
            return True
        else:
            self.songList.append(newSong.file)

        currentNode = self.head

        if currentNode == None:
            self.head = newSong
        else:
            while(currentNode.next != None):
                currentNode = currentNode.next
            newSong.prev = currentNode
            currentNode.next = newSong       
        self.size += 1
        return False

    # Remove song from the playlist
    def Remove(self,songFile):
        # First, we need to find that node in list
        currentNode = self.head

        if currentNode == None:
            return
        else:
            # Special case: if remove the first element in the list
            if currentNode.file == songFile:
                if(currentNode.next == None):
                    self.head = None
                else:
                    self.head = currentNode.next
            else:
                while(currentNode.file != songFile):
                    currentNode = currentNode.next
       
                currentNode.prev.next = currentNode.next

            # Update the song list
            self.songList.remove(songFile)

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
        self.track = StringVar()
        self.track.set("The Music Player")

        # Volume Variable(s)
        self.mute = False
        self.preVol = 0.0

        # Time Variable(s)
        self.runningTime = StringVar()
        self.songLength = StringVar()
        self.runningTime.set("0:00")
        self.songLength.set("0:00")

        # Track State Variable(s)
        self.singleLoop = False
        self.loop = False
        self.shuffle = False
        self.pause = False
        self.isRunning = False
        self.stop = True
        self.loopState = 0

        # ListBox Variable(s)
        self.chosenItem = None

        # Initiate Playlist object
        self.playlist = Playlist()

        # Instantiate a Pygame (music mixer) object
        pygame.init()
        pygame.mixer.init()
        self.songEnd = False
        self.SONG_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.SONG_END)
        self.preVol = pygame.mixer.music.get_volume()

        # Using Tkinter module, create a interactive GUI
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("600x500")
        self.pos = 0
        self.prevIndex = None
        self.currIndex = None

        # Images
        self.loopImage = PhotoImage(file="Icons\\repeat.png")
        self.backImage = PhotoImage(file="Icons\\previous.png")
        self.playImage = PhotoImage(file="Icons\\play-button-arrowhead.png")
        self.skipImage = PhotoImage(file="Icons\\next.png")
        self.shuffleImage = PhotoImage(file="Icons\\shuffle.png")
        self.pauseImage = PhotoImage(file="Icons\\pause.png")
        self.repeatonceImage = PhotoImage(file="Icons\\repeat-once.png")
        self.speakerImage = PhotoImage(file="Icons\\speaker.png")
        self.muteImage = PhotoImage(file="Icons\\mute-speaker.png")
        self.folderImage = PhotoImage(file="Icons\\folder.png")
        self.addImage = PhotoImage(file="Icons\\add.png")
        self.rmvImage = PhotoImage(file="Icons\\minus.png")

        # NEW GUI
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure((0,1), weight=1)

        # Define Font
        font = customtkinter.CTkFont(family="Helvatica",
                                        size = 15,
                                        weight="normal")

        self.queuelistFrame= customtkinter.CTkFrame(master=self.root)
        self.queuelistFrame.grid(row=0,column=0,padx=20, columnspan=2, pady=(20,0), sticky="nsew")

        self.queuelistFrame.grid_rowconfigure(0, weight=1)
        self.queuelistFrame.grid_columnconfigure((0, 2), weight=1)

        # create scrollable textbox
        self.trackTextBox = Listbox(master=self.queuelistFrame,selectmode=SINGLE,font=font,bg="#404040",fg="white",bd=0,activestyle = 'dotbox', relief=FLAT, highlightthickness=0,exportselection = False, state="disabled")
        self.trackTextBox.grid(row=0, column=1, columnspan=2,sticky="nsew")
        self.trackTextBox.bind("<Double-1>", self.doubleClickEvent)

        # create CTk scrollbar
        self.scrollbar = customtkinter.CTkScrollbar(master=self.queuelistFrame, command=self.trackTextBox.yview)
        self.scrollbar.grid(row=0, column=3, sticky="ns")
        # connect textbox scroll event to CTk scrollbar
        self.trackTextBox.configure(yscrollcommand=self.scrollbar.set)

        self.addSongBtn = customtkinter.CTkButton(master=self.queuelistFrame,text="", width=40, height=40,hover_color="#fff", fg_color="#CD4F39",image=self.addImage,command=self.AddSong)
        self.addSongBtn.place(relx=0.07 , rely=0.09, anchor=CENTER)

        self.addListBtn = customtkinter.CTkButton(master=self.queuelistFrame,text="", width=40, height=40,hover_color="#fff", fg_color="#CD4F39",image=self.folderImage,command=self.AddPlayList)
        self.addListBtn.place(relx=0.17 , rely=0.09, anchor=CENTER)

        self.rmvSongBtn = customtkinter.CTkButton(master=self.queuelistFrame,text="", width=40, height=40,hover_color="#fff", fg_color="#CD4F39",command=self.RemoveSong,image=self.rmvImage)
        self.rmvSongBtn.place(relx=0.27 , rely=0.09, anchor=CENTER)
        
        self.controllerFrame = customtkinter.CTkFrame(master=root, height=70, width=570)
        self.controllerFrame.grid(row=3,column=0,padx=20,pady=5,sticky="nsew")

        self.statusFrame = customtkinter.CTkFrame(master=root, height=35, width=100,fg_color="transparent")
        self.statusFrame.grid(row=2,column=0, padx = 80, pady=5, sticky="nsew")

        self.trackLabel = customtkinter.CTkLabel(master=root, textvariable=self.track,font=font)
        self.trackLabel.grid(row=1,column=0, pady=10, sticky="nsew")

        self.statusFrame.grid_rowconfigure(0, weight=1)
        self.statusFrame.grid_columnconfigure((0, 2), weight=1)

        self.timeBar = customtkinter.CTkProgressBar(master=self.statusFrame, orientation="horizontal",progress_color="#CD4F39")
        self.timeBar.grid(row=0,column=1)

        self.timeRunning = customtkinter.CTkLabel(master=self.statusFrame, textvariable=self.runningTime)
        self.timeRunning.grid(row=0,column=0)

        self.songTime = customtkinter.CTkLabel(master=self.statusFrame, textvariable=self.songLength)
        self.songTime.grid(row=0,column=2)

        self.BackBtn = customtkinter.CTkButton(master=self.controllerFrame, text="",image=self.backImage, width=30, height=30,fg_color="transparent",hover_color="#CD4F39",command=self.Backward)
        self.BackBtn.place(relx=0.25, rely=0.5, anchor=CENTER)

        self.playBtn= customtkinter.CTkButton(master=self.controllerFrame,text="",image=self.playImage, width=30, height=30,fg_color="transparent",hover_color="#CD4F39",command=self.PlayButtonClick)
        self.playBtn.place(relx=0.38 , rely=0.5, anchor=CENTER)

        self.SkipBtn = customtkinter.CTkButton(master=self.controllerFrame, text="",image=self.skipImage, width=30, height=30,fg_color="transparent",hover_color="#CD4F39",command=self.Forward)
        self.SkipBtn.place(relx=0.51 , rely=0.5, anchor=CENTER)

        self.ShuffleBtn = customtkinter.CTkButton(master=self.controllerFrame, text="", width=30, height=30,image=self.shuffleImage,command=self.ShuffleButtonClick,fg_color="transparent",hover_color="#CD4F39")
        self.ShuffleBtn.place(relx=0.10, rely=0.5, anchor=CENTER)

        self.LoopBtn = customtkinter.CTkButton(master=self.controllerFrame, text="", image=self.loopImage, width=30, height=30,fg_color="transparent",command=self.LoopButtonClick, hover_color="#CD4F39")
        self.LoopBtn.place(relx=0.64, rely=0.5, anchor=CENTER)

        self.volBtn = customtkinter.CTkButton(master=self.controllerFrame, text="", image=self.speakerImage, width=30, height=30,fg_color="transparent",command=self.SpeakerButtonClick, hover_color="#CD4F39")
        self.volBtn.place(relx=0.75, rely=0.5, anchor=CENTER)

        self.volumnSlider = customtkinter.CTkSlider(master=self.controllerFrame,width=100,from_=0,to=100,command=self.AdjustVolume,progress_color="#CD4F39", button_color="#CD4F39", button_hover_color="#CD4F39")
        self.volumnSlider.place(relx=0.88, rely=0.5, anchor=CENTER)
        self.volumnSlider.set(self.preVol)
    
    # Play the current song
    def Play(self):
        if(self.pause == False and self.isRunning == True):
            self.playBtn.configure(image=self.pauseImage)
            self.Pause()
        else:
            self.playBtn.configure(image=self.playImage)
            pygame.mixer.music.unpause()
            self.pause = False

        # Case: Play the list when first started without current song
        if(self.playlist.currentSong == None):
            if(self.shuffle == True):
                self.Shuffle()
            else:
                self.playlist.currentSong = self.playlist.head
                self.currIndex = 0

        if(not self.isRunning):
            try:
                pygame.mixer.music.load(self.playlist.currentSong.file)
                pygame.mixer.music.play()

                # Hard To Do: Add a fade effect between songs

                self.track.set(self.playlist.currentSong.name)

                if(self.prevIndex is None):
                    self.trackTextBox.itemconfig(self.currIndex, {'fg': '#CD4F39'})
                else:
                    self.trackTextBox.itemconfig(self.prevIndex, {'fg': '#fff'})
                    self.trackTextBox.itemconfig(self.currIndex, {'fg': '#CD4F39'})
                
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
                    if self.singleLoop:
                        self.Play()
                    elif self.shuffle:
                        self.Shuffle()
                        self.Play()
                    elif(self.playlist.currentSong.next is not None and not self.singleLoop):
                        self.playlist.currentSong = self.playlist.currentSong.next
                        self.Play()
                    elif self.loop:
                        self.playlist.currentSong = self.playlist.head
                        self.prevIndex = self.currIndex
                        self.currIndex = 0
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
        if self.playlist.currentSong is None:
            return
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
        if self.playlist.currentSong is None:
            return
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

    # Adjust Volumn using the value get from the slider
    def AdjustVolume(self, value):
        self.preVol = value * 0.01
        pygame.mixer.music.set_volume(self.preVol)     

    # When play button clicked, run these methods
    def PlayButtonClick(self):
        self.Play()
        root.after(100, self.CheckSongStatus, root)
        root.after(100, self.GetTime, root)

    # Enable/Disable Shuffle Mode
    def ShuffleButtonClick(self):
        if self.shuffle == False:
            self.shuffle = True
            self.ShuffleBtn.configure(fg_color="#CD4F39")           
        else:
            self.shuffle = False
            self.ShuffleBtn.configure(fg_color="transparent")
    
    # Enable/Disable Loop, Single Loop
    def LoopButtonClick(self):
        if self.loopState < 2:
            self.loopState += 1
        else:
            self.loopState = 0

        match(self.loopState):
            case 0:
                self.loop = False
                self.singleLoop = False
                self.LoopBtn.configure(image=self.loopImage)
                self.LoopBtn.configure(fg_color="transparent")    
            case 1:
                self.loop = True
                self.LoopBtn.configure(fg_color="#CD4F39")
            case 2:
                self.singleLoop = True
                self.LoopBtn.configure(image=self.repeatonceImage)

    # Mute/Unmute
    def SpeakerButtonClick(self):
        if self.mute:
            pygame.mixer.music.set_volume(self.preVol)
            self.volBtn.configure(image=self.speakerImage)
            self.mute = False
            self.volumnSlider.set(self.preVol * 100)
        else:
            pygame.mixer.music.set_volume(0)
            self.volBtn.configure(image=self.muteImage)
            self.mute = True
            self.volumnSlider.set(0)

    # Add (playlist) folder to the program
    def AddPlayList(self):
        self.trackTextBox.configure(state="normal")
        #Ask for the folder that contains music files, and add those to the playlist
        folderPath = filedialog.askdirectory(title="Choose a music folder")
        os.chdir(folderPath)
        songtracks = os.listdir()
        for i, track in enumerate(songtracks):
            newSong = Song(track)
            isDuplicate = self.playlist.Append(newSong)
            if not isDuplicate:
                self.trackTextBox.insert(END, f"{i + 1}. {track}")
    
    # Add specific mp3 file to the program
    def AddSong(self):
        self.trackTextBox.configure(state="normal")
        filePath = filedialog.askopenfile(title="Choose a MP3 file",mode='r')
        file = os.path.abspath(filePath.name)
        track = os.path.basename(filePath.name)
        newSong = Song(file=file)
        isDuplicate = self.playlist.Append(newSong)
        if not isDuplicate:
            self.trackTextBox.insert(END, f"{self.playlist.size}. {track}")

    # Remove the choosing song from the listbox
    def RemoveSong(self):
        index = self.trackTextBox.curselection()
        if index:
            self.chosenItem = index[0]
            song = self.trackTextBox.get(self.chosenItem)
            spaceIndex = song.find(' ')
            self.playlist.Remove(song[spaceIndex + 1:])

            # Display the new playlist after removing
            self.trackTextBox.delete(0,END)
            for i, track in enumerate(self.playlist.songList):
                self.trackTextBox.insert(END, f"{i + 1}. {track}")

    # Custom Handler for double click event on the ListBox
    def doubleClickEvent(self,event):
        self.isRunning = False
        index = self.trackTextBox.curselection()
        if index:
            selectedIndex = index[0]
            self.prevIndex = self.currIndex
            self.currIndex = selectedIndex

            if(self.playlist.currentSong is None):
                self.playlist.Get(selectedIndex)
                self.PlayButtonClick()
            else:
                self.playlist.Get(selectedIndex)
                self.Play()
        
        # Clear the selection in the listbox
        self.trackTextBox.selection_clear(0, self.trackTextBox.size()-1)

    # Display the song playtime on the GUI and update the progress bar
    def GetTime(self, root):
        if self.isRunning:
            # Display Time 
            currentTimeInSec = pygame.mixer.music.get_pos()/1000
            min, sec = divmod(currentTimeInSec, 60)
            hour, min = divmod(min, 60)

            if(sec < 10):
                currentTime = f"{int(min)}:0{int(sec)}"
            else:
                currentTime = f"{int(min)}:{int(sec)}"
            
            self.runningTime.set(currentTime)
            self.songLength.set(self.playlist.currentSong.songLength)

            # Update the progress bar
            progress = currentTimeInSec / self.playlist.currentSong.lengthInSec
            self.timeBar.set(progress)

        root.after(50, self.GetTime, root)


root = customtkinter.CTk()
musicPlayer = MusicPlayer(root)
root.mainloop()

