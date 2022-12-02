from operator import truediv
import pygame
import socket
from game import Game
from player import Player  
import ast
pygame.init()
import enum
import threading
import select
import queue
pygame.init()

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

# connect to server
port = 5050
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((socket.gethostname(), port))
form = 'utf-8'
playerChosen = False

# set up threading for pygame and server events
SERVER_MESSAGE = pygame.USEREVENT+1
class SocketListener(threading.Thread):
    def __init__(self, sock, queue):
         threading.Thread.__init__(self)
         self.daemon = True
         self.socket = sock
         self.queue = queue
    def run(self):
         while True:
             msg = self.socket.recv(1024)
             readmsg = msg.decode(form)
             #self.queue.put(msg)
             new_event = pygame.event.Event(SERVER_MESSAGE, {"message": readmsg})
             pygame.event.post(new_event)
q = queue.Queue()
SocketListener(s,q).start()

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

def movePlayer(p, otherPlayerLocations): # break into 2 functions - first populates drop down correctly, second actually does action
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
    return moveInput #actual moving of player happens later - this just gets a VALID move from player, which it returns

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
        
# Class definitions 
# Text class creates text boxes in (position) with (fontInput) of (base_color)
# has functions to bold text and "grey out" the color
# IF WE WANT USERS TO BE ABLE TO TYPE IN TEXTBOXES, we need to get the "CheckForInput" and "upateText" working
class Text():
	def __init__(self, position, text_input, font_input, bold_input, base_color, greyed_color):
		self.position = position
		self.text_input = text_input
		self.font_input = font_input
		self.bold_input = bold_input
		self.base_color = base_color
		self.greyed_color = greyed_color
		self.text = self.font_input.render(self.text_input, True, self.base_color)
		#self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))  #needed only for checking inputs
		#self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))  #needed only for checking inputs

	def update(self, screen):
		if self.text_input is not None:
			screen.blit(self.text, self.position) # populate on screen

	def boldText(self):
		self.text = self.bold_input.render(self.text_input, True, self.base_color)

	def baseText(self):
		self.text = self.font_input.render(self.text_input, True, self.base_color)

	def greyText(self):
		self.text = self.font_input.render(self.text_input, True, self.greyed_color)

	#def checkForInput(self, position):
    #    if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
    #                                                                                      self.rect.bottom):
    #        return True
    #    return False

    #def updateText(self, new_text_input)
    # read new_text_input 
    # write new_text_input to text_input 

# Button class creates buttons
class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]     
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
            
    def isOver(self, position, button_width, button_height):
        x_p = self.x_pos-button_width/2
        y_p = self.y_pos-button_height/2
        if position[0] > x_p and position[0] < x_p + button_width:
            if position[1] > y_p and position[1] < y_p + button_height:
                return True
        return False
    



################################
# End Class Definition 
# Note that a bulk of definition and updates outside of the gameplay loop
# As few as possible items will have to be updated during gameplay
################################
# Define Variables
# Define  colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (13, 69, 214)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

#Define board areas
width = 1366
height = 768
size = (width, height)
screen = pygame.display.set_mode(size)
# Define the sectors for each section
vertical = 2*width/3 # = 911
hLeft = 3*height/4 # = 576
hRight= 2*height/3 # = 512

# Define other variables
#PI = 3.141592653

# Basic Sreen setup
pygame.display.set_caption("Ctrl-Alt-Elites Clueless") # name of the tab
screen.fill(WHITE) # background color
 
################################
# Import Images Here
################################# Boardgame Image
# Define sizes and locations of images
# Board
boardSize = (911, 576) #set size of board image
boardLocation = (0,0)

boardImage = pygame.image.load("board_image.png").convert() #load image
boardImage = pygame.transform.scale(boardImage, boardSize) #transform size
screen.blit(boardImage, boardLocation) ##populate on screen

## INSERT PLAYER IMAGES IN HERE
#playerSize = (50, 50) #set size of character images
# for each of the images .... 
#playerImage = pygame.image.load("player_image.png").convert() #load image
#boardImage = pygame.transform.scale(boardImage, boardSize) #transform size
#### screen.blit will have to happen in the loop


################################
# Make all of the Buttons Here
################################
# Declare all variables 
button_font = pygame.font.SysFont('Calibri', 16, True, False)
button_color = (255, 249, 242)
button_greyed_color = (133, 105, 73)
button_image = pygame.image.load("button_background.png").convert() #image to be used as button background PLAY WITH THIS
button_width_1 = 100 #width of buttons PLAY WITH THIS
button_height = 50
button_size_1 = (button_width_1, button_height)
button_type_1 = pygame.transform.scale(button_image, button_size_1) #transform size

button_width_2 = 455 #width of buttons PLAY WITH THIS
button_size_2 = (button_width_2, button_height)
button_type_2 = pygame.transform.scale(button_image, button_size_2) #transform size

