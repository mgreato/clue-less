import pygame
import socket
from game import Game
from player import Player
import random
import itertools, random
import time

# initialize
port = 5050
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
activePlayerNumbers = []
numberOfPlayers = 0
numPlayersExpected = 10000

def goto(linenum):
    global line
    line = linenum

def who_plays_next(currentPlayer, allPlayers):
    if(len(activePlayerNumbers) == 0):
        print("Game is over for all players")
    else:
        if allPlayers:
            if currentPlayer==0:
                return 1
            elif currentPlayer == numPlayers:
                return 1
            return currentPlayer+1
        else:
            if currentPlayer==0:
                return 1
            if currentPlayer == activePlayerNumbers[-1]:
                return activePlayerNumbers[0]
            else:
                index = activePlayerNumbers.index(currentPlayer)
                return activePlayerNumbers[index+1]

def send_message(msg,clients): 
    for i in clients:
        i.send(msg.encode(form))

names = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
locations = ["room1", "room2", "room3", "room4", "room5", "room6", "room7", "room8", "room9",
            "hallway12", "hallway23", "hallway14", "hallway25", "hallway36", "hallway45",
            "hallway56", "hallway47", "hallway58", "hallway69", "hallway78", "hallway89"]
roomsToNames = {"room1": "study","room2": "hall","room3": "lounge", "room4": "dining room", 
            "room5": "kitchen", "room6": "ballroom", "room7": "conservatory", "room8": "library", "room9": "billiard room"}
rooms = ["study","hall","lounge","dining room","kitchen", "ballroom", "conservatory", "library", "billiard room"]
weapons = ["rope", "candlestick", "dagger", "wrench", "lead pipe", "revolver"]

cards = names + rooms + weapons
solution = {}
solutionName = random.choice(names)
solution["Person"] = solutionName
solutionLocation = random.choice(rooms)
solution["Room"] = solutionLocation
solutionWeapon = random.choice(weapons)
solution["Weapon"] = solutionWeapon
print("The game solution is: " + str(solution))

cards.remove(solutionName)
cards.remove(solutionLocation)
cards.remove(solutionWeapon)

MOVE_MSG = "move"
SUGGESTION_MSG = "suggest"
ACCUSATION_MSG = "accuse"
END_MSG = "end"
gameOn = True
g = Game(0)

lastMove = ""

