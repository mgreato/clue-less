from operator import truediv
import pygame
import socket
from game import Game
from player import Player  

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

# names, locations, and weapons that can be indexed. This code is identical in the server.py file
names = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
locations = ["room1", "room2", "room3", "room4", "room5", "room6", "room7", "room8", "room9",
            "hallway12", "hallway23", "hallway34", "hallway45", "hallway56", "hallway67",
            "hallway78", "hallway81", "hallway89", "hallway29", "hallway49", "hallway69"]
roomsToNames = {"room1": "study","room2": "hall","room3": "lounge", "room4": "dining room", 
            "room5": "kitchen", "room6": "ballroom", "room7": "conservatory", "room8": "library", "room9": "billiard room"}
weapons = ["rope", "candlestick", "dagger", "wrench", "lead pipe", "revolver"]
playerStartLocations = {"Miss Scarlett": "hallway23", "Colonel Mustard": "hallway34", "Mrs. White": "hallway56", "Mr. Green": "hallway67",
            "Mrs. Peacock": "hallway78", "Professor Plum": "hallway81"}

# initialize
port = 5050
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((socket.gethostname(), port))
form = 'utf-8'
playerChosen = False
# p = Player

# function definitions
def is_move_valid(): # dummy function for now
    pass

# def is_in_room(locationIndex):
#     if locationIndex > 0 and locationIndex < 9:
#         return true
#     return false

# def is_in_hallway(locationIndex):
#     if locationIndex > 8:
#         return true
#     return false

def can_take_secret_passage(playerRoom):
    boolean = False
    diagonal_room_name = ""
    if playerRoom == "room1":
        diagonal_room_name = "room5"
        boolean = True
    if playerRoom == "room3":
        diagonal_room_name = "room7"
        boolean = True
    if playerRoom== "room5":
        diagonal_room_name = "room1"
        boolean = True
    if playerRoom== "room7":
        diagonal_room_name = "room3"
        boolean = True
    return boolean, diagonal_room_name

def movePlayer(p):
    if(p.hasMoved == True):
        moveInput = "You can only move once per turn"
        print(moveInput)
        s.send(moveInput.encode())
        clientsMessage = s.recv(1024).decode()
    else:
        if(p.playerLocation.__contains__("hallway")):
            hallwayRooms = p.playerLocation.split("hallway")[1]
            roomChoices = list(hallwayRooms)
            roomChoice1 = "room" + roomChoices[0]
            roomChoice2 = "room" + roomChoices[1]
            possibleRooms = []
            possibleRooms.append(roomChoice1)
            possibleRooms.append(roomChoice2)
            print("Where would you like to move? Your choices are: " + str(possibleRooms))
        if(p.playerLocation.__contains__("room")):
            roomNumber = p.playerLocation.split("room")[1]
            possibleHallways = [h for h in locations if (("hallway" and roomNumber in h) and ("room" not in h))]
            check_diagonal_result = can_take_secret_passage(p.playerLocation)
            if check_diagonal_result[0] == True:
                print("Where would you like to move? Your hallway choices are: " + str(possibleHallways) + ". Your diagonal room choice is: " + check_diagonal_result[1])
            else:
                print("Where would you like to move? Your choices are: " + str(possibleHallways))
        moveInput = input("->")
        if("room" not in moveInput):
            p.hasSuggested = True   
            p.canEndTurn = True 
        s.send(moveInput.encode())
        clientsMessage = s.recv(1024).decode()
        p.hasMoved = True
    return moveInput

def handleSuggestion():
    print("Who would you like to suggest?")
    suggestPersonInput = input("person ->")
    suggestRoomInput = p.playerLocation
    suggestWeaponInput = input("weapon ->")
    all = suggestPersonInput + "," + suggestRoomInput + "," + suggestWeaponInput
    s.send(all.encode())
    empty = True
    while empty == True:
        clientsMessage = s.recv(1024).decode().split("///")[0]
        if(clientsMessage != ""):
            empty = False

    again = True
    while (again == True) and (clientsMessage != "No Matches for this client"):
        suggestionHelpMessage = s.recv(1024).decode()
        if((suggestionHelpMessage != "") or (suggestionHelpMessage != None)) and ("is suggesting" not in suggestionHelpMessage) and (("Next" not in suggestionHelpMessage)):
            again = False
    if(" ///" in suggestionHelpMessage):
        suggestion = suggestionHelpMessage.split(" ///")[0]
        print("Another player is suggesting that [" + suggestion + "] is not in the solution")
    else:
        suggestion = suggestionHelpMessage
        print("No players had cards that matched your suggestion")
    msg = "\n SUGGEST " + suggestPersonInput + " in the " + roomsToNames.get(suggestRoomInput) + " with the " + suggestWeaponInput + "\n"
    s.send(msg.encode(form))
    p.hasSuggested = True
    p.canEndTurn = True