button_y_shift = (52) #y-shift (spacing) of buttons PLAY WITH THIS
button_x_shift = (150) #y-shift (spacing) of buttons PLAY WITH THIS

# Initialize and update individual BUTTONs: image, pos, text_input, font, base_color, hovering_color)
# Move Button
b_x = width - (button_width_1/2)
b_y = height - 256 + (50/2)
b_move = Button(button_type_1, (b_x, b_y), "Move", button_font, button_color, button_greyed_color)
b_move.update(screen)
# Suggest Button
b_y = b_y + button_y_shift
b_suggest = Button(button_type_1, (b_x, b_y), "Suggest", button_font, button_color, button_greyed_color)
b_suggest.update(screen)
b_suggest.update(screen)
# Accuse Button
b_y = b_y + button_y_shift
b_accuse = Button(button_type_1, (b_x, b_y), "Accuse", button_font, button_color, button_greyed_color)
b_accuse.update(screen)
# Show Button
b_y = b_y + button_y_shift
b_show = Button(button_type_1, (b_x, b_y), "Show", button_font, button_color, button_greyed_color)
b_show.update(screen)
# End Button
b_x = width - (button_width_2/2)
b_y = b_y + button_y_shift
b_end = Button(button_type_2, (b_x, b_y), "End Turn", button_font, button_color, button_greyed_color)
b_end.update(screen)


################################
# Make all of the text boxes Here
################################
# Define fonts
info_font = pygame.font.SysFont('Calibri', 14, False, False)
info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
action_font = pygame.font.SysFont('Calibri', 16, False, False)
notification_font = pygame.font.SysFont('Calibri', 18, False, False)
# Define spacing
info_y_shift = 23
notification_y_shift = 30
# Define colors
info_color = BLACK ## UPDATE
info_title_color = (133, 105, 73)
info_greyed_color = (133, 105, 73)
notification_color = BLACK ##UPDATE

# Initialize and update TEXTs: (self, position, text_input, font_input, bold_input, base_color, greyed_color)
################################
# Info Board
################################
# Names
t_x = vertical + 5
t_y = 5
t_names = Text((t_x, t_y), "NAMES", info_font, info_font_bold, info_title_color, info_greyed_color)
t_names.update(screen)
# NOTE the following could be done in a loop like "for names in names_list", but I don't know how to create objects of unique names doing so

# Mustard
t_y = t_y + info_y_shift
t_mustard= Text((t_x, t_y), "Col. Mustard", info_font, info_font_bold, info_color, info_greyed_color)
t_mustard.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Peacock
t_y = t_y + info_y_shift
t_peacock= Text((t_x, t_y), "Mrs. Peacock", info_font, info_font_bold, info_color, info_greyed_color)
t_peacock.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Plum
t_y = t_y + info_y_shift
t_plum= Text((t_x, t_y), "Prof. Plum", info_font, info_font_bold, info_color, info_greyed_color)
t_plum.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Scarlet
t_y = t_y + info_y_shift
t_scarlet= Text((t_x, t_y), "Ms.Scarlet", info_font, info_font_bold, info_color, info_greyed_color)
t_scarlet.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# White
t_y = t_y + info_y_shift
t_white= Text((t_x, t_y), "Mrs. White", info_font, info_font_bold, info_color, info_greyed_color)
t_white.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Weapons
t_y = t_y + info_y_shift
t_weapons = Text((t_x, t_y), "WEAPONS", info_font, info_font_bold, info_title_color, info_greyed_color)
t_weapons.update(screen)

# Candlestick
t_y = t_y + info_y_shift
t_candle= Text((t_x, t_y), "Candlestick", info_font, info_font_bold, info_color, info_greyed_color)
t_candle.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Dagger
t_y = t_y + info_y_shift
t_dagger= Text((t_x, t_y), "Dagger", info_font, info_font_bold, info_color, info_greyed_color)
t_dagger.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Lead Pipe
t_y = t_y + info_y_shift
t_pipe= Text((t_x, t_y), "Lead Pipe", info_font, info_font_bold, info_color, info_greyed_color)
t_pipe.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Rope
t_y = t_y + info_y_shift
t_rope= Text((t_x, t_y), "Rope", info_font, info_font_bold, info_color, info_greyed_color)
t_rope.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Wrench
t_y = t_y + info_y_shift
t_wrench= Text((t_x, t_y), "Wrench", info_font, info_font_bold, info_color, info_greyed_color)
t_wrench.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Rooms
t_y = t_y + info_y_shift
t_rooms = Text((t_x, t_y), "ROOMS", info_font, info_font_bold, info_title_color, info_greyed_color)
t_rooms.update(screen)

