import pygame
import socket
from game import Game
from player import Player
import pickle
  
def is_move_valid(): # dummy function for now
    return true  

names = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
#locations = ["room1", "room2", "room3", "room4" ... ] or however we want to code this up
  
# initialize
port = 5000
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((socket.gethostname(), port))
  
# receive message from server
i = 0
while True:
    msg = s.recv(1024)
    readmsg = msg.decode()
    if "Connection Established" in readmsg:
        print(readmsg, "\n")
        myNumber = int(readmsg[39])
        p = Player(myNumber,names[myNumber])
    if "Game is beginning" in readmsg:
        print(readmsg, "\n")
        totalPlayers = int(readmsg[23])
        g = Game(totalPlayers)
    if "Next Turn" in readmsg:
        print(readmsg, "\n")
        if str(p.playerNumber) in readmsg:
            print("my turn!")
            #then I take my turn
            #if I move, then msg = something like "MOV character, new location"
            #if I make a suggestion, then msg = something like "SUG weapon, etc."
            #if I make an accusation, then msg = something like "ACU weapon, etc."
            msg = "dummy text"
            s.send(msg.encode())
        else:
            print("not my turn!")
    if "You Win" in readmsg:
        # display wind screen
        s.close()
    
    if "You Loose" in readmsg:
        # display lose screen
        s.close()