def makeAccusation():
    print("Who would you like to accuse?")
    accusePersonInput = input("person ->")
    accuseRoomInput = input("room ->")
    accuseWeaponInput = input("weapon ->")
    allAccusations = accusePersonInput + "," + accuseRoomInput + "," + accuseWeaponInput
    s.send(allAccusations.encode())
    clientsMessage = s.recv(1024).decode()
    wonLostMessage = s.recv(1024).decode()
    if "won" in wonLostMessage:
        print("You Won!")
        msg = "endConnection for all"
    if "lost" in wonLostMessage:
        print("You lost, your connection will now be ended")
        msg = "endConnection for player"
    return msg

def validateSuggestion(p):
    if (roomsToNames.get(p.playerLocation) != None) and (p.hasSuggested == False):
        return True
    else:
        return False

def validateEndTurn(p):
    if(p.canEndTurn == True):
        return True
    else:
        return False

# def validatePlayer(name, number, cards):
#     playerLocation = Game.playerStartLocations.get(name)
#     global p
#     p = Player(number,name, playerLocation, cards, False, False, False)
#     return p.playerName, p.playerLocation, True

# receive message from server
while True:
    msg = s.recv(1024)
    readmsg = msg.decode(form)
    print("PRINTING READ MESSAGE HERE")
    print(readmsg)
    if CONNECTED_MSG in readmsg:
        print(readmsg, "\n")
        myNumber = readmsg.split("You are Player ")[1].split(".")[0]
        # while playerChosen == False:
        message = input(" -> ")
        playerLocation = Game.playerStartLocations.get(message)
        p = Player(myNumber, message, playerLocation, None, False, False, False)
        # p.playerName, p.playerLocation, True
        # playerName, playerLocation, validatePlayer = validatePlayer(message, myNumber, None)
        sendMessage = p.playerName + "," + playerLocation
        s.send(sendMessage.encode())
        playerMessage = s.recv(1024).decode()
        print("PRINTING")
        print(playerMessage)
        readmsg = playerMessage
    if BEGINNING_MSG in readmsg:
        print("IN BEGIN MESSAGE")
        print(readmsg)
        cards = readmsg.split("Your cards are: ")[1]
        setattr(p, 'cards', cards)
        print(p.cards)
    if ((TURN_MSG or MOVE_MSG) in readmsg) or (SUGGESTION in readmsg):
        suggestionValidation = None
        if "Player "+str(p.playerNumber) in readmsg:
            playerMoveActive = True
            while playerMoveActive:
                currentPlayer = p.playerNumber
                msg = "Please enter your move: "
                print(msg)
                message = input(" -> ")
                s.send(message.encode())

                choice = s.recv(1024).decode()
                player_choice = choice[1:]
                if player_choice == "move":
                    moveInput = movePlayer(p)
                    if(moveInput != "You can only move once per turn") and ("room" not in moveInput):
                        p.playerLocation = moveInput
                        msg = "\nMOVE " + p.playerName + " to " + p.playerLocation
                    elif("room" in moveInput):
                        p.playerLocation = moveInput
                        print("\nMOVE " + p.playerName + " to " + p.playerLocation)
                        msg = "Player must now suggest"
                        p.canEndTurn = False
                        p.hasSuggested = False
                    else:
                        msg = "Player cannot move again"
                    print(msg)
                    s.send(msg.encode(form))
                    playerMoveActive = False

                if player_choice == "suggest":
                    suggestionValidation = validateSuggestion(p)
                    if(suggestionValidation == True):
                        handleSuggestion()
                        playerMoveActive = False
                    else:
                        print("You are are not able to make a suggestion \n")
                        suggestionError = "Player cannot make a suggestion!!!! \n"
                        s.send(suggestionError.encode())
                        playerMoveActive = False

                if player_choice == "accuse":
                    msg = makeAccusation()
                    s.send(msg.encode())
                    playerMoveActive = False
                if player_choice == "end":
                    canTurnEnd = validateEndTurn(p)
                    if(canTurnEnd == True):
                        msg = "\n Turn Over. && " + str(p.canEndTurn)
                        s.send(msg.encode(form))
                        playerMoveActive = False
                    else:
                        msg = "\n You must either move or suggest. && " + str(p.canEndTurn)
                        s.send(msg.encode(form))
                        playerMoveActive = False
        else:
            if("is suggesting" in readmsg):
                playerMoveChoice = "nextSuggest"
            else:
                message = s.recv(1024).decode()
                playerNum = list(message)
                playerMoveChoice = message[1:]
                print("Player " + playerNum[0] + " chose to " + playerMoveChoice + "\n")
            if(playerMoveChoice == "move"):
                clientsMessage = s.recv(1024).decode()
                print(clientsMessage)
                playerMoveActive = False
                p.hasMoved = False
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
            if(playerMoveChoice == "suggest") or (playerMoveChoice == "nextSuggest"):
                # p.hasSuggested = False
                print("THERE WAS A SUGGESTION")
                if(playerMoveChoice == "suggest"):
                    validationMessage = s.recv(1024).decode()
                else: 
                    validationMessage = readmsg
                if("cannot") in validationMessage:
                    print("Player " + playerNum[0] + " is not in a location to suggest \n")
                    playerMoveActive = False
                    message = s.recv(1024).decode()
                if("able to" in validationMessage) or ("suggesting" in validationMessage): 
                    print("INSIDE THIS IF STATEMENT")
                    print(validationMessage)
                    # print(clientsMessage)
                    clientsMessage = ""
                    if("///" in validationMessage):
                        clientsMessage = validationMessage
                    else:
                        clientsMessage = s.recv(1024).decode()
                    # print(clientsMessage)
                    print("OTHER PLAYERS CLIENT MESSAGE")
                    clientsMessageSplit = clientsMessage.split("///")
                    # print("THIS IS A TEST TO SEE WHAT THIS IS")
                    # print(clientsMessageSplit)
                    print(clientsMessageSplit[0])
                    suggestions = clientsMessageSplit[1].split(",")
                    # print(suggestions)
                    # print("PLAYER NUMBER MESSAGE")
                    # print(p.playerNumber)
                    # currentPlayerNum = readmsg.split("Next Turn: Player ")[1].split(".")[0]
                    nextPlayer = int(suggestions[3])
                    print("NEXT PLAYER")
                    print(nextPlayer)
                    # nextPlayer = int(currentPlayerNum) + 1
                    # print(nextPlayer)
                    print(p.playerNumber)
                    count = 0
                    if(int(p.playerNumber) == nextPlayer):
                        print("IN THIS IF STATEMENT")
                        print(p.cards)
                        print(suggestions[0])
                        print(suggestions[1])
                        print(suggestions[2])
                        matches = []
                        print(p.cards)
                        # print(Player.cards)
                        playerCards = getattr(p, 'cards')
                        print("PRINTING PLAYER CARDS")
                        print(playerCards)
                        if((suggestions[0] in p.cards) or (suggestions[1] in p.cards) or (suggestions[2] in p.cards)):
                            count += 1
                            for i in suggestions:
                                # print("IN FOR LOOP")
                                # print(i)
                                if i in p.cards:
                                    matches.append(i)
                            print("You have a card to disprove an item in player " + str(playerNum[0]) + "'s suggestion. ")
                            print("Your options to show player " +str(playerNum[0]) + " are " + str(matches))
                            print("Which would you like to show?")
                            message = input(" -> ")  # take input
                            # print("PlAYER SUGGESTION HELP MESSAGE HERE")
                            # print(message)
                            s.send(message.encode())
                        else:
                            count += 1
                            message = "No matches please move to next player"
                            # print(message)
                            # print("INSIDE HERE AND AM SENDING THE NO MATCHES MESSAGE")
                            s.send(message.encode())
                    playerMoveActive = False
                p.hasSuggested = False
                p.hasMoved = False

            # print("not my turn!")
    if WIN_MSG in readmsg:
        pass # dummy right now
    if LOSE_MSG in readmsg:
        pass # dummy right now