# Study
t_y = t_y + info_y_shift
t_study= Text((t_x, t_y), "Study", info_font, info_font_bold, info_color, info_greyed_color)
t_study.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Hall
t_y = t_y + info_y_shift
t_hall= Text((t_x, t_y), "Hall", info_font, info_font_bold, info_color, info_greyed_color)
t_hall.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Lounc
t_y = t_y + info_y_shift
t_lounge= Text((t_x, t_y), "Lounge", info_font, info_font_bold, info_color, info_greyed_color)
t_lounge.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Library
t_y = t_y + info_y_shift
t_library= Text((t_x, t_y), "Library", info_font, info_font_bold, info_color, info_greyed_color)
t_library.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Billiard Room
t_y = t_y + info_y_shift
t_billiard= Text((t_x, t_y), "Billiard Room", info_font, info_font_bold, info_color, info_greyed_color)
t_billiard.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Dining Room
t_y = t_y + info_y_shift
t_dining= Text((t_x, t_y), "Dining Room", info_font, info_font_bold, info_color, info_greyed_color)
t_dining.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Conservatory
t_y = t_y + info_y_shift
t_conservatory= Text((t_x, t_y), "Conservatory", info_font, info_font_bold, info_color, info_greyed_color)
t_conservatory.update(screen)

# Ballroom
t_y = t_y + info_y_shift
t_ballroom= Text((t_x, t_y), "Ballroom", info_font, info_font_bold, info_color, info_greyed_color)
t_ballroom.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

# Kitchen
t_y = t_y + info_y_shift
t_kitchen= Text((t_x, t_y), "Kitchen", info_font, info_font_bold, info_color, info_greyed_color)
t_kitchen.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#	boldText()

################################
# Notifications
################################# 
# what player are you
t_x = 5
t_y = hLeft + 5
t_x_you = t_x
t_y_you = t_y
## INSERT LOGIC TO read the current player
t_you = Text((t_x_you, t_y_you), "initial", notification_font, info_font_bold, notification_color, notification_color)
t_you.update(screen)

t_x_cards = t_x
t_y_cards = t_y + notification_y_shift
t_cards = Text((t_x_cards, t_y_cards), "initial", notification_font, info_font_bold, notification_color, notification_color)
t_cards.update(screen)

# display current notification
t_x_notification = t_x
t_y_notification = t_y + 2*notification_y_shift
t_notification= Text((t_x_notification, t_y_notification), "Initial", notification_font, info_font_bold, notification_color, notification_color)
t_notification.update(screen)

canClickButtons = False
done = False
clock = pygame.time.Clock()
while not done:
    pygame.draw.rect(screen, BLACK, [0, 0, vertical, hLeft], 2) #Draw a rectangle around the map
    pygame.draw.rect(screen, GREEN, [vertical, 0, width, hRight], 2) #Information Panel
    pygame.draw.rect(screen, RED, [0, hLeft, vertical, height], 2) #notification Panel
    pygame.draw.rect(screen, BLUE, [vertical, hRight, width, height], 2) #Action Panel
    pygame.display.flip()
    clock.tick(60)

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user closes window
            done = True  # Flag to exit the loop
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if canClickButtons:
                if b_move.isOver(pos, button_width_1, button_height):
                    message = "move" 
                if b_accuse.isOver(pos, button_width_1, button_height):
                    message = "accuse"
                if b_suggest.isOver(pos, button_width_1, button_height):
                    message = "suggest"
                if b_show.isOver(pos, button_width_1, button_height):
                    message = "show"
                if b_end.isOver(pos, button_width_2, button_height):
                    message = "end"
        
        if event.type == SERVER_MESSAGE: # If the server sends a message
            readmsg = event.message
            
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
                    #numberOfPlayers = input("->")
                    numberOfPlayers = "2" #dummy for now
                    s.send(numberOfPlayers.encode())
                    #readmsg = s.recv(1024).decode() # NEED TO GET RID OF THIS
                print(readmsg, "\n")
                #message = input(" -> ")
                if int(myNumber) == 1: # dummy for now
                    message = "Mrs. White"
                else:
                    message = "Colonel Mustard"
                playerLocation = Game.playerStartLocations.get(message)
                p = Player(myNumber, message, playerLocation, None, False, False, False, False)
                sendMessage = p.playerName + "," + playerLocation
                s.send(sendMessage.encode())
                #playerMessage = s.recv(1024).decode() # NEED TO GET RID OF THIS
                #print(playerMessage)
                #readmsg = playerMessage
            
            if BEGINNING_MSG in readmsg:
                print(readmsg)
                cards = readmsg.split("Your cards are: ")[1]
                if("Next Turn" in cards):
                    cards = cards.split("N")[0]
                setattr(p, 'cards', ast.literal_eval(cards))            

            if WIN_MSG in readmsg:
                pass # dummy right now
            if LOSE_MSG in readmsg:
                pass # dummy right now
                
            #if ((TURN_MSG or MOVE_MSG) in readmsg) or (SUGGESTION in readmsg):
            #    suggestionValidation = None
            #    if "Player "+str(p.playerNumber) in readmsg:
            #        canClickButtons = True
            #        playerMoveActive = True # CAN I USE THIS TO ALLOW BUTTON CLICKS?
            #    else:
            #        canClickButtons = False

pygame.quit()
s.close() 