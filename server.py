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

def goto(linenum):
    global line
    line = linenum

# function definitions
def who_plays_next(currentPlayer, numPlayers):
    if currentPlayer==0:
        return 1
    if currentPlayer==numPlayers:
        return 1
    return currentPlayer+1
    
def send_message(msg,clients): # sends to ALL clients
    for i in clients:
        # print("INSIDE SEND_MESSAGE")
        # print(msg.encode(form))
        i.send(msg.encode(form))

# server picks a solution (name, location, weapon)
names = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
locations = ["room1", "room2", "room3", "room4", "room5", "room6", "room7", "room8", "room9",
            "hallway12", "hallway23", "hallway14", "hallway25", "hallway36", "hallway45",
            "hallway56", "hallway47", "hallway58", "hallway69", "hallway78", "hallway89"]
roomsToNames = {"room1": "study","room2": "hall","room3": "lounge", "room4": "dining room", 
            "room5": "kitchen", "room6": "ballroom", "room7": "conservatory", "room8": "library", "room9": "billiard room"}
rooms = ["study","hall","lounge","dining room","kitchen", "ballroom", "conservatory", "library", "billiard room"]
weapons = ["rope", "candlestick", "dagger", "wrench", "lead pipe", "revolver"]

cards = names + rooms + weapons
solution = []
solutionName = random.choice(names)
solution.append(solutionName)
solutionLocation = random.choice(rooms)
solution.append(solutionLocation)
solutionWeapon = random.choice(weapons)
solution.append(solutionWeapon)
print(solution)

cards.remove(solutionName)
cards.remove(solutionLocation)
cards.remove(solutionWeapon)

