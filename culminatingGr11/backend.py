import os
import glob
import json
import uuid
import hashlib
from tinytag import TinyTag

# User management
active = None

def writeUsersFile(users = {}):
    os.path.exists("data") or os.mkdir("data") # create data directory if non-existent
    with open("data/users.json", "w") as usersFile:
        json.dump(users, usersFile)

def register(username, password):
    global active

    # empty username or password
    if not (username and password):
        return "Username or password cannot be empty"

    # create file if non-existent
    os.path.exists("data/users.json") or writeUsersFile()

    users = {}
    with open("data/users.json", "r") as usersFile:
        users = json.load(usersFile)
    if username in users:
        return "Username already exists"
    
    users[username] = password
    writeUsersFile(users)

    # create the user's file structure
    os.makedirs("data/" + username + "/music")
    with open("data/" + username + "/user.json", "w") as userFile:
        json.dump({"music": {}, "playlists": {}}, userFile)
    active = username

    return "Registration successful"

def login(username, password):
    global active

    # check for users file
    if not os.path.exists("data/users.json"):
        return "Invalid username or password"

    with open("data/users.json", "r") as usersFile:
        users = json.load(usersFile)
    if not (username in users and users[username] == password):
        return "Invalid username or password"

    active = username
    return "Login successful"

def logout():
    global active
    active = None


# Music management
supportedFormats = ["mp3", "wav", "ogg", "flac"]

def importMusic(filePath):
    global active

    extension = filePath.split(".")[-1]
    if extension not in supportedFormats:
        return "Unsupported file format"

    # to avoid file name clashing, every file will be named its hash
    # all metadata will be stored in the user's json
    musicFile = open(filePath, "rb")
    musicData = musicFile.read()
    musicFile.close()
    id = hashlib.sha256(musicData).hexdigest()

    # check if already imported
    musicFiles = os.listdir("data/" + active + "/music")
    if id + extension in musicFiles:
        with open("data/" + active + "/user.json", "r") as userFile:
            userData = json.load(userFile)
        metadata = userData["music"][id]
        metadata["id"] = id
        return metadata

    metadata = TinyTag.get(filePath).as_dict()
    # strip unimportant metadata
    metadata = {key: val for key, val in metadata.items() if key in ["album", "artist", "comment", "composer", "duration", "genre", "title", "year"]}
    if metadata["title"] == None: # if the file has no title, use the file name
        metadata["title"] = str.join(".", os.path.basename(filePath).split(".")[:-1])
    
    # assign empty values to missing metadata
    for key in metadata:
        if key == "year":
            metadata[key] = -1
        if metadata[key] == None:
            metadata[key] = ""
        

    # copy the file to the user's music directory
    musicFile = open("data/" + active + "/music/" + id + "." + extension, "wb")
    musicFile.write(musicData)
    musicFile.close()

    # add the metadata to the user's json
    with open("data/" + active + "/user.json", "r") as userFile:
        userData = json.load(userFile)

    userData["music"][id] = metadata

    with open("data/" + active + "/user.json", "w") as userFile:
        json.dump(userData, userFile)

    metadata["id"] = id
    return metadata

def deleteMusic(id):
    global active

    # dereference the music from the user's json
    with open("data/" + active + "/user.json", "r") as userFile:
        userData = json.load(userFile)

    del userData["music"][id]

    with open("data/" + active + "/user.json", "w") as userFile:
        json.dump(userData, userFile)

    # delete the music file
    path = glob.glob("data/" + active + "/music/" + id + ".*")
    os.remove(path[0])
    
def importPlaylist(dirPath):
    global active
    
    # import all audio files in a directory
    # then create a playlist
    playlistData = {"music": []}

    playlistData["name"] = os.path.basename(dirPath)

    files = os.listdir(dirPath)
    for filePath in files:
        if not filePath.split(".")[-1] in supportedFormats:
            continue # skip non-audio files

        metadata = importMusic(os.path.join(dirPath, filePath))
        if type(metadata) == str:
            continue # failed to import file
        playlistData["music"].append(metadata["id"])

    with open("data/" + active + "/user.json", "r") as userFile:
        userData = json.load(userFile)

    userData["playlists"][str(uuid.uuid4())] = playlistData

    with open("data/" + active + "/user.json", "w") as userFile:
        json.dump(userData, userFile)


# Fetching music and playlists
def getUserData():
    global active

    with open("data/" + active + "/user.json", "r") as userFile:
        userData = json.load(userFile)

    # only return the music and playlists
    return {"music": userData["music"], "playlists": userData["playlists"]}