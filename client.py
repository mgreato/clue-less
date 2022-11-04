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
    boolean = False
    diagonal_room_index = -1
    if locationIndex==1-1:
        diagonal_room_index = 9-1
        diagonal_room_name = roomsToNames[locations[diagonal_room_index]]
        boolean = True
    if locationIndex ==7-1:
        diagonal_room_index = 3-1
        diagonal_room_name = roomsToNames[locations[diagonal_room_index]]
        boolean = True
    if locationIndex==3-1:
        diagonal_room_index = 7-1
        diagonal_room_name = roomsToNames[locations[diagonal_room_index]]
        boolean = True
    if locationIndex==9-1:
        diagonal_room_index = 1-1
        diagonal_room_name = roomsToNames[locations[diagonal_room_index]]
        boolean = True
    return boolean, diagonal_room_name, locations[diagonal_room_index]


def movePlayer(p):
    if(p.playerLocation.__contains__("hallway")):
        print("player is in a hallway")
        print(p.playerLocation)
        hallwayRooms = p.playerLocation.split("hallway")[1]
        roomChoices = list(hallwayRooms)
        roomChoice1 = "room" + roomChoices[0]
        roomChoice2 = "room" + roomChoices[1]
        possibleRooms = []
        possibleRooms.append(roomChoice1)
        possibleRooms.append(roomChoice2)
        print(possibleRooms)
        print("Where would you like to move? Your choices are: " + str(possibleRooms))
    if(p.playerLocation.__contains__("room")):
        print("player is in a room")
        print(p.playerLocation)
        roomNumber = p.playerLocation.split("room")[1]
        possibleHallways = [h for h in locations if (("hallway" and roomNumber in h) and ("room" not in h))]
        
        #Check diagonal room option
        check_diagonal_result = can_take_secret_passage(p.locationIndex)
        if check_diagonal_result[0] == True:
            print("Where would you like to move? Your hallway choices are: " + str(possibleHallways) + ". Your diagonal room choice is: " + check_diagonal_result[2])
        else:
            print("Where would you like to move? Your choices are: " + str(possibleHallways))
    moveInput = input("->")
    s.send(moveInput.encode())
    clientsMessage = s.recv(1024).decode()
    print("CLIENTS MESSAGE BELOW")
    print(clientsMessage)
    return moveInput

def makeAccusation():
    print("Who would you like to accuse?")
    accusePersonInput = input("person ->")
    s.send(accusePersonInput.encode())
    accuseRoomInput = input("room ->")
    s.send(accuseRoomInput.encode())
    accuseWeaponInput = input("weapon ->")
    s.send(accuseWeaponInput.encode())
    clientsMessage = s.recv(1024).decode()
    print("CLIENTS MESSAGE BELOW")
    print(clientsMessage)
    # accusationMessage = s.recv(1024).decode()
    # print("accusationMessage BELOW")
    # print(accusationMessage)
    wonLostMessage = s.recv(1024).decode()
    print("9120389883013890101203818301")
    print(wonLostMessage)
    if "won" in wonLostMessage:
        print("You Won!")
        msg = "endConnection for all"
    if "lost" in wonLostMessage:
        print("You lost, your connection will now be ended")
        msg = "endConnection for player"
    return msg
    
# names, locations, and weapons that can be indexed. This code is identical in the server.py file
names = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
locations = ["room1", "room2", "room3", "room4", "room5", "room6", "room7", "room8", "room9",
            "hallway12", "hallway23", "hallway34", "hallway45", "hallway56", "hallway67",
            "hallway78", "hallway81", "hallway89", "hallway29", "hallway49", "hallway69"]
roomsToNames = {"room1": "study","room2": "hall","room3": "lounge", "room4": "dining room", 
            "room5": "kitchen", "room6": "ballroom", "room7": "conservatory", "room8": "library", "room9": "billiard room"}
weapons = ["rope", "candlestick", "dagger", "wrench", "lead pipe", "revolver"]

# initialize
port = 5050
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((socket.gethostname(), port))
form = 'utf-8'

# possible messages from server
CONNECTED_MSG = "Connection established"
BEGINNING_MSG = "Game is beginning"
TURN_MSG = "Next Turn"
CARDS_MSG = "Your cards are"
WIN_MSG = "You Win"
LOSE_MSG = "You Lose"
currentPlayer = 0

