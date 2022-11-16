from operator import truediv
import pygame
import socket
from game import Game
from player import Player  
import ast

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
# playerStartLocations = {"Miss Scarlett": "hallway23", "Colonel Mustard": "hallway34", "Mrs. White": "hallway56", "Mr. Green": "hallway67",
#             "Mrs. Peacock": "hallway78", "Professor Plum": "hallway81"}
playerFirstLocations = {"Miss Scarlett": "hallway23", "Colonel Mustard": "hallway34", "Mrs. White": "hallway56", "Reverend Green": "hallway67",
        "Mrs. Peacock": "hallway78", "Professor Plum": "hallway81"}

# initialize
port = 5050
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((socket.gethostname(), port))
form = 'utf-8'
playerChosen = False

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

def movePlayer(p, otherPlayerLocations):
    otherPlayerLocationsList = [h for h in ast.literal_eval(otherPlayerLocations) if ("room" not in h)]
    playerInRoom = p.playerLocation.__contains__("room")
    if(playerInRoom):
        roomNumber = p.playerLocation.split("room")[1]
        possibleHallways = [h for h in locations if (("hallway" and roomNumber in h) and ("room" not in h) and (h not in otherPlayerLocationsList))]
        check_diagonal_result = can_take_secret_passage(p.playerLocation)
    if(p.playerLocation == "None"):
        possibleHallways = playerFirstLocations.get(p.playerName)
        print("Where would you like to move? Your first move must be to: " + str(possibleHallways))
    if(p.hasMoved == True):
        moveInput = "You can only move once per turn."
        print(moveInput)
        s.send(moveInput.encode())
        clientsMessage = s.recv(1024).decode()
    elif(playerInRoom) and (len(possibleHallways) == 0) and (check_diagonal_result[0] == False):
        moveInput = "Your move options are all blocked. You can either make an accusation or end your turn."
        print(moveInput)
        s.send(moveInput.encode())
        clientsMessage = s.recv(1024).decode()
        print(clientsMessage)
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
        if(playerInRoom):
            if check_diagonal_result[0] == True:
                if(len(possibleHallways) == 0):
                    print("Where would you like to move? Your only option is:  " + check_diagonal_result[1])
                else:
                    print("Where would you like to move? Your hallway choices are: " + str(possibleHallways) + ". Your diagonal room choice is: " + check_diagonal_result[1])
            else:
                print("Where would you like to move? Your choices are: " + str(possibleHallways))
        validMove = False
        while validMove == False:
            moveInput = input("->")
            if(moveInput not in otherPlayerLocationsList):
                validMove = True
            else:
                print("That room is already occupied, please enter another choice.")
        if("room" not in moveInput):
            p.hasSuggested = True   
            p.canEndTurn = True 
        moveMessage = moveInput + "," + p.playerName
        s.send(moveMessage.encode())
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
    print("Move " + suggestPersonInput + " to " + suggestRoomInput + ".\n")
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
    p.hasMoved = True
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
        print("You lost, you can no longer move or suggest.")
        msg = "endConnection for player"
    return msg

def validateSuggestion(p):
    if (roomsToNames.get(p.playerLocation) != None) and (p.hasSuggested == False) and (p.canSuggest == True):
        p.canSuggest = False
        return True
    else:
        return False

def validateEndTurn(p):
    if(p.canEndTurn == True):
        p.canSuggest = False
        return True
    else:
        return False

