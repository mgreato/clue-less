from operator import truediv
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

def movePlayer(p):
    if(p.playerLocation.__contains__("hallway")):
        # print("player is in a hallway")
        # print(p.playerLocation)
        hallwayRooms = p.playerLocation.split("hallway")[1]
        roomChoices = list(hallwayRooms)
        roomChoice1 = "room" + roomChoices[0]
        roomChoice2 = "room" + roomChoices[1]
        possibleRooms = []
        possibleRooms.append(roomChoice1)
        possibleRooms.append(roomChoice2)
        # print(possibleRooms)
        print("Where would you like to move? Your choices are: " + str(possibleRooms))
    if(p.playerLocation.__contains__("room")):
        # print("player is in a room")
        # print(p.playerLocation)
        roomNumber = p.playerLocation.split("room")[1]
        possibleHallways = [h for h in locations if (("hallway" and roomNumber in h) and ("room" not in h))]
        # NEED TO ADD IN SUPPORT FOR DIAGONAL ROOMS
        print("Where would you like to move? Your choices are: " + str(possibleHallways))
    moveInput = input("->")
    s.send(moveInput.encode())
    clientsMessage = s.recv(1024).decode()
    # print("CLIENTS MESSAGE BELOW")
    # print(clientsMessage)
    return moveInput

def makeAccusation():
    print("Who would you like to accuse?")
    accusePersonInput = input("person ->")
    # s.send(accusePersonInput.encode())
    accuseRoomInput = input("room ->")
    # s.send(accuseRoomInput.encode())
    accuseWeaponInput = input("weapon ->")
    allAccusations = accusePersonInput + "," + accuseRoomInput + "," + accuseWeaponInput
    s.send(allAccusations.encode())
    clientsMessage = s.recv(1024).decode()
    # print("CLIENTS MESSAGE BELOW")
    # print(clientsMessage)
    # accusationMessage = s.recv(1024).decode()
    # print("accusationMessage BELOW")
    # print(accusationMessage)
    wonLostMessage = s.recv(1024).decode()
    # print("9120389883013890101203818301")
    # print(wonLostMessage)
    if "won" in wonLostMessage:
        print("You Won!")
        msg = "endConnection for all"
    if "lost" in wonLostMessage:
        print("You lost, your connection will now be ended")
        msg = "endConnection for player"
    return msg

def validateSuggestion(location):
    if roomsToNames.get(location) != None:
        return True
    else:
        return False
    
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
MOVE_MSG = "another"
SUGGESTION = "is suggesting "
CARDS_MSG = "Your cards are"
WIN_MSG = "You Win"
LOSE_MSG = "You Lose"
currentPlayer = 0

