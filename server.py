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

# function definitions
def who_plays_next(currentPlayer, numPlayers):
    # if currentPlayer==0:
    #     return 1
    if currentPlayer==numPlayers:
        return 1
    return currentPlayer+1
    
def send_message(msg,clients): # sends to ALL clients
    for i in clients:
        print("INSIDE SEND_MESSAGE")
        print(msg.encode(form))
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

while gameOn:
    # when client connects
    c, addr = s.accept()
    clients.append(c)
    addresses.append(addr)
    print("Connection from: ", str(addr))
    numPlayers = numPlayers+1
    print("Number of Players: ", numPlayers,"\n")
    msg = "Connection established. You are Player "+str(numPlayers)+"."
    c.send(msg.encode(form))

    # pygame.init()
    # clock = pygame.time.Clock()
    # # screen = pygame.display.set_mode((128, 128))
    # counter, text = 30, '30'.rjust(3)
    # pygame.time.set_timer(numPlayers == 6, 3000)
    # # font = pygame.font.SysFont('Consolas', 30)
    # # for e in pygame.event.get():
    # while numPlayers < 6 and counter != 0:
    #     print(counter)
    #     counter -= 1
    #     text = str(counter).rjust(3) if counter > 0 else 'boom!'

    # # screen.fill((255, 255, 255))
    # # screen.blit(font.render(text, True, (0, 0, 0)), (32, 48))
    # # pygame.display.flip()
    # clock.tick(60)
    
    # when all clients are connected, the game begins
    if numPlayers>=3: # need to update this so numPlayers == 6 or some timeout function

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
            msg = "Game is beginning with "+str(numPlayers)+" players. \n \nYour cards are: " + str(hands[playersCount]) + "\n"
            playersCount += 1
            i.send(msg.encode(form))
        # send_message("Game is beginning with "+str(numPlayers)+" players.  \n",clients)



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

            for i in clients:
                i.send(msg.encode(form))

            playerTurn = True
            while playerTurn:
                moveMsg = clients[currentPlayer-1].recv(1024)
                print(";;;;;;;;;;;")
                playerMoveMsg = str(currentPlayer) + moveMsg.decode(form)
                print("................")
                # send_message(playerMoveMsg, clients)

                # wait to receive messages from clients          
                # msg = clients[currentPlayer-1].recv(1024)
                # readmsg = msg.decode(form)
                # print(f"[{addr}] {msg}")
                
                # message received from client, now must be sent to all clients or handled
                if MOVE_MSG in playerMoveMsg:
                    print("INSIDE MOVE MESSAGE")
                    print(playerMoveMsg)
                    send_message(playerMoveMsg,clients)
                    moveChoice = clients[currentPlayer-1].recv(1024).decode()
                    print("RECEIVING NEXT MESSAGE")
                    print(moveChoice)
                    moveMessage = "Player " + str(currentPlayer) + " is moving to " + moveChoice;
                    send_message(moveMessage, clients)
                    msg = clients[currentPlayer-1].recv(1024).decode()
                    print("RECEIVING NEXT MESSAGE")
                    print(msg)
                    print("^^^^^^^^^^^^^^^^^^")
                    
                if SUGGESTION_MSG in playerMoveMsg:
                    print("INSIDE SUGGESTION MESSAGE")
                    print(playerMoveMsg)
                    send_message(playerMoveMsg,clients)
                    suggestionMessage = clients[currentPlayer-1].recv(1024).decode()
                    # roomSuggest = clients[currentPlayer-1].recv(1024).decode()
                    # weaponSuggest = clients[currentPlayer-1].recv(1024).decode()
                    suggestion = suggestionMessage.split(",")
                    person = suggestion[0]
                    room = roomsToNames.get(suggestion[1])
                    weapon = suggestion[2]
                    print("RECEIVING SUGGESTION MESSAGE")
                    print(person)
                    print(solutionName)
                    print(room)
                    print(solutionLocation)
                    print(weapon)
                    print(solutionWeapon)
                    print("///////////////////////")
                    suggestion = person + " in the " + room + " with the " + weapon
                    suggestionMessage = "Player " + str(currentPlayer) + " is suggesting " + suggestion + " \n";
                    send_message(suggestionMessage, clients)
                    msg = clients[currentPlayer-1].recv(1024).decode()
                    print("RECEIVING NEXT MESSAGE")
                    print(msg)
                    # send_message(msg, clients)
                    print("^$$$$$$$$$$$$$$")

                if ACCUSATION_MSG in playerMoveMsg:
                    print("INSIDE ACCUSATION MESSAGE")
                    print(playerMoveMsg)
                    send_message(playerMoveMsg,clients)
                    personAccuse = clients[currentPlayer-1].recv(1024).decode()
                    roomAccuse = clients[currentPlayer-1].recv(1024).decode()
                    weaponAccuse = clients[currentPlayer-1].recv(1024).decode()
                    print("RECEIVING ACCUSATION MESSAGE")
                    print(personAccuse)
                    print(solutionName)
                    print(roomAccuse)
                    print(solutionLocation)
                    print(weaponAccuse)
                    print(solutionWeapon)
                    print("///////////////////////")
                    accusation = personAccuse + " in the " + roomAccuse + " with the " + weaponAccuse
                    accusationMessage = "Player " + str(currentPlayer) + " is accusing " + accusation + " \n";
                    send_message(accusationMessage, clients)
                    time.sleep(3)
                    if((personAccuse == solutionName) and (roomAccuse == solutionLocation) and (weaponAccuse == solutionWeapon)):
                        wonMessage = "Player " + str(currentPlayer) + " won! \n"
                        send_message(wonMessage, clients)
                    else:
                        lostMessage = "Player " + str(currentPlayer) + " lost the game. \n"
                        send_message(lostMessage, clients)
                    msg = clients[currentPlayer-1].recv(1024).decode()
                    print("RECEIVING NEXT MESSAGE")
                    print(msg)
                    # send_message(msg, clients)
                    print("@@@@@@@@@@@@@@@@@@")
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
                    print("IN END MESSAGE")
                    print("!!!!!!!!!!!!!!!!!!!!")
                    print(playerMoveMsg)
                    send_message(playerMoveMsg,clients)
                    msg = clients[currentPlayer-1].recv(1024).decode()
                    print("+++++++++++++++++++++")
                    print(msg)
                    playerTurn = False
                    currentPlayer = who_plays_next(currentPlayer, numPlayers)
                    # endMessage = clients[currentPlayer-1].recv(1024).decode()
                    # print(endMessage)
                
                if testCounter == numTurnsTested: # delete this when while loop implemented properly
                    winner = 1 # delete this when while loop implemented properly
                    gameOn = False
                
                # NEED TO ADD ELSE IF MESSAGE ISNT VALID
socket.close     
