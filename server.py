import pygame
import socket
from game import Game
from player import Player
import pickle
  
# initialize
port = 5000
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((socket.gethostname(), port))
s.listen(6) # this sets the max number of players
print("Server Started. Waiting for a connection.")
numPlayers = 0 # this is the current number of players
currentPlayer = 0
winner = 0

def who_plays_next(currentPlayer, numPlayers):
    if currentPlayer==0:
        return 1
    if currentPlayer==numPlayers:
        return 1
    return currentPlayer+1

clients = []

# here, server picks a solution - so a person, weapon, and room
  
while True:
    # when client connects
    c, addr = s.accept()
    clients.append(c)
    print(clients)
    print("Connection from: ", str(addr))
    numPlayers = numPlayers+1
    print("Number of Players: ", numPlayers,"\n")
    msg = "Connection Established. You are Player "+str(numPlayers)+"."
    c.send(msg.encode())
    
    # when all clients are connected, the game begins
    if numPlayers==2: # need to update this so numPlayers == 6 or some timeout function
        msg = "Game is beginning with "+str(numPlayers)+" players."
        for i in clients:
            i.send(msg.encode())
        
        while winner==0:
            currentPlayer = who_plays_next(currentPlayer, numPlayers)
            print("current player: ", currentPlayer)
            msg = "Next Turn: Player "+str(currentPlayer)+"."
            for i in clients:
               i.send(msg.encode())
           
            msg = clients[currentPlayer-1].recv(1024)
            readmsg = msg.decode()
            print("Received.")
            # you received response from a client that you have to do something with
            msgConfirmation = "Player "+str(currentPlayer)+" has completed his/her turn."
            for i in clients:
                i.send(msgConfirmation.encode())
        
        # now the server has to interpret the move that the player made
        # if it's a movement, relay that movement to all clients
        # if it's a suggestion, get info from clients - this can be automatic without user interaction
        # if it's an accusation - see if it's right; if so, declare winner and loosers (if not, just make that player lose)
        # if string contains "Turn Over", then go back to the top of the while loop
           
        
