import pygame
import socket
from game import Game
from player import Player
import random
  
# initialize
port = 5000
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((socket.gethostbyname(socket.gethostname()),port))
s.listen(6) # this sets the max number of players
print("Server Started. Waiting for a connection.")
numPlayers = 0 # this is the current number of players
currentPlayer = 0
winner = 0
clients = []
addresses = []
form = 'utf-8'

# function definitions
def who_plays_next(currentPlayer, numPlayers):
    if currentPlayer==0:
        return 1
    if currentPlayer==numPlayers:
        return 1
    return currentPlayer+1
    
def send_message(msg,clients): # sends to ALL clients
    for i in clients:
        i.send(msg.encode(form))

# server picks a solution (name, location, weapon)
names = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
locations = ["room1", "room2", "room3", "room4", "room5", "room6", "room7", "room8", "room9",
              "hallway12", "hallway23", "hallway14", "hallway25", "hallway36", "hallway45",
              "hallway56", "hallway47", "hallway58", "hallway69", "hallway78", "hallway89"]
weapons = ["rope", "candlestick", "dagger", "wrench", "lead pipe", "revolver"]
solutionName = random.choice(names)
solutionLocation = random.choice(locations)
solutionWeapon = random.choice(weapons)

# possible messages from clients
MOVE_MSG = "MOVE"
SUGGESTION_MSG = "SUGEGEST"
ACCUSATION_MSG = "ACCUSE"
END_MSG = "Turn Over"
  
while True:
    # when client connects
    c, addr = s.accept()
    clients.append(c)
    addresses.append(addr)
    print("Connection from: ", str(addr))
    numPlayers = numPlayers+1
    print("Number of Players: ", numPlayers,"\n")
    msg = "Connection established. You are Player "+str(numPlayers)+"."
    c.send(msg.encode(form))
    
    # when all clients are connected, the game begins
    if numPlayers==3: # need to update this so numPlayers == 6 or some timeout function
        send_message("Game is beginning with "+str(numPlayers)+" players.",clients)
        
        #also, need to send each client what their cards are
        #so logic here to shuffle & divide cards, then send cards to client
        
        testCounter = 0 # delete this when while loop implemented properly
        numTurnsTested = 9 # delete this when while loop implemented properly
        currentPlayer = who_plays_next(currentPlayer, numPlayers)
        while winner==0:
            testCounter = testCounter+1 # delete this when while loop implemented properly
            print("current player: ", currentPlayer)
            msg = "Next Turn: Player "+str(currentPlayer)+"."
            for i in clients:
               i.send(msg.encode(form))
               
            # wait to receive messages from clients          
            msg = clients[currentPlayer-1].recv(1024)
            readmsg = msg.decode(form)
            print(f"[{addr}] {msg}")
            
            # message received from client, now must be sent to all clients or handled
            if MOVE_MSG in readmsg:
                send_message(readmsg,clients)
            if SUGGESTION_MSG in readmsg:
                send_message(readmsg,clients)
            if ACCUSATION_MSG in readmsg:
                send_message(readmsg,clients)
            if END_MSG in readmsg:
                currentPlayer = who_plays_next(currentPlayer, numPlayers)
            
            if testCounter == numTurnsTested: # delete this when while loop implemented properly
                winner = 1 # delete this when while loop implemented properly
           
        