# possible messages from clients
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
    # c.send(msg.encode(form))
    availablePlayers = [name for name in g.playerNames if name not in g.chosenPlayers]
    playerChoice = msg + ".\nWhat player would you like to be? Your choices are " + str(availablePlayers)
    c.send(playerChoice.encode(form))
    playerInfo = c.recv(1024).decode().split(",")
    players = g.chosenPlayers
    players.append(playerInfo[0])
    g.chosenPlayers = players
    initialMessage = ("\nYour are " + playerInfo[0] + " and you are starting the game in " + playerInfo[1])
    c.send(initialMessage.encode(form))
    
    
    # when all clients are connected, the game begins
    if numPlayers>=3: # need to update this so numPlayers == 6 or some timeout function

        print("INSIDE HERE")
        #also, need to send each client what their cards are
        #so logic here to shuffle & divide cards, then send cards to client
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
        # send_message("Game is beginning with "+str(numPlayers)+" players.  \n",clients)

        print("ALL THE WAY DOWN HERE HERE")

        # for y in clients:
        #     cardsMessage = "Your cards are: " + str(hands[playersCount]) + "\n"

        #     y.send(cardsMessage.encode(form))
        
        testCounter = 0 # delete this when while loop implemented properly
        numTurnsTested = 9 # delete this when while loop implemented properly
        currentPlayer = who_plays_next(currentPlayer, numPlayers)
        while winner==0:
            testCounter = testCounter+1 # delete this when while loop implemented properly
            print("current player: ", currentPlayer)
            msg = "Next Turn: Player "+str(currentPlayer)+"."
            # print("SENDING THIS MESSAGE")
            # print(msg)
            send_message(msg, clients)

            playerTurn = True
            while playerTurn:
                print("INSIDE HERE")
                moveMsg = clients[currentPlayer-1].recv(1024)
                playerMoveMsg = str(currentPlayer) + moveMsg.decode(form)



                # wait to receive messages from clients          
                # msg = clients[currentPlayer-1].recv(1024)
                # readmsg = msg.decode(form)
                # print(f"[{addr}] {msg}")
                
                # message received from client, now must be sent to all clients or handled
                if MOVE_MSG in playerMoveMsg:
                    # print("INSIDE MOVE MESSAGE")
                    # print(playerMoveMsg)
                    #/////////////////////////////////////////
                    send_message(playerMoveMsg,clients)
                    moveChoice = clients[currentPlayer-1].recv(1024).decode()

                    # print(moveChoice)
                    # print("RECEIVING NEXT MESSAGE")
                    # print(moveChoice)
                    if("You can only move once per turn" in moveChoice):
                        moveMessage = "Player cannot move again"
                    else:
                        moveMessage = "Player " + str(currentPlayer) + " is moving to " + moveChoice;
                    #/////////////////////////////////////////
                    send_message(moveMessage, clients)
                    # print("MAKING IT HERE")
                    msg = clients[currentPlayer-1].recv(1024).decode()
                    # print("RECEIVING NEXT MESSAGE")
                    print(msg)

                    # print("^^^^^^^^^^^^^^^^^^")
                    # print("PRINTING WINNER HERE $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                    # print(winner)
                    currentPlayer = currentPlayer
                    # print(currentPlayer)
                    playerTurn = False

                    # if(msg == "Player must now suggest"):
                    #     # playerMoveMsg = "suggest"
                    #     goto(125)
                    # nextMoveMessage = "Player can make another move" 
                    # send_message(nextMoveMessage, clients)
                    
                if SUGGESTION_MSG in playerMoveMsg:
                    # print("INSIDE SUGGESTION MESSAGE")
                    # print(playerMoveMsg)
                    #/////////////////////////////////////////
                    send_message(playerMoveMsg,clients)
                    suggestionMessage = clients[currentPlayer-1].recv(1024).decode()
                    if "cannot" in suggestionMessage:
                        falseSuggestion = "You are not in a room so you cannot make a suggestion \n"
                        send_message(falseSuggestion, clients)
                        # falseSuggestionMessage = clients[currentPlayer-1].recv(1024).decode()
                        # print(falseSuggestion)
                        currentPlayer = currentPlayer
                        playerTurn = False
                    # roomSuggest = clients[currentPlayer-1].recv(1024).decode()
                    # weaponSuggest = clients[currentPlayer-1].recv(1024).decode()
                    else:
                        goodSuggestion = "Player is able to make a suggestion \n"
                        # clientsToValidate = clients
                        clientsToValidate = []
                        clientsToValidate.extend(clients)
                        # print("CLIENTS ARE UP HERE")
                        # print(clients)
                        # print(currentPlayer-1)
                        # print(clientsToValidate)
                        clientsToValidate.pop(currentPlayer-1)
                        # print(clientsToValidate)
                        # print("CLIENTS ARE UP HERE AGAIN!!!!!")
                        # print(clients)
                        send_message(goodSuggestion, clientsToValidate)
                        suggestion = suggestionMessage.split(",")
                        print("SUGGESTION HERE")
                        print(suggestion)
                        person = suggestion[0]
                        room = roomsToNames.get(suggestion[1])
                        weapon = suggestion[2]
                        # print("RECEIVING SUGGESTION MESSAGE")
                        # print(person)
                        # print(solutionName)
                        # print(room)
                        # print(solutionLocation)
                        # print(weapon)
                        # print(solutionWeapon)
                        # print(str(who_plays_next(currentPlayer, numPlayers)))
                        # print(currentPlayer)
                        # print(numPlayers)
                        playerToPass = who_plays_next(currentPlayer, numPlayers)
                        # print("PLAYER TO PASS BELOW")
                        # print(playerToPass)
                        # print("///////////////////////")
                        suggestionHelpMade = False
                        playerSuggest = currentPlayer
                        suggestCheckCount = 0
                        while (suggestionHelpMade != True):
                            print("PLAYER SUGGEST AT THE BEGINNING")
                            print(playerSuggest)
                            suggestionPass = person + " in the " + room + " with the " + weapon
                            suggestionMessage = "Player " + str(currentPlayer) + " is suggesting " + suggestionPass + ".\n ///"
                            if(playerSuggest == numPlayers):
                                fullSuggestion = person + "," + room + "," + weapon + "," + str(1)
                            else:
                                fullSuggestion = person + "," + room + "," + weapon + "," + str(playerSuggest+1)
                            #/////////////////////////////////////////
                            send_message(suggestionMessage + fullSuggestion, clients)
                            # send_message(fullSuggestion, clients)
                            # print("PRINTING CURRENT PLAYER HERE FOR CLIENT HELP")
                            # print(str(currentPlayer))
                            # suggestionHelpMade = False
                            # playerSuggest = currentPlayer
                            # while suggestionHelpMade != True:
                            print("IN HERE")
                            print(playerSuggest)
                            print(numPlayers)
                            if(playerSuggest == numPlayers) and (suggestCheckCount != numPlayers-1): 
                                suggestionHelp = clients[0].recv(1024).decode()
                                # currentPlayer = currentPlayer
                                # playerTurn = False
                            else:
                                print("MADE IT")
                                print(playerSuggest)
                                print(clients)
                                # print(clients[playerSuggest])
                                if(suggestCheckCount == numPlayers-1):
                                    noSuggestionsMessage = "No player has cards that match your suggestion"
                                    print("/////////////////////")

                                    print(currentPlayer)
                                    clientToSend = []
                                    
                                    clientToSend.append(clients[currentPlayer-1])
                                    send_message(noSuggestionsMessage, clientToSend)
                                    suggestionHelpMade = True
                                else:
                                    suggestionHelp = clients[playerSuggest].recv(1024).decode()
                                    print("SUGGESTION HELP HERE")
                                    print(suggestionHelp)
                                # currentPlayer = currentPlayer
                                # playerTurn = False
                        # print("SUGGESTION HELP MESSAGE")
                        # print(suggestionHelp)
                            if "No matches" in suggestionHelp:
                                print("No Matches for this client")
                                playerSuggest = who_plays_next(playerSuggest, numPlayers)
                                print(playerSuggest)
                                suggestCheckCount = suggestCheckCount + 1
                                
                            else:
                                # print(suggestionHelp)
                                # print("IN THIS IF STATEMENT")
                                clientToSend = []
                                print("PLAYER SUGGEST HERE MINUS 1")
                                print(str(playerSuggest-1))
                                clientToSend.append(clients[currentPlayer-1])
                                print("PRINTING CURRENT PLAYER HERE")
                                print(playerSuggest)
                                print(currentPlayer)
                                print(clientsToValidate)
                                print(clients)
                                print(clientToSend)
                                # clientToSend.append(clients[currentPlayer])
                                # print(clientToSend)
                                #/////////////////////////////////////////
                                # suggestionHelpMade == True
                                send_message(suggestionHelp + " ///\n", clientToSend)
                                
                                print("WE ARE HERE NOW!!!!!!!!")
                                print(suggestionHelpMade)
                                msg = clients[currentPlayer-1].recv(1024).decode()
                                print("RECEIVING NEXT MESSAGE")
                                suggestionHelpMade = True
                        # print(msg)
                        # print(type(list(clients.index(currentPlayer-1))))
                        # print(list(clients[currentPlayer-1]))
                        
                        

                        
                        # send_message(msg, clients)
                        # print("^$$$$$$$$$$$$$$")
                        currentPlayer = currentPlayer
                        playerTurn = False

                if ACCUSATION_MSG in playerMoveMsg:
                    # print("INSIDE ACCUSATION MESSAGE")
                    print(playerMoveMsg)
                    #/////////////////////////////////////////
                    send_message(playerMoveMsg,clients)
                    accusationClientMesssage = clients[currentPlayer-1].recv(1024).decode()
                    accuse = accusationClientMesssage.split(",")
                    personAccuse = accuse[0]
                    roomAccuse = accuse[1]
                    weaponAccuse = accuse[2]
                    # print("RECEIVING ACCUSATION MESSAGE")
                    # print(personAccuse)
                    # print(solutionName)
                    # print(roomAccuse)
                    # print(solutionLocation)
                    # print(weaponAccuse)
                    # print(solutionWeapon)
                    # print("///////////////////////")
                    accusation = personAccuse + " in the " + roomAccuse + " with the " + weaponAccuse
                    accusationMessage = "Player " + str(currentPlayer) + " is accusing " + accusation + " \n"
                    #/////////////////////////////////////////
                    send_message(accusationMessage, clients)
                    time.sleep(1.5)
                    if((personAccuse == solutionName) and (roomAccuse == solutionLocation) and (weaponAccuse == solutionWeapon)):
                        wonMessage = "Player " + str(currentPlayer) + " won! \n"
                        #/////////////////////////////////////////
                        send_message(wonMessage, clients)
                    else:
                        lostMessage = "Player " + str(currentPlayer) + " lost the game. \n"
                        #/////////////////////////////////////////
                        send_message(lostMessage, clients)
                    msg = clients[currentPlayer-1].recv(1024).decode()
                    # print("RECEIVING NEXT MESSAGE")
                    # print(msg)
                    # send_message(msg, clients)
                    # print("@@@@@@@@@@@@@@@@@@")
                    if "player" in msg:
                        print("PLAYER CONNECTION SHOULD BE ENDED")
                        # NEED TO FIGURE OUT HOW TO DROP CONNECTION
                        # c.shutdown()
                        # numPlayers -= 1
                    if "all" in msg:
                        print("CONNECTION SHOULD BE ENDED FOR ALL")
                        # NEED TO FIGURE OUT HOW TO DROP CONNECTION
                        # c.shutdown()
                        # s.close()
                    playerTurn = False
                    currentPlayer = who_plays_next(currentPlayer, numPlayers)
                if (END_MSG in playerMoveMsg) and ("end connection" not in playerMoveMsg):
                    # print("IN END MESSAGE")
                    print("!!!!!!!!!!!!!!!!!!!!")
                    print(playerMoveMsg)
                    
                    # print(validation)
                    # if validation[1] == True:
                    send_message(playerMoveMsg,clients)
                    msg = clients[currentPlayer-1].recv(1024).decode()
                    print("+++++++++++++++++++++")
                    validation = msg.split("&& ")
                    # print(validation)
                    print(validation[1])
                    print(eval(validation[1]))
                    print(bool(validation[1]))
                    print(currentPlayer)
                    if(eval(validation[1]) == True):
                        print("GOING IN TO THE TRUE VALIDATION")
                        currentPlayer = who_plays_next(currentPlayer, numPlayers)
                            # print(currentPlayer)
                        playerTurn = False
                    elif(eval(validation[1]) == False):
                        print("GOING IN HERE")
                        print(currentPlayer)
                        currentPlayer = currentPlayer
                        print(currentPlayer)
                        playerTurn = False
                        #/////////////////////////////////////////
                    # else:
                    #     send_message(validation[0],clients)
                    #     msg = clients[currentPlayer-1].recv(1024).decode()
                    #     # print("+++++++++++++++++++++")
                    #     # print(msg)
                    #     # print(currentPlayer)
                    #     currentPlayer = currentPlayer
                    #     # print(currentPlayer)
                    #     playerTurn = False
                    
                    # endMessage = clients[currentPlayer-1].recv(1024).decode()
                    # print(endMessage)
                
                # if testCounter == numTurnsTested: # delete this when while loop implemented properly
                #     winner = 1 # delete this when while loop implemented properly
                #     gameOn = False
                
                # NEED TO ADD ELSE IF MESSAGE ISNT VALID
socket.close     