# receive message from server
while True:
    msg = s.recv(1024)
    readmsg = msg.decode(form)
    # print("PRINTiNG READ MESSAGE HERE")
    # print(readmsg)
    if CONNECTED_MSG in readmsg:
        # print(readmsg, "\n")
        myNumber = int(readmsg[39])
    if BEGINNING_MSG in readmsg:
        # print(readmsg)
        totalPlayers = int(readmsg[23])
        g = Game(totalPlayers)
        cards = readmsg.split("Your cards are: ")[1]
        p = Player(myNumber,names[myNumber],locations[myNumber], cards)
        # print(p)
    # if CARDS_MSG in readmsg:
    #     print(readmsg, "\n")
    print(readmsg)
    print(SUGGESTION)
    print(SUGGESTION in readmsg)
    if ((TURN_MSG or MOVE_MSG) in readmsg) or (SUGGESTION in readmsg):
        print("HERE!!!")
        suggestionValidation = None
        print("WE ARE IN THIS SPOT IN THE CODE!!!!!!!")
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
                    print("IN MOVE AND HERE IS MOVE INPUT")
                    print(moveInput)
                    # NEED TO ADD VALIDATION FOR IF A HALLWAY IS OPEN
                    p.playerLocation = moveInput
                    msg = "\nMOVE " + p.playerName + " to " + p.playerLocation
                    print(msg)
                    s.send(msg.encode(form))
                    playerMoveActive = False

                elif player_choice == "suggest":
                    suggestionValidation = validateSuggestion(p.playerLocation)
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    print(suggestionValidation)
                    if(suggestionValidation == True):
                        # serverSuggestionValidation = s.recv(1024).decode()
                        # print(serverSuggestionValidation)
                        print("Who would you like to suggest?")
                        suggestPersonInput = input("person ->")
                        # s.send(suggestPersonInput.encode())
                        # NEED TO MOVE PLAYER TO THIS LOCATION
                        suggestRoomInput = p.playerLocation
                        # s.send(suggestRoomInput.encode())
                        suggestWeaponInput = input("weapon ->")
                        all = suggestPersonInput + "," + suggestRoomInput + "," + suggestWeaponInput
                        print("HERE MAKING ALL MESSAGE")
                        s.send(all.encode())
                        empty = True
                        while empty == True:
                            clientsMessage = s.recv(1024).decode().split("///")[0]
                            # print("CLIENTS MESSAGE BELOW")
                            # print(clientsMessage)
                            if(clientsMessage != ""):
                                empty = False

                    # elif player_choice == "suggestHelp":
                        print("Waiting for suggestion help")
                        # suggestionHelpMessage = s.recv(1024).decode()
                        again = True
                        print(again)
                        while (again == True) and (clientsMessage != "No Matches for this client"):
                            suggestionHelpMessage = s.recv(1024).decode()
                            if((suggestionHelpMessage != "") or (suggestionHelpMessage != None)) and ("is suggesting" not in suggestionHelpMessage) and (("Next" not in suggestionHelpMessage)):
                                print(suggestionHelpMessage)
                                again = False
                        if(" ///" in suggestionHelpMessage):
                            suggestion = suggestionHelpMessage.split(" ///")[0]
                            print("SUGGESTION HELP MESSAGE BELOW")
                            print(suggestionHelpMessage)
                            print("Another player is suggesting that [" + suggestion + "] is not in the solution")
                        else:
                            suggestion = suggestionHelpMessage
                            print("SUGGESTION HELP MESSAGE BELOW")
                            print(suggestionHelpMessage)
                            print("No players had cards that matched your suggestion")
                        playerMoveActive = False
                        msg = "\n SUGGEST " + suggestPersonInput + " in the " + roomsToNames.get(suggestRoomInput) + " with the " + suggestWeaponInput + "\n"
                        s.send(msg.encode(form))
                    else:
                        print("You are not in a room so you cannot make a suggestion \n")
                        suggestionError = "Player cannot make a suggestion!!!! \n"
                        s.send(suggestionError.encode())
                        # message = s.recv(1024).decode()
                        # print("THIS IS A TEST")
                        # print(message)
                        # message = s.recv(1024).decode()
                        # print("THIS IS A TEST #2")
                        # print(message)
                        # s.send("suggestionOver".encode(form))
                        playerMoveActive = False

                elif player_choice == "accuse":
                    msg = makeAccusation()
                    s.send(msg.encode())
                    playerMoveActive = False
                elif player_choice == "end":
                    msg = "\n Turn Over."
                    s.send(msg.encode(form))
                    playerMoveActive = False
                print("&&&&&&&&&&&&&&&&&&&")
                print(playerMoveActive)
                # print(msg)
        else:
            if("is suggesting" in readmsg):
                playerMoveChoice = "nextSuggest"
            else:
                message = s.recv(1024).decode()
                playerNum = list(message)
                playerMoveChoice = message[1:]
                print("Player " + playerNum[0] + " chose to " + playerMoveChoice + "\n")
                print(playerMoveChoice)
            if(playerMoveChoice == "move"):
                clientsMessage = s.recv(1024).decode()
                print("OTHER PLAYERS MESSAGE BELOW")
                print(clientsMessage)
                playerMoveActive = False
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
            print("#########################################")
            print(suggestionValidation)
            print(playerMoveChoice)
            print(playerMoveChoice == "nextSuggest")
            if(playerMoveChoice == "suggest") or (playerMoveChoice == "nextSuggest"):
                if(playerMoveChoice == "suggest"):
                    validationMessage = s.recv(1024).decode()
                    print("OTHER PLAYERS VALIDATION MESSAGE")
                    print(validationMessage)
                else: 
                    print("IN THE ELSE STATEMENT")
                    print(readmsg)
                    validationMessage = readmsg
                    print(validationMessage)
                if("cannot") in validationMessage:
                    print("Player " + playerNum[0] + " is not in a location to suggest \n")
                    playerMoveActive = False
                    message = s.recv(1024).decode()
                    print("THIS IS A TEST")
                    print(message)
                    # suggestions = s.recv(1024).decode()
                print("suggesting" in validationMessage)
                if("able to" in validationMessage) or ("suggesting" in validationMessage): 
                    print("INSIDE THIS IF STATEMENT")
                    print(validationMessage)
                    # print(clientsMessage)
                    clientsMessage = ""
                    if("///" in validationMessage):
                        clientsMessage = validationMessage
                    else:
                        clientsMessage = s.recv(1024).decode()
                    print(clientsMessage)
                    print("OTHER PLAYERS CLIENT MESSAGE")
                    clientsMessageSplit = clientsMessage.split("///")
                    print(clientsMessageSplit[0])
                    suggestions = clientsMessageSplit[1].split(",")
                    print(suggestions)
                    print("PLAYER NUMBER MESSAGE")
                    print(p.playerNumber)
                    # currentPlayerNum = readmsg.split("Next Turn: Player ")[1].split(".")[0]
                    nextPlayer = int(suggestions[3])
                    print(nextPlayer)
                    # nextPlayer = int(currentPlayerNum) + 1
                    # print(nextPlayer)
                    count = 0
                    if(p.playerNumber == nextPlayer):
                        print("IN THIS IF STATEMENT")
                        print(p.cards)
                        print(suggestions[0])
                        print(suggestions[1])
                        print(suggestions[2])
                        matches = []
                        if((suggestions[0] in p.cards) or (suggestions[1] in p.cards) or (suggestions[2] in p.cards)):
                            count += 1
                            for i in suggestions:
                                print("IN FOR LOOP")
                                print(i)
                                if i in p.cards:
                                    matches.append(i)
                            print("You have a card to disprove an item in player " + str(playerNum[0]) + "'s suggestion. ")
                            print("Your options to show player " +str(playerNum[0]) + " are " + str(matches))
                            print("Which would you like to show?")
                            message = input(" -> ")  # take input
                            print("PlAYER SUGGESTION HELP MESSAGE HERE")
                            print(message)
                            s.send(message.encode())
                        else:
                            count += 1
                            message = "No matches please move to next player"
                            print(message)
                            print("INSIDE HERE AND AM SENDING THE NO MATCHES MESSAGE")
                            s.send(message.encode())
                    playerMoveActive = False
            

            print("not my turn!")
    if WIN_MSG in readmsg:
        pass # dummy right now
    if LOSE_MSG in readmsg:
        pass # dummy right now