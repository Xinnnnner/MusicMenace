import os
import glob
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import pygame
import time
from ttkthemes import ThemedTk
#Don't know why they may be underlined, by they work and that's all that matters

import backend #Refrencing the backend file

root = ThemedTk()
pygame.init()
currentFrame = None
# Setup window parameters
root.title("Music Menace")
root.resizable(True, True)
s = ttk.Style()
s.theme_use("xpnative")
s.configure(".", font=("Helevetica", 20))
s.configure("TButton", font=("Helevetica", 12))

def loginScreen():
    root.geometry("1080x720")
    root.minsize(720, 720)

    # Create the login screen
    loginFrame = ttk.Frame(root)
    loginFrame.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor="center")

    # Labels
    loginLabel = ttk.Label(loginFrame, text="Login")
    loginLabel.place(relx=0.5, rely=0.1, relwidth=0.5, relheight=0.1, anchor="center")

    # Fields
    usernameEntry = tk.Entry(loginFrame, font=("Courier", 20))
    usernameEntry.place(relx=0.5, rely=0.3, relwidth=0.5, relheight=0.1, anchor="center")
    passwordEntry = tk.Entry(loginFrame, font=("Courier", 20))
    passwordEntry.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.1, anchor="center")

    # Buttons
    loginButton = ttk.Button(loginFrame, text="Login", 
        command=lambda: login(usernameEntry.get(), passwordEntry.get()))
    loginButton.place(relx=0.5, rely=0.7, relwidth=0.5, relheight=0.1, anchor="center")
    registerButton = ttk.Button(loginFrame, text="Register",
        command=lambda: register(usernameEntry.get(), passwordEntry.get()))
    registerButton.place(relx=0.5, rely=0.85, relwidth=0.5, relheight=0.1, anchor="center")

    return loginFrame

def mainScreen():
    root.geometry("1080x720")
    root.minsize(720, 720)

    # Create the main screen
    mainFrame = ttk.Frame(root)
    mainFrame.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor="center")

    # Labels
    mainLabel = ttk.Label(mainFrame, text="Music Menace")
    mainLabel.place(relx=0.45, rely=0, relwidth=0.5, relheight=0.1)

    # Gif
    frameCnt = 36 #36 frames within the gif, will loop through them all.
    frames = [PhotoImage(file='hutaoyao.gif',format = 'gif -index %i' %(i)) for i in range(frameCnt)]
    def update(ind):

        frame = frames[ind]
        ind += 1
        if ind == frameCnt:
            ind = 0
        label.configure(image=frame)
        root.after(60, update, ind)
    label = Label(root)
    label.place(relx=0.7, rely=0.85)
    root.after(0, update, 0)



    # Buttons
    importMusicButton = ttk.Button(mainFrame, text="Import Music",
        command=lambda: importMusic())
    importMusicButton.place(relx=0.5, rely=0.9, relwidth=0.35, relheight=0.05, anchor="center")
    importMusicButton = ttk.Button(mainFrame, text="Import Playlist",
        command=lambda: importPlaylist())
    importMusicButton.place(relx=0.5, rely=0.95, relwidth=0.35, relheight=0.05, anchor="center")
    logoutButton = ttk.Button(mainFrame, text="Logout",
        command=lambda: logout())
    logoutButton.place(relx=0.9, rely=0.95, relwidth=0.15, relheight=0.05, anchor="center")

    # Player controls
    global playButton, pauseButton
    playButton = ttk.Button(mainFrame, text="Play",
        command=lambda: playMusic(playButton, pauseButton))
    playButton.place(relx=0.15, rely=0.9, relwidth=0.15, relheight=0.05, anchor="center")
    pauseButton = ttk.Button(mainFrame, text="Pause",
        command=lambda: pauseMusic(pauseButton))
    pauseButton.place(relx=0.15, rely=0.95, relwidth=0.15, relheight=0.05, anchor="center")
    delButton = ttk.Button(mainFrame, text="DELETE",
        command=lambda: delMusic())
    delButton.place(relx=0.15, rely=0.05, relwidth=0.15, relheight=0.05, anchor="center")

    # Music list
    global userData
    userData = backend.getUserData()

    sortingOptions = ["Title", "Artist", "Album", "Genre", "Year", "Duration"]
    sortingOption = StringVar(root, sortingOptions[0])
    sortingOptionMenu = ttk.OptionMenu(mainFrame, sortingOption, *sortingOptions,
        command=lambda option: setSortingOption(option))
    sortingOptionMenu.place(relx=0.35, rely=0.05, relwidth=0.15, relheight=0.05, anchor="center")

    createMusicList(mainFrame, userData["music"]) #Initializing the music list with the pre-existing user data

    # Volume slider
    volumeSlider = Scale(mainFrame, from_=0, to=100, orient=HORIZONTAL, command=lambda value: setVolume(value), variable=IntVar(root, 50))
    volumeSlider.place(relx=0.825, rely=0.05, relwidth=0.3, relheight=0.07, anchor="center")

    #Time slider
    global timeSlider #Global so it can be changed by functions
    timeSlider = Scale(mainFrame, from_=0, to=1, orient=HORIZONTAL, command=lambda value: timeSlide(value), variable=IntVar(root, 0))
    timeSlider.place(relx=0.5, rely=0.85, relwidth=0.4, relheight=0.05, anchor="center")



    

    return mainFrame