while gameOn:
    # when client connects
    c, addr = s.accept()
    clients.append(c)
    addresses.append(addr)
    print("Connection from: ", str(addr))
    numPlayers = numPlayers+1
    print("Number of Players: ", numPlayers,"\n")
    g.numPlayers = numPlayers
    msg = "\nConnection established. You are Player "+str(numPlayers)
    if(numPlayers == 1):
        c.send(msg.encode(form))
        numPlayersExpected = int(c.recv(1024).decode())
        availablePlayers = [name for name in g.playerNames if name not in g.chosenPlayers]
        playerChoice = "\nWhat player would you like to be? Your choices are " + str(availablePlayers)
    else: 
        availablePlayers = [name for name in g.playerNames if name not in g.chosenPlayers]
        playerChoice = msg + ".\nWhat player would you like to be? Your choices are " + str(availablePlayers)
    activePlayerNumbers.append(numPlayers)
    availablePlayers = [name for name in g.playerNames if name not in g.chosenPlayers]
    c.send(playerChoice.encode(form))
    playerInfo = c.recv(1024).decode().split(",")
    players = g.chosenPlayers
    players.append(playerInfo[0])
    g.chosenPlayers = players
    initialMessage = ("\nYou are " + playerInfo[0] + ".\n")
    c.send(initialMessage.encode(form))
    

    if numPlayers == numPlayersExpected:
        random.shuffle(cards)
        hands = [[] for player in range(numPlayers)]

        for x in range(len(cards)):
            for hand in hands:
                if(bool(cards)):
                    card = cards.pop(0)
                    hand.append(card)

        playersCount = 0
        for i in clients:
            msg = "\nGame is beginning with "+str(numPlayers)+" players. \n \nYour cards are: " + str(hands[playersCount]) + "\n"
            playersCount += 1
            i.send(msg.encode(form))

        currentPlayer = who_plays_next(currentPlayer, False)
        while winner==0:
            print("Current player: ", currentPlayer)
            print("UP HERE")
            msg = "\nNext Turn: Player "+str(currentPlayer)+". |||||" +  str(list(g.playerLocations.values()))
            send_message(msg, clients)

            playerTurn = True
            while playerTurn:
                moveMsg = clients[currentPlayer-1].recv(1024)
                playerMoveMsg = str(currentPlayer) + "..." +  moveMsg.decode(form) + "//" + str(list(g.playerLocations.values()))
                print("PLAYER TURN MOVE MESSAGE HERE IN SERVER")
                print(playerMoveMsg)

                if "KEEP SAME PLAYER TURN" in moveMsg.decode(form):
                    currentPlayer = currentPlayer
                    playerTurn = False

                if (MOVE_MSG in playerMoveMsg) or ("moving" in playerMoveMsg):
                    print("IN MOVING THIS IS THE PLAYER MOVE MSG")
                    print(playerMoveMsg)
                    movePlayer = playerMoveMsg.split("...")[1].split("---")[1]
                    print("MOVE PLAYER")
                    print(movePlayer)
                    moveChoice = playerMoveMsg.split("...")[1].split("---")[2].split("//")[0]
                    print("MOVE CHOICE")
                    print(moveChoice)
                    g.playerLocations[movePlayer] = moveChoice
                    moveMessage = str(movePlayer) + " is moving to " + str(moveChoice) + "."
                    print(moveMessage)
                    send_message(moveMessage, clients)
                    currentPlayer = currentPlayer
                    playerTurn = False
                    
                if SUGGESTION_MSG in playerMoveMsg:
                    print("INSIDE SUGGESTION")
                    print(playerMoveMsg)
                    print("PRINTING SUGGESTION MESSAGE HERE")
                    suggestionMessage = playerMoveMsg.split("//")[0].split("!!!")[1]
                    print(suggestionMessage)
                    clientsToValidate = []
                    clientsToValidate.extend(clients)
                    clientsToValidate.pop(currentPlayer-1)
                    # send_message(goodSuggestion, clientsToValidate)
                    suggestion = suggestionMessage.split(",")
                    print("HERE!!!!!!!s")
                    person = suggestion[0]
                    room = roomsToNames.get(suggestion[1])
                    weapon = suggestion[2]
                    playerToPass = who_plays_next(currentPlayer, True)
                    suggestionHelpMade = False
                    playerSuggest = currentPlayer
                    suggestCheckCount = 0
                    while (suggestionHelpMade != True):
                        suggestionPass = person + " in the " + room + " with the " + weapon
                        printMessage = "Player " + str(currentPlayer) + " is suggesting " + suggestionPass + ".\n"
                        print(printMessage)
                        suggestionMessage = printMessage + " ///"
                        if(playerSuggest == numPlayers):
                            fullSuggestion = person + "," + room + "," + weapon + "," + str(1)
                        else:
                            fullSuggestion = person + "," + room + "," + weapon + "," + str(playerSuggest+1)
                        print("SUGGESTION MESSAGE PLUS FULL SUGGESTION BELOW")
                        print(suggestionMessage + fullSuggestion)
                        send_message(suggestionMessage + fullSuggestion, clients)

                        g.playerLocations[person] = suggestion[1]
                        print("HERE")
                        print(playerSuggest)
                        print(numPlayers)
                        print(suggestCheckCount)
                        if(playerSuggest == numPlayers) and (suggestCheckCount != numPlayers-1): 
                            print("THIS IS THE PART FOR A PLAYER TO SUGGEST")
                            suggestionHelp = clients[0].recv(1024).decode()
                        else:
                            if(suggestCheckCount == numPlayers-1):
                                noSuggestionsMessage = "No player has cards that match your suggestion ///suggestionHelpMade\n"
                                print("No player had cards that matched the suggestion.")
                                clientToSend = []
                                clientToSend.append(clients[currentPlayer-1])
                                send_message(noSuggestionsMessage, clientToSend)
                                suggestionHelpMade = True
                            else:
                                waitForHelp = True
                                print("THIS IS WHERE THE HOLD UP IS")
                                print(playerSuggest)
                                suggestionHelp = clients[playerSuggest].recv(1024).decode()
                                print(suggestionHelp)
                                while waitForHelp:
                                    if suggestionHelp == "":
                                        suggestionHelp = clients[playerSuggest].recv(1024).decode()
                                    else:
                                        waitForHelp = False
                                print("GETTING THIS SUGGESTION HELP")
                                print(suggestionHelp)
                        if "No matches" in suggestionHelp:
                            print("No Matches for this client, moving to the next player.")
                            playerSuggest = who_plays_next(playerSuggest, True)
                            suggestCheckCount = suggestCheckCount + 1
                            
                        else:
                            clientToSend = []
                            clientToSend.append(clients[currentPlayer-1])
                            send_message(suggestionHelp + " ///suggestionHelpMade\n", clientToSend)
                            if(playerSuggest == numPlayers):
                                print("Player 1 is showing [" + suggestionHelp + "] to disprove the suggestion.")
                            else:
                                print("Player " + str(playerSuggest+1) + " is showing [" + suggestionHelp + "] to disprove the suggestion.")
                            suggestionHelpMade = True
                    nextMessage = "Move " + person + " to " + room + ".\n"
                    print(nextMessage)
                    currentPlayer = currentPlayer
                    playerTurn = False

                if ACCUSATION_MSG in playerMoveMsg:
                    send_message(playerMoveMsg,clients)
                    accuse = playerMoveMsg.split(" !!!")[1].split("//")[0].split(",")
                    personAccuse = accuse[0]
                    roomAccuse = accuse[1]
                    weaponAccuse = accuse[2]
                    accusation = personAccuse + " in the " + roomAccuse + " with the " + weaponAccuse
                    accusationMessage = "Player " + str(currentPlayer) + " is accusing " + accusation + " \n"
                    if((personAccuse == solutionName) and (roomAccuse == solutionLocation) and (weaponAccuse == solutionWeapon)):
                        wonMessage = "Player " + str(currentPlayer) + " won! \n *****" + accusationMessage
                        print(wonMessage)
                        send_message(wonMessage, clients)
                    else:
                        lostMessage = "Player " + str(currentPlayer) + " lost the game. \n *****" + accusationMessage
                        print(lostMessage)
                        send_message(lostMessage, clients)
                    msg = clients[currentPlayer-1].recv(1024).decode()
                    if "player" in msg:
                        playerToEnd = currentPlayer
                        currentPlayer = who_plays_next(currentPlayer, False)
                        activePlayerNumbers.remove(playerToEnd)
                        if(len(activePlayerNumbers) == 1):
                            activePlayerNumbers.clear()
                            closeConnectionMessage = "CLOSE ALL CONNECTION," + str(currentPlayer) + ",You are the only player left so you win!"
                            send_message(closeConnectionMessage, clients)
                            s.close()
                    if "all" in msg:
                        print("Connection should be ended for all.")
                        activePlayerNumbers.clear()
                        currentPlayer = who_plays_next(currentPlayer, False)
                        send_message("CLOSE ALL CONNECTION", clients)
                        s.close()
                    playerTurn = False
                    
                if (END_MSG in playerMoveMsg) and ("end connection" not in playerMoveMsg) and ("rend") not in playerMoveMsg:
                    print("IN END AND HERE IS THE MOVE MESSSAGE")
                    print(moveMsg.decode(form))
                    print("Player " + str(currentPlayer) + " chose to end their turn.")
                    currentPlayer = who_plays_next(currentPlayer, False)
                    playerTurn = False

s.close()