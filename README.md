# **Music Player**

A music player which included all the functionalities that I took inspired from Spotify and others. This is my first project that built entirely on my own knowledge, research and references that I came across online.

## **Functionalities:** 
* Play
* Pause
* Enable Shuffle 
* Loop
* Single Loop
* Adjust Volume
* Mute/Unmute

## **Description**
This project was made as a learning experience for myself so it is nowhere near perfect, and I may improve user's experience as well as adding more functionalites to it. Feel free to give me any comment to enhance the project as it would only help me become a better developer. Thank you.



## **How to Install and Run the Project**
1. To run the project, you would need to install python and these modules:
    * [Pygame](https://github.com/pygame/pygame)
    * [Tkinter](https://docs.python.org/3/library/tkinter.html)
    * [mutagen](https://mutagen.readthedocs.io/en/latest/)
    * [Custom Tkinter](https://github.com/TomSchimansky/CustomTkinter)

2. Run this command in cmd/powershell to start:
```
python3 musicplayer-old.py
```
OR

```
python3 musicplayer-new.py
```
## **How to Use the Project**
OLD:
1. When start the project, it will ask for the folder that contains music files (make sure it only contains ".mp3" files - I may improve this in the future that works for all sound files extension)
2. There are 4 buttons to interact:
    * *Play*: Play song; Click again while a song is playing will pause the song.
    * *Stop*: Stop current song.
    * *Skip*: Skip current song.
    * *Back*: Go back to previous song.
3. There are 3 checkboxes to interact:
    * *Shuffle*: Enable shuffle mode which will randomly assign next song to play.
    * *Loop*: Enable Loop mode, which repeat the entire playlist.
    * *Single Loop*: Enable Single Loop mode, which keep repeating the current song

NEW:
1. When start the project, you can either click the "folder" button that contains music files (make sure it only contains ".mp3" files - I may improve this in the future that works for all sound files extension)
   OR click the "plus-sign" button to add specific ".mp3" file to the playlist
2. Buttons to interact:
    * *Play*: Play song; Click again while a song is playing will pause the song.
    * *Stop*: Stop current song.
    * *Skip*: Skip current song.
    * *Back*: Go back to previous song.
    * *Plus*: Add specific mp3 file to the playlist
    * *Folder*: Add entire folder to the playlist
    * *Minus*: Remove specific song in the playlist (Click on the song you want to remove then click this button)
    * *Loop* : Change the state into loop or single loop or off
    * *Shuffle*: Enable/Disable shuffle mode
    * *Sound*: Unmute/Mute
3.  Slider to interact: this is for adjusting the volume


## **Reference**
* https://stackoverflow.com/questions/66579693/check-if-a-song-has-ended-in-pygame
* https://www.makeuseof.com/build-music-player-using-python/
* https://stackoverflow.com/questions/6037826/finding-the-length-of-an-mp3-file