# Music list
musicListIds = []
musicListUi = None
def createMusicList(parent, musicList):
    global musicListUi, musicListIds
    if musicListUi != None:
        musicListUi.destroy() #recreates music list if one already exists
    musicListIds = []

    if parent == None:
        parent = currentFrame

    list = tk.Listbox(parent, font=("Courier", 20))
    list.place(relx=0.5, rely=0.475, relwidth=0.95, relheight=0.70, anchor="center")
    for id in musicList:
        list.insert(END, musicList[id]["title"])
        musicListIds.append(id) #adds the song into the list box as well as the list of ids.

    musicListUi = list

def setSortingOption(option):
    global userData, musicListIds

    option = option.lower() #Makes all of the options lowercased so they can be processed

    musicList = {}
    for id in musicListIds:
        musicList[id] = userData["music"][id]

    # sorts depending on the user's option
    sortedMusic = sorted(musicList.items(), key=lambda x: x[1][option])

    createMusicList(currentFrame, dict(sortedMusic))

#Volume Slider
def setVolume(value):
     pygame.mixer.music.set_volume(int(value) / 100)
#Time slider
def timeSlide(value):
    global timeSlider, currentTime, isPaused, manualStop
    if currentTime == int(timeSlider.get()) or isPaused == True or manualStop == True:
         return
    pygame.mixer.music.play(start = int(value))

#Sets playlist
def setPlaylist():
    createMusicList(currentFrame, userData["music"])

#Communicates with backend to import music
def importMusic():
    global userData
    supportedFormats = []
    for format in backend.supportedFormats: #grabs supported formats from backend
        supportedFormats.append("*." + format)
    selected = filedialog.askopenfilename(filetypes=[("Music Files", supportedFormats)])
    if selected:
        backend.importMusic(selected) #imports with backend
        userData = backend.getUserData() #refresh user data
        setPlaylist()

#Imports all of the songs within a folder
def importPlaylist():
    global userData
    selected = filedialog.askdirectory(initialdir=os.path.expanduser("~"), mustexist=True, title="Select a playlist folder")
    if selected:
        backend.importPlaylist(selected) #imports with backend and refreshes user data just like aboce.
        userData = backend.getUserData()
        setPlaylist()

MUSIC_END = pygame.USEREVENT+1
pygame.mixer.music.set_volume(0.5) #default volume at half
isPlaying = False
manualStop = False