while True:
    msg = s.recv(1024)
    readmsg = msg.decode(form)
    if("CLOSE ALL CONNECTION" in readmsg):
        readmsg = readmsg.split(",")
        print(readmsg)
        if(readmsg[1]) and (int(readmsg[1]) == int(p.playerNumber)):
            print(readmsg[2])
        s.close()

    if CONNECTED_MSG in readmsg:
        myNumber = readmsg.split("You are Player ")[1].split(".")[0]
        if(int(myNumber) == 1):
            print(readmsg)
            print("How many players are going to be playing in the game?")
            numberOfPlayers = input("->")
            s.send(numberOfPlayers.encode())
            readmsg = s.recv(1024).decode()
        print(readmsg, "\n")
        message = input(" -> ")
        playerLocation = Game.playerStartLocations.get(message)
        p = Player(myNumber, message, playerLocation, None, False, False, False, False)
        sendMessage = p.playerName + "," + playerLocation
        s.send(sendMessage.encode())
        playerMessage = s.recv(1024).decode()
        print(playerMessage)
        readmsg = playerMessage

    if BEGINNING_MSG in readmsg:
        print(readmsg)
        cards = readmsg.split("Your cards are: ")[1]
        if("Next Turn" in cards):
            cards = cards.split("N")[0]
        setattr(p, 'cards', ast.literal_eval(cards))

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
                choiceInput = s.recv(1024).decode().split("//")
                choice = choiceInput[0]
                player_choice = choice[1:]
                if("," in player_choice):
                    player_choice = player_choice.split(",")[0]

                if player_choice == "move":
                    moveInput = movePlayer(p, choiceInput[1])
                    blockedOptions = (moveInput == "Your move options are all blocked. You can either make an accusation or end your turn.")
                    if(moveInput != "You can only move once per turn.") and ("room" not in moveInput) and (blockedOptions == False):
                        p.playerLocation = moveInput
                        msg = "\nMove " + p.playerName + " to " + p.playerLocation + "."
                        print(msg)
                    elif("room" in moveInput):
                        p.playerLocation = moveInput
                        print("\nMove " + p.playerName + " to " + p.playerLocation + ".")
                        msg = "Player must now suggest"
                        p.canEndTurn = False
                        p.hasSuggested = False
                        p.canSuggest = True
                        print(msg)
                    elif(moveInput != "You can only move once per turn.") and (blockedOptions == False):
                        msg = "Player cannot move again."
                    elif(blockedOptions):
                        msg = moveInput
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
                    if(msg == "endConnection for all"):
                        s.close()
                    playerMoveActive = False

                if player_choice == "end":
                    canTurnEnd = validateEndTurn(p)
                    if(canTurnEnd == True):
                        msg = "\nTurn Over. && " + str(p.canEndTurn)
                        s.send(msg.encode(form))
                        end = s.recv(1024).decode()
                        s.send("END".encode(form))
                        playerMoveActive = False
                    else:
                        if(p.canSuggest and not p.hasMoved):
                            msg = "\nYou must either move or make a suggestion. && " + str(p.canEndTurn)
                        if(p.canSuggest and p.hasMoved):
                            msg = "\nYou must make a suggestion. && " + str(p.canEndTurn)
                        if(not p.canSuggest and p.hasMoved):
                            msg = "\nYou must move to a new location. && " + str(p.canEndTurn)
                        if(not p.canSuggest and not p.hasMoved):
                            msg = "\nYou must move to a new location. && " + str(p.canEndTurn)
                        print(msg.split(" &&")[0])
                        s.send(msg.encode(form))
                        end = s.recv(1024).decode()
                        s.send("END".encode(form))
                        playerMoveActive = False

        else:
            if("is suggesting" in readmsg):
                playerMoveChoice = "nextSuggest"
            else:
                message = s.recv(1024).decode()
                playerNum = list(message)
                if("//" in message):
                    message = message.split("//")[0]
                playerMoveChoice = message[1:]
                if("," in playerMoveChoice):
                    playerMoveChoice = playerMoveChoice.split(",")[0]
            if(playerMoveChoice == "move"):
                clientsMessage = s.recv(1024).decode()
                if(clientsMessage != "Player cannot move again."):
                    print("\n" + clientsMessage)
                playerMoveActive = False
                p.hasMoved = False
            if(playerMoveChoice == "accuse"):
                clientsMessage = s.recv(1024).decode()
                wonLostMessage = s.recv(1024).decode()
                playerNum = wonLostMessage.split("Player ")[1]
                if "won" in wonLostMessage:
                    print("Player " + playerNum[0] + " chose to accuse and" + playerNum[1:] + "\n")
                    s.close()
                if "lost" in wonLostMessage:
                    print("Player " + playerNum[0] + " chose to accuse and" + playerNum[1:] + "\n")
            if(playerMoveChoice == "suggest") or (playerMoveChoice == "nextSuggest"):
                if(playerMoveChoice == "suggest"):
                    validationMessage = s.recv(1024).decode()
                else: 
                    validationMessage = readmsg
                if("cannot") in validationMessage:
                    playerMoveActive = False
                    message = s.recv(1024).decode()
                if("able to" in validationMessage) or ("suggesting" in validationMessage): 
                    if("///" in validationMessage):
                        clientsMessage = validationMessage
                    else:
                        clientsMessage = s.recv(1024).decode()
                    clientsMessageSplit = clientsMessage.split("///")
                    print(clientsMessageSplit[0])
                    suggestions = clientsMessageSplit[1].split(",")
                    nextPlayer = int(suggestions[3])
                    if(p.playerName == suggestions[0]):
                        keys = [k for k, v in roomsToNames.items() if v == suggestions[1]]
                        p.playerLocation = keys[0]
                        p.canSuggest = True
                    count = 0
                    if(int(p.playerNumber) == nextPlayer):
                        matches = []
                        playerCards = getattr(p, 'cards')
                        if((suggestions[0] in p.cards) or (suggestions[1] in p.cards) or (suggestions[2] in p.cards)):
                            count += 1
                            for i in suggestions:
                                if i in p.cards:
                                    matches.append(i)
                            print("You have a card to disprove an item in player " + str(playerNum[0]) + "'s suggestion. ")
                            print("Your options to show player " +str(playerNum[0]) + " are " + str(matches))
                            print("Which would you like to show?")
                            message = input(" -> ")
                            s.send(message.encode())
                        else:
                            count += 1
                            message = "No matches please move to next player"
                            s.send(message.encode())
                    nextMessage = "Move " + suggestions[0] + " to " + suggestions[1] + ".\n"
                    print(nextMessage)
                    playerMoveActive = False
            if(playerMoveChoice == "end"):
                player = message.split("//")[0].split(",")[1]
                message = s.recv(1024).decode()
                if(message == "True"):
                    print("Player " + player + " chose to end their turn.")
                playerMoveActive = False
            p.hasSuggested = False
            p.hasMoved = False

    if WIN_MSG in readmsg:
        pass # dummy right now
    if LOSE_MSG in readmsg:
        pass # dummy right now