# receive message from server
while True:
    msg = s.recv(1024)
    readmsg = msg.decode(form)
    if CONNECTED_MSG in readmsg:
        print(readmsg, "\n")
        myNumber = int(readmsg[39])
    if BEGINNING_MSG in readmsg:
        print(readmsg)
        totalPlayers = int(readmsg[23])
        g = Game(totalPlayers)
        cards = readmsg.split("Your cards are: ")[1]
        p = Player(myNumber,names[myNumber],locations[myNumber], cards)
        print(p)
    # if CARDS_MSG in readmsg:
    #     print(readmsg, "\n")
    if TURN_MSG in readmsg:
        print(readmsg)
        if "Player "+str(p.playerNumber) in readmsg:
            playerMoveActive = True
            while playerMoveActive:
                currentPlayer = p.playerNumber
                print("my turn!")
                msg = "Please enter your move: "
                print(msg)
                message = input(" -> ")  # take input
                s.send(message.encode())

                choice = s.recv(1024).decode()
                print("^^^^^^$^$^@#*$)@#$*$)@*#&$*)#@$)#@*")
                print(choice)
                player_choice = choice[1:]
                # move1 = pygame.get_player_move(0)
                print("THE PLAYERS CHOICE IS: " + player_choice + "\n")
                # s.send(player_choice.encode(form))
            
                # THIS SECTION IS WHERE THE BULK OF THE GAME LOGIC SHOULD GO
            
                # player_choice = "end" #dummy options right now are move, suggest, accuse, end
                if player_choice == "move":
                    moveInput = movePlayer(p)
                    # NEED TO ADD VALIDATION FOR IF A HALLWAY IS OPEN
                    p.playerLocation = moveInput
                    msg = "\n MOVE " + p.playerName + " to " + p.playerLocation
                    s.send(msg.encode(form))

                elif player_choice == "suggest":
                    print("Who would you like to suggest?")
                    suggestPersonInput = input("person ->")
                    # s.send(suggestPersonInput.encode())
                    # NEED TO MOVE PLAYER TO THIS LOCATION
                    suggestRoomInput = p.playerLocation
                    # s.send(suggestRoomInput.encode())
                    suggestWeaponInput = input("weapon ->")
                    all = suggestPersonInput + "," + suggestRoomInput + "," + suggestWeaponInput
                    s.send(all.encode())
                    clientsMessage = s.recv(1024).decode()
                    print("CLIENTS MESSAGE BELOW")
                    print(clientsMessage)
                    msg = "\n SUGGEST " + suggestPersonInput + " in the " + suggestRoomInput + " with the " + suggestWeaponInput + "\n"
                    s.send(msg.encode(form))
                    

                elif player_choice == "accuse":
                    msg = makeAccusation()
                    s.send(msg.encode())
                    playerMoveActive = False
                elif player_choice == "end":
                    playerMoveActive = False
                    msg = "\n Turn Over."
                    s.send(msg.encode(form))
                print("&&&&&&&&&&&&&&&&&&&")
                print(playerMoveActive)
                print(msg)
        else:
            message = s.recv(1024).decode()
            playerNum = list(message)
            playerMoveChoice = message[1:]
            print("Player " + playerNum[0] + " chose to " + playerMoveChoice + "\n")
            if(playerMoveChoice == "move"):
                clientsMessage = s.recv(1024).decode()
                print("OTHER PLAYERS MESSAGE BELOW")
                print(clientsMessage)
            if(playerMoveChoice == "accuse"):
                clientsMessage = s.recv(1024).decode()
                print("OTHER PLAYERS CLIENT MESSAGE")
                print(clientsMessage)
                wonLostMessage = s.recv(1024).decode()
                playerNum = wonLostMessage.split("Player ")[1]
                if "won" in wonLostMessage:
                    print("Player " + playerNum + " won the game \n")
                if "lost" in wonLostMessage:
                    print("Player " + playerNum + " lost the game \n")
            if(playerMoveChoice == "suggest"):
                clientsMessage = s.recv(1024).decode()
                print("OTHER PLAYERS CLIENT MESSAGE")
                print(clientsMessage)

            print("not my turn!")
    if WIN_MSG in readmsg:
        pass # dummy right now
    if LOSE_MSG in readmsg:
        pass # dummy right now
