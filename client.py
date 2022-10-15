import pygame
import socket
from game import Game
from player import Player  

# function definitions
def is_move_valid(): # dummy function for now
    pass

def is_in_room(locationIndex):
    if locationIndex > 0 and locationIndex < 9:
        return true
    return false

def is_in_hallway(locationIndex):
    if locationIndex > 8:
        return true
    return false

def can_take_secret_passage(locationIndex):
    if locationIndex==1-1 or locationIndex ==7-1 or locationIndex==3-1 or locationIndex==9-1:
        return true
    return false
    
# names, locations, and weapons that can be indexed. This code is identical in the server.py file
names = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
locations = ["room1", "room2", "room3", "room4", "room5", "room6", "room7", "room8", "room9",
              "hallway12", "hallway23", "hallway14", "hallway25", "hallway36", "hallway45",
              "hallway56", "hallway47", "hallway58", "hallway69", "hallway78", "hallway89"]
weapons = ["rope", "candlestick", "dagger", "wrench", "lead pipe", "revolver"]
  
# initialize
port = 5000
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((socket.gethostname(), port))
form = 'utf-8'

# possible messages from server
CONNECTED_MSG = "Connection established"
BEGINNING_MSG = "Game is beginning"
TURN_MSG = "Next Turn"
WIN_MSG = "You Win"
LOSE_MSG = "You Lose"
  
# receive message from server
while True:
    msg = s.recv(1024)
    readmsg = msg.decode(form)
    if CONNECTED_MSG in readmsg:
        print(readmsg, "\n")
        myNumber = int(readmsg[39])
        p = Player(myNumber,names[myNumber],locations[myNumber])
    if BEGINNING_MSG in readmsg:
        print(readmsg)
        totalPlayers = int(readmsg[23])
        g = Game(totalPlayers)
    if TURN_MSG in readmsg:
        print(readmsg)
        if "Player "+str(p.playerNumber) in readmsg:
            print("my turn!")
            
            # THIS SECTION IS WHERE THE BULK OF THE GAME LOGIC SHOULD GO
            
            player_choice = "end" #dummy options right now are move, suggest, accuse, end
            if player_choice == "move":
                msg = "MOVE [character] to [location]"
            elif player_choice == "suggest":
                msg = "SUGGEST [character] in [location] with [weapon]"
            elif player_choice == "accuse":
                msg = "ACCUSE [character] in [location] with [weapon]"
            elif player_choice == "end":
                msg = "Turn Over."
            s.send(msg.encode(form))
        else:
            print("not my turn!")
    if WIN_MSG in readmsg:
        pass # dummy right now
    if LOSE_MSG in readmsg:
        pass # dummy right now