#Plays and stops music depending on the state of the player
def playMusic(playButton, pauseButton):
    global musicListUi, isPlaying, isPaused, manualStop, currentTime, timeSlider, userData

    if isPlaying:
        pygame.mixer.music.stop()
        manualStop = True
        currentTime = 0
        timeSlider.set(0) #clears slider value
        playButton.config(text="Play")
        pauseButton.config(text="Pause") #changes the button text depending on state
        isPlaying = False
        isPaused = False
        return

    selected = musicListUi.curselection()
    #Plays seletected music, paths grabbed wtih backend.
    if selected:
        resolvedFilePath = glob.glob("data/" + backend.active + "/music/" + musicListIds[selected[0]] + ".*")
        pygame.mixer.music.load(resolvedFilePath[0])
        pygame.mixer.music.play()
        playButton.config(text="Stop")
        pauseButton.config(text="Pause")
        isPlaying = True
        isPaused = False
        global duration
        userData = backend.getUserData()
        duration = userData["music"][musicListIds[selected[0]]]["duration"] #gets the duration of the song
        playTime()
        pygame.mixer.music.set_endevent(MUSIC_END)

#Calculates time, runs every second.
def playTime():
    global currentTime, timeSlider, isPaused,duration, manualStop, isPlaying
    if manualStop == True or isPlaying == False:
        return
    currentTime = int(pygame.mixer.music.get_pos()/1000)
    timeSlider.config(to=duration) #the highest value of the slider will always be the value of the duration
    if int(timeSlider.get()) == int(duration): #set slider to 0 once the song is done
        timeSlider.set(0)
    elif isPaused == True: #Stops running if music isn't playing
        pass

    #moves the slider along as long as the songs are playing
    elif int(timeSlider.get()) == currentTime:
        timeSlider.set(currentTime)
    else:
        timeSlider.set(int(timeSlider.get())+1)
    root.after(1000, playTime)

isPaused = False
#Pauses and resumes music
def pauseMusic(uiButton):
    global isPaused, manualStop
    if isPaused:
        pygame.mixer.music.unpause()
        uiButton.config(text="Pause")
    else: #Changes button text depending on the state
        pygame.mixer.music.pause()
        uiButton.config(text="Resume")

    isPaused = not isPaused

#Plays next song once the current song is done
def musicStopped():
     global musicListUi, isPlaying, playButton, pauseButton, manualStop, timeSlider
     playButton.config(text="Play")
     timeSlider.set(0) #resets back to 0
     isPlaying = False

     if manualStop:
         manualStop = False
         return

     # Get the next song, by incrementing the current selection
     selected = musicListUi.curselection()
     if selected:
         selected = selected[0] + 1
         if selected >= len(musicListIds):
             selected = 0
         musicListUi.selection_clear(0, END)
         musicListUi.selection_set(selected)

         playMusic(playButton, pauseButton)

#Deletes music from the user's database
def delMusic():
    global musicListUi, userData
    selected = musicListUi.curselection()
    if selected:
        backend.deleteMusic(musicListIds[selected[0]])
        userData = backend.getUserData()
        print(userData)
        setPlaylist()

        pygame.mixer.music.set_endevent(MUSIC_END)

#Login function, works with backend and displays different things depending on authentication.
def login(username, password):
    message = backend.login(username, password)
    if message == "Login successful":
        global currentFrame
        currentFrame.destroy()
        currentFrame = mainScreen()
    else:
        messagebox.showerror("Error", message)


#Creates a new account and directory in the database
def register(username, password):
    message = backend.register(username, password)
    if message == "Registration successful":
        global currentFrame
        currentFrame.destroy()
        currentFrame = mainScreen()
    else:
        messagebox.showerror("Error", message)

#Logs out of the current account and returns to login screen.
def logout():
    backend.logout()
    global currentFrame

    # stop music
    pygame.mixer.music.stop()

    currentFrame.destroy()
    currentFrame = loginScreen()

#Checks whether or not the song is done.
def checkEvents():
    for event in pygame.event.get():
        if event.type == MUSIC_END:
            musicStopped()

    root.after(50, checkEvents) #constantly ran to check state
checkEvents()

currentFrame = loginScreen()
root.mainloop()