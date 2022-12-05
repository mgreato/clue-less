from operator import truediv
import pygame
import socket
from game import Game
from player import Player  
import ast
import enum
import threading
import select
import queue

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
        self.bolded = False

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,self.rect.bottom):
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

pygame.init()
pygame.event.clear()

# possible messages from server
CONNECTED_MSG = "Connection established"
BEGINNING_MSG = "Game is beginning"
TURN_MSG = "Next Turn"
# MOVE_MSG = "another"
SUGGESTION = "is suggesting "
CARDS_MSG = "Your cards are"
WIN_MSG = "You Win"
LOSE_MSG = "You Lose"
PLAYER_CHOICE_MESSAGE = "What player would you like to be?"
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

playerText = ""
cardText = ""

choiceInput = ""
moveChoiceMade = False
currentButtons = []
buttonsClicked = False
clickedButton = ""
myNumber = 0
suggesting = False
personSuggested = ""
weaponSuggested = ""
roomSuggested = ""
collectSuggestionHelp = False
waitingForSuggestion = False
suggestionHelpPlayer = 0

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

def moveOptionButtons(moveOptions):
    pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
    pygame.display.update()
    print("SHOULD DRAW RECTANGLE NOW")
    info_font = pygame.font.SysFont('Calibri', 14, False, False)
    info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
    where = Text((1075, 525), "Where would you like to move?", info_font, info_font_bold, (0,0,0), info_greyed_color)
    where.update(screen)
    size = (145, 65)
    font = pygame.font.SysFont('Calibri', 16, True, False)
    buttonType = pygame.transform.scale(button_image, size) #transform size
    buttonList = []
    x = 250
    y = 250
    buttonCount = 1
    for option in moveOptions:
        print("PRINTING OPTION")
        print(option)
        if buttonCount % 2 == 1:
            print("ODD")
            print(x)
            print(y)
            option = Button(buttonType, (850+x, 325+y), option, font, (0,255,255), (0,50,50))
            buttonList.append(option)
            option.update(screen)
            x += 170
            buttonCount += 1
        else:
            print("EVEN")
            print(x)
            print(y)
            option = Button(buttonType, (850+x, 325+y), option, font, (0,255,255), (0,50,50))
            buttonList.append(option)
            option.update(screen)
            y += 250
            buttonCount += 1
        pygame.display.update()
    return buttonList

def movePlayer(p, otherPlayerLocations):
    otherPlayerLocationsList = [h for h in ast.literal_eval(otherPlayerLocations) if ("room" not in h)]
    playerInRoom = p.playerLocation.__contains__("room")
    if(p.playerLocation == "None"):
        possibleHallways = playerFirstLocations.get(p.playerName)
        # print(str(possibleHallways))
        # print([possibleHallways])
        # print(type(possibleHallways))
        # print("Where would you like to move? Your first move must be to: " + str(possibleHallways))
        return [possibleHallways]
    # if(p.hasMoved == True):
    #     moveInput = "You can only move once per turn."
    #     print(moveInput)
    #     s.send(moveInput.encode())
        # clientsMessage = s.recv(1024).decode()
    if(playerInRoom):
        roomNumber = p.playerLocation.split("room")[1]
        possibleHallways = [h for h in locations if (("hallway" and roomNumber in h) and ("room" not in h) and (h not in otherPlayerLocationsList))]
        print("IN THE PLAYER IS IN A ROOM PART")
        print(otherPlayerLocationsList)
        print(possibleHallways)
        check_diagonal_result = can_take_secret_passage(p.playerLocation)
        if (len(possibleHallways) == 0) and (check_diagonal_result[0] == False):
            moveInput = "NO POSSIBLE OPTIONS"
            return moveInput
            # print(moveInput)
            # s.send(moveInput.encode())
            # clientsMessage = s.recv(1024).decode()
            # print(clientsMessage)
        else:
            if check_diagonal_result[0] == True:
                if(len(possibleHallways) == 0):
                    print("Where would you like to move? Your only option is:  " + check_diagonal_result[1])
                    return [check_diagonal_result[1]]
                else:
                    print("Where would you like to move? Your hallway choices are: " + str(possibleHallways) + ". Your diagonal room choice is: " + check_diagonal_result[1])
                    possible = possibleHallways
                    possible.append(check_diagonal_result[1])
                    return possible
            else:
                print("Where would you like to move? Your choices are: " + str(possibleHallways))
                return possibleHallways
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
            return possibleRooms
        # validMove = False
        # while validMove == False:
        #     moveInput = input("->")
        #     if(moveInput not in otherPlayerLocationsList):
        #         validMove = True
        #     else:
        #         print("That room is already occupied, please enter another choice.")
        # if("room" not in moveInput):
        #     p.hasSuggested = True   
        #     p.canEndTurn = True 
        # moveMessage = moveInput + "," + p.playerName
        # s.send(moveMessage.encode())
        # clientsMessage = s.recv(1024).decode()
        # p.hasMoved = True
    # return moveInput

def printPlayerButtons():
    pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
    pygame.display.update()
    info_font = pygame.font.SysFont('Calibri', 14, False, False)
    info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
    who = Text((1075, 525), "Who would you like to suggest?", info_font, info_font_bold, (0,0,0), info_greyed_color)
    who.update(screen)
    size = (100, 50)
    positions = [(1075, 575), (1190, 575), (1305, 575), (1075, 650), (1190, 650), (1305, 650)]
    font = pygame.font.SysFont('Calibri', 16, True, False)
    buttonType = pygame.transform.scale(button_image, size) #transform size
    playerButtons = []
    for i in range(0,len(names)):
        print("SIZES")
        print(positions[i][0])
        print(names[i])
        playerButton = Button(buttonType, (positions[i]), names[i], font, (0,255,255), (0,50,50))
        playerButtons.append(playerButton)
        playerButton.update(screen)
    pygame.display.update()
    return playerButtons

def printWeaponButtons():
    pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
    pygame.display.update()
    info_font = pygame.font.SysFont('Calibri', 14, False, False)
    info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
    who = Text((1075, 525), "What weapon would you like to suggest?", info_font, info_font_bold, (0,0,0), info_greyed_color)
    who.update(screen)
    size = (100, 50)
    positions = [(1075, 575), (1190, 575), (1305, 575), (1075, 650), (1190, 650), (1305, 650)]
    font = pygame.font.SysFont('Calibri', 16, True, False)
    buttonType = pygame.transform.scale(button_image, size) #transform size
    weaponButtons = []
    for i in range(0,len(weapons)):
        print("SIZES")
        print(positions[i][0])
        print(names[i])
        weaponButton = Button(buttonType, (positions[i]), weapons[i], font, (0,255,255), (0,50,50))
        weaponButtons.append(weaponButton)
        weaponButton.update(screen)
    pygame.display.update()
    return weaponButtons

def printSuggestionHelpButtons(playerNumber, suggestionMatches):
    print("INSIDE PRINT SUGGESTION HELP BUTTONS")
    info_font = pygame.font.SysFont('Calibri', 14, False, False)
    info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
    helpMessage = "What card would you like to show to player" + str(playerNumber) + "?"
    help = Text((1025, 525), helpMessage, info_font, info_font_bold, (0,0,0), info_greyed_color)
    help.update(screen)
    size = (100, 50)
    positions = [(1100, 575), (1250, 575), (1175, 650)]
    font = pygame.font.SysFont('Calibri', 16, True, False)
    buttonType = pygame.transform.scale(button_image, size) #transform size
    helpButtons = []
    for i in range(0,len(suggestionMatches)):
        helpButton = Button(buttonType, (positions[i]), suggestionMatches[i], font, (0,255,255), (0,50,50))
        helpButtons.append(helpButton)
        helpButton.update(screen)
    pygame.display.update()
    # currentButtons = helpButtons
    return helpButtons

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
boardSize = (911, 768) #set size of board image
boardLocation = (0,0)

boardImage = pygame.image.load("gameboard.png").convert() #load image
boardImage = pygame.transform.scale(boardImage, boardSize) #transform size
background_image = pygame.image.load("background.png").convert() #image to be used as button background PLAY WITH THIS
initialBoardImage = pygame.image.load("background.png").convert()
initialBoardImage = pygame.transform.scale(initialBoardImage, boardSize)
screen.blit(initialBoardImage, boardLocation) ##populate on screen
#screen.blit(boardImage, boardLocation) ##populate on screen

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

## height and width of info buttons
info_height = 32
info_width = 151
button_size_3 = (info_width, info_height)
button_type_3 = pygame.transform.scale(background_image, button_size_3) #transform size

button_y_shift = (52) #y-shift (spacing) of buttons PLAY WITH THIS
button_x_shift = (150) #y-shift (spacing) of buttons PLAY WITH THIS

# Initialize and update individual BUTTONs: image, pos, text_input, font, base_color, hovering_color)
# Move Button
b_x = width - 455 + (button_width_1/2)
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
# Make all of the text box BUTTONS Here
################################
# Define fonts
info_font = pygame.font.SysFont('Calibri', 14, False, False)
info_font_bold = pygame.font.SysFont('Calibri', 16, True, False)
action_font = pygame.font.SysFont('Calibri', 16, False, False)
notification_font = pygame.font.SysFont('Calibri', 18, False, False)
# Define spacing
info_y_shift = info_height
notification_y_shift = 30
# Define colors
info_color = WHITE ## UPDATE
info_title_color = (133, 105, 73)
info_greyed_color = (133, 105, 73)
notification_color = BLACK ##UPDATE

# Initialize and update TEXTs: (self, position, text_input, font_input, bold_input, base_color, greyed_color)
################################
# Info Board
################################
# Print instrucdtions for how to use the info panel

# Names
t_x = vertical + (info_width/2)
t_y_1 = 192 + (info_height/2)
t_y = t_y_1
t_names = Button(button_type_3, (t_x,t_y), "NAMES", info_font, info_color, info_greyed_color)
t_names.update(screen)
# NOTE the following could be done in a loop like "for names in names_list", but I don't know how to create objects of unique names doing so

# Mustard
t_y = t_y_1 + info_y_shift
t_mustard= Button(button_type_3, (t_x, t_y), "Col. Mustard", info_font, info_color, info_greyed_color)
t_mustard.update(screen)

# Peacock
t_y = t_y + info_y_shift
t_peacock= Button(button_type_3, (t_x, t_y), "Mrs. Peacock", info_font, info_color, info_greyed_color)
t_peacock.update(screen)

# Plum
t_y = t_y + info_y_shift
t_plum= Button(button_type_3, (t_x, t_y), "Prof. Plum", info_font, info_color, info_greyed_color)
t_plum.update(screen)

# Scarlet
t_y = t_y + info_y_shift
t_scarlet= Button(button_type_3, (t_x, t_y), "Ms. Scarlet", info_font, info_color, info_greyed_color)
t_scarlet.update(screen)

# White
t_y = t_y + info_y_shift
t_white= Button(button_type_3, (t_x, t_y), "Mrs. White", info_font, info_color, info_greyed_color)
t_white.update(screen)

# Green
t_y = t_y + info_y_shift
t_green= Button(button_type_3, (t_x, t_y), "Rev. Green", info_font, info_color, info_greyed_color)
t_green.update(screen)

# Weapons
t_x = t_x + info_width # shift to the right for a new "column"
t_y = t_y_1
t_weapons = Button(button_type_3, (t_x, t_y), "WEAPONS", info_font, info_color, info_greyed_color)
t_weapons.update(screen)

# Candlestick
t_y = t_y + info_y_shift
t_candle= Button(button_type_3, (t_x, t_y), "Candlestick", info_font, info_color, info_greyed_color)
t_candle.update(screen)

# Dagger
t_y = t_y + info_y_shift
t_dagger= Button(button_type_3, (t_x, t_y), "Dagger", info_font, info_color, info_greyed_color)
t_dagger.update(screen)

# Lead Pipe
t_y = t_y + info_y_shift
t_pipe= Button(button_type_3, (t_x, t_y), "Lead Pipe", info_font, info_color, info_greyed_color)
t_pipe.update(screen)

# Rope
t_y = t_y + info_y_shift
t_rope= Button(button_type_3, (t_x, t_y), "Rope", info_font, info_color, info_greyed_color)
t_rope.update(screen)

# Wrench
t_y = t_y + info_y_shift
t_wrench= Button(button_type_3, (t_x, t_y), "Wrench", info_font, info_color, info_greyed_color)
t_wrench.update(screen)

# Revolver
t_y = t_y + info_y_shift
t_revolver= Button(button_type_3, (t_x, t_y), "Revolver", info_font, info_color, info_greyed_color)
t_revolver.update(screen)

# Rooms
t_x = t_x + info_width # shift to the right for a new "column"
t_y = t_y_1
t_rooms = Button(button_type_3, (t_x, t_y), "ROOMS", info_font, info_color, info_greyed_color)
t_rooms.update(screen)

# Study
t_y = t_y + info_y_shift
t_study= Button(button_type_3, (t_x, t_y), "Study", info_font, info_color, info_greyed_color)
t_study.update(screen)

# Hall
t_y = t_y + info_y_shift
t_hall= Button(button_type_3, (t_x, t_y), "Hall", info_font, info_color, info_greyed_color)
t_hall.update(screen)

# Lounc
t_y = t_y + info_y_shift
t_lounge= Button(button_type_3, (t_x, t_y), "Lounge", info_font, info_color, info_greyed_color)
t_lounge.update(screen)

# Library
t_y = t_y + info_y_shift
t_library= Button(button_type_3, (t_x, t_y), "Library", info_font, info_color, info_greyed_color)
t_library.update(screen)

# Billiard Room
t_y = t_y + info_y_shift
t_billiard= Button(button_type_3, (t_x, t_y), "Billiard", info_font, info_color, info_greyed_color)
t_billiard.update(screen)

# Dining Room
t_y = t_y + info_y_shift
t_dining= Button(button_type_3, (t_x, t_y), "Dining", info_font, info_color, info_greyed_color)
t_dining.update(screen)

# Conservatory
t_y = t_y + info_y_shift
t_conservatory= Button(button_type_3, (t_x, t_y), "Conservatory", info_font, info_color, info_greyed_color)
t_conservatory.update(screen)

# Ballroom
t_y = t_y + info_y_shift
t_ballroom= Button(button_type_3, (t_x, t_y), "Ballroom", info_font, info_color, info_greyed_color)
t_ballroom.update(screen)

# Kitchen
t_y = t_y + info_y_shift
t_kitchen= Button(button_type_3, (t_x, t_y), "Kitchen", info_font, info_color, info_greyed_color)
t_kitchen.update(screen)

################################
# Notifications
################################# 
t_x = vertical + 5
t_y = 5
fontHeight = 18
t_line1 = Text((vertical+5, 5), "INITIAL", notification_font, info_font_bold, notification_color, notification_color)
t_line1.update(screen)
t_line2 = Text((vertical+5, 5+1*fontHeight), "INITIAL", notification_font, info_font_bold, notification_color, notification_color)
t_line2.update(screen)
t_line3 = Text((vertical+5, 5+2*fontHeight), "INITIAL", notification_font, info_font_bold, notification_color, notification_color)
t_line3.update(screen)
t_line4 = Text((vertical+5, 5+3*fontHeight), "INITIAL", notification_font, info_font_bold, notification_color, notification_color)
t_line4.update(screen)
t_line5 = Text((vertical+5, 5+4*fontHeight), "INITIAL", notification_font, info_font_bold, notification_color, notification_color)
t_line5.update(screen)
t_line6 = Text((vertical+5, 5+5*fontHeight), "INITIAL", notification_font, info_font_bold, notification_color, notification_color)
t_line6.update(screen)



def updateNotifications(text1, text2, text3, text4, text5, text6):
    pygame.draw.rect(screen, WHITE, [vertical, 0, vertical, 192])
    pygame.draw.rect(screen, RED, [vertical, 0, vertical, 192], 2)
    t_line1 = Text((vertical+5, 5), text1, notification_font, info_font_bold, notification_color, notification_color)
    t_line1.update(screen)
    t_line2 = Text((vertical+5, 5+1*fontHeight), text2, notification_font, info_font_bold, notification_color, notification_color)
    t_line2.update(screen)
    t_line3 = Text((vertical+5, 5+2*fontHeight), text3, notification_font, info_font_bold, notification_color, notification_color)
    t_line3.update(screen)
    t_line4 = Text((vertical+5, 5+3*fontHeight), text4, notification_font, info_font_bold, notification_color, notification_color)
    t_line4.update(screen)
    t_line5 = Text((vertical+5, 5+4*fontHeight), text5, notification_font, info_font_bold, notification_color, notification_color)
    t_line5.update(screen)
    t_line6 = Text((vertical+5, 5+5*fontHeight), text6, notification_font, info_font_bold, notification_color, notification_color)
    t_line6.update(screen)

currentPlayerLocations = ""
canClickButtons = False
done = False
clock = pygame.time.Clock()
while not done:
    pygame.draw.rect(screen, BLACK, [0, 0, vertical, height], 2) #Draw a rectangle around the map
    pygame.draw.rect(screen, RED, [vertical, 0, width-vertical, 192], 2) #Notification Panel
    pygame.draw.rect(screen, BLACK, [vertical, 192, width-vertical, 320], 2) #Scorecard Panel
    pygame.draw.rect(screen, BLUE, [vertical, hRight, width-vertical, height], 2) #Action Panel
    
    pygame.display.flip()
    clock.tick(60)

    for event in pygame.event.get():  # User did something
        
        if event.type == pygame.QUIT:  # If user closes window
            done = True  # Flag to exit the loop
        
        if event.type == SERVER_MESSAGE: # If the server sends a message
            readmsg = event.message
            print("PRINTING READ MSG HERE")
            print(readmsg)
            print(canClickButtons)
            print("==============================")
            print("==============================")
            
            if("CLOSE ALL CONNECTION" in readmsg):
                readmsg = readmsg.split(",")
                print(readmsg)
                if(readmsg[1]) and (int(readmsg[1]) == int(p.playerNumber)):
                    print(readmsg[2])
                s.close()
                
            if CONNECTED_MSG in readmsg and waitingForSuggestion == False:
                myNumber = readmsg.split("You are Player ")[1].split(".")[0]
                if(int(myNumber) == 1):
                    print(readmsg)
                    updateNotifications(readmsg[1:]+".", "", "", "", "", "")
                    print("How many players are going to be playing in the game?")
                    #numberOfPlayers = input("->")
                    numberOfPlayers = "3" #dummy for now
                    s.send(numberOfPlayers.encode())

            if PLAYER_CHOICE_MESSAGE in readmsg and waitingForSuggestion == False:
                #readmsg = s.recv(1024).decode() # NEED TO GET RID OF THIS
                print("PLAYER CHOICE MESSAGE WAS IN READ MSG")
                print(readmsg, "\n")
                # message = input(" -> ")
                if int(myNumber) == 1: # dummy for now
                    message = "Mrs. White"
                else:
                    message = "Colonel Mustard"
                playerLocation = Game.playerStartLocations.get(message)
                p = Player(myNumber, message, playerLocation, None, False, False, False, False, False)
                sendMessage = p.playerName + "," + playerLocation
                s.send(sendMessage.encode())
                #playerMessage = s.recv(1024).decode() # NEED TO GET RID OF THIS
                #print(playerMessage)
                #readmsg = playerMessage
            
            if BEGINNING_MSG in readmsg and waitingForSuggestion == False:
                print(readmsg)
                cards = readmsg.split("Your cards are: ")[1]
                if("Next Turn" in cards):
                    cards = cards.split("N")[0]
                setattr(p, 'cards', ast.literal_eval(cards))
                playerText = p.playerName+", you are Player "+str(p.playerNumber)+"."
                cardText = cards[:-3]
                cardText = cardText.replace('[','')
                cardText = cardText.replace(']','')
                cardText = cardText.replace('\'','')
                cardText = cardText.replace('Colonel','Col.')
                cardText = cardText.replace('Reverend','Rev.')
                cardText = cardText.replace('Professor','Prof.')
                cardText = cardText+"."
                cardTextForCount = cardText.split(", ")
                print("CARD TEXT FOR COUNT:")
                print(cardTextForCount)
                updateNotifications(playerText, "", readmsg[1:34], "", "", "")

                t_card1 = Text((911+5, 33+387), "Click on cards to track what you know.", action_font, action_font, notification_color, notification_color)
                t_card1.update(screen)
                t_card2 = Text((911+5, 25+385+2*(fontHeight-2)), "Your "+str(len(cardTextForCount))+" cards are:", action_font, action_font, notification_color, notification_color)
                t_card2.update(screen)
                
                if len(cardTextForCount)==0:
                    cardLine3 = ""
                elif len(cardTextForCount)==1:
                    cardLine3 = cardTextForCount[0]
                elif len(cardTextForCount)==2:
                    cardLine3 = cardTextForCount[0]+", "+cardTextForCount[1]
                elif len(cardTextForCount)==3: 
                    cardLine3 = cardTextForCount[0]+", "+cardTextForCount[1]+", "+cardTextForCount[2]
                else:
                    cardLine3 = cardTextForCount[0]+", "+cardTextForCount[1]+", "+cardTextForCount[2]+","
                t_card3 = Text((911+5, 25+385+3*(fontHeight-2)), cardLine3, action_font, action_font, notification_color, notification_color)
                t_card3.update(screen)
                
                if len(cardTextForCount)<=3:
                    cardLine4 = ""
                elif len(cardTextForCount)==4:
                    cardLine4 = cardTextForCount[3]
                elif len(cardTextForCount)==5:
                    cardLine4 = cardTextForCount[3]+", "+cardTextForCount[4]
                elif len(cardTextForCount)==6:
                    cardLine4 = cardTextForCount[3]+", "+cardTextForCount[4]+", "+cardTextForCount[5]
                else:
                    cardLine4 = cardTextForCount[3]+", "+cardTextForCount[4]+", "+cardTextForCount[5]+","
                t_card4 = Text((911+5, 25+385+4*(fontHeight-2)), cardLine4, action_font, action_font, notification_color, notification_color)
                t_card4.update(screen)
                
                if len(cardTextForCount)<=6:
                    cardLine5 = ""
                elif len(cardTextForCount)==7:
                    cardLine5 = cardTextForCount[6]
                elif len(cardTextForCount)==8:
                    cardLine5 = cardTextForCount[6]+", "+cardTextForCount[7]
                else:
                    cardLine5 = cardTextForCount[6]+", "+cardTextForCount[7]+", "+cardTextForCount[8]
                t_card5 = Text((911+5, 25+385+5*(fontHeight-2)), cardLine5, action_font, action_font, notification_color, notification_color)
                t_card5.update(screen)
                
                print("boardSize: ", boardSize)
                print("boardLocation: ", boardLocation)
                boardImage = pygame.image.load("gameboard.png").convert() #load image
                boardImage = pygame.transform.scale(boardImage, boardSize) #transform size
                screen.blit(boardImage, boardLocation) ##populate on screen
                
            if TURN_MSG in readmsg:
                print("-------------------")
                print(readmsg)
                currentPlayerLocations = readmsg.split("|||||")[1]
                if "Player "+str(p.playerNumber) in readmsg:
                    canClickButtons = True
                else:
                    canClickButtons = False
                    p.hasMoved = False
                    p.canEndTurn = False
                    currentButtons = []
                    buttonsClicked = False
            
            if ("is suggesting" in readmsg) and canClickButtons:
                waitingForSuggestion = True
                print("WAITING")
                print("INSIDE IS SUGGESTING")
                print(readmsg)
                print(readmsg.split("///"))
                clientsMessage = readmsg.split("///")[0]

            if waitingForSuggestion == True and ("suggestionHelpMade" in readmsg):
                print("YOU ARE NOW HERE!!!!")
                print(readmsg)
                suggestionHelpMessage = readmsg.split(" ///")
                if "No player has cards that match your suggestion" in suggestionHelpMessage:
                    print("IN THIS PART NOW!!!")
                    suggestion = suggestionHelpMessage
                    print("No player has cards that match your suggestion")
                    noSuggestionFont = pygame.font.SysFont('Calibri', 14, False, False)
                    noSuggestionHelp = "No player has cards that match your suggestion."
                    noSuggestionHelpText = Text((1030, 525), noSuggestionHelp, noSuggestionFont, noSuggestionFont, (0,0,0), notification_color)
                    noSuggestionHelpText.update(screen)
                    p.hasSuggested = True
                    p.hasMoved = True
                    p.canEndTurn = True
                    msg = "KEEP SAME PLAYER TURN"
                    print(msg)
                    s.send(msg.encode(form))
                else:
                    suggestionHelp1 = "Another player is suggesting that"
                    suggestionHelpText1 = Text((1055, 525), suggestionHelp1, action_font, action_font, (0,0,0), notification_color)
                    suggestionHelpText1.update(screen)
                    suggestionHelp2 = "[ " + str(suggestionHelpMessage[0]) + " ]"
                    suggestionHelpText2 = Text((1105, 545), suggestionHelp2, action_font, action_font, (0,0,0), notification_color)
                    suggestionHelpText2.update(screen)
                    suggestionHelp3 = "is not in the solution."
                    suggestionHelpText3 = Text((1085, 565), suggestionHelp3, action_font, action_font, (0,0,0), notification_color)
                    suggestionHelpText3.update(screen)
                    msg = "KEEP SAME PLAYER TURN"
                    print(msg)
                    s.send(msg.encode(form))
                    print("Another player is suggesting that [" + str(suggestionHelpMessage[0]) + "] is not in the solution")
                    p.hasSuggested = True
                    p.hasMoved = True
                    p.canEndTurn = True
                


            if ("is suggesting" in readmsg) and (not canClickButtons):
                playerSuggesting = readmsg.split("///")[0][7]
                print("PLAYER SUGGESTING")
                print(playerSuggesting)
                cardsToCheck = readmsg.split("///")[1]
                suggestions = cardsToCheck.split(",")
                if(p.playerName == suggestions[0]):
                    keys = [k for k, v in roomsToNames.items() if v == suggestions[1]]
                    p.playerLocation = keys[0]
                    p.canSuggest = True
                if p.playerNumber in cardsToCheck:
                    print("INSIDE HERE SO ADD CHECK FOR SUGGESTION HELPER")
                    print(readmsg)
                    print(readmsg.split("///"))
                    # nextPlayer = int(suggestions[3])
                    count = 0
                    # if(int(p.playerNumber) == nextPlayer):
                    matches = []
                    playerCards = getattr(p, 'cards')
                    if((suggestions[0] in p.cards) or (suggestions[1] in p.cards) or (suggestions[2] in p.cards)):
                        count += 1
                        for i in suggestions:
                            if i in p.cards:
                                matches.append(i)
                        print("CHEKING THIS")
                        print(playerSuggesting)
                        print("You have a card to disprove an item in player " + str(playerSuggesting) + "'s suggestion. ")
                        print("Your options to show player " +str(playerSuggesting) + " are " + str(matches))
                        print("Which would you like to show?")
                        p.helpingSuggestion = True
                        helpButtons = printSuggestionHelpButtons(playerSuggesting, matches)
                        currentButtons = helpButtons
                        print("HERE IN SUGGESTION HELP LOGIC")
                        # message = input(" -> ")
                        # s.send(message.encode())
                    else:
                        count += 1
                        message = "No matches please move to next player"
                        s.send(message.encode())
                    nextMessage = "Move " + suggestions[0] + " to " + suggestions[1] + ".\n"
                    print(nextMessage)
                    playerMoveActive = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if canClickButtons:
                print("INSIDE THIS PART!!!")
                print(currentButtons)
                if b_move.isOver(pos, button_width_1, button_height):
                    print("NOW WE MADE IT HERE")
                    print("MOVE CHOICE WAS MADE")
                    print(p.hasMoved)
                    if p.hasMoved == False:
                        moveOptions = movePlayer(p, currentPlayerLocations)
                        if moveOptions == "NO POSSIBLE OPTIONS":
                            moveInput1 = "Your move options are all blocked."
                            moveInput2 = "You can either accuse or end your turn."
                            blockedText1 = Text((1070, 525), moveInput1, action_font, action_font, (0,0,0), notification_color)
                            blockedText2 = Text((1050, 540), moveInput2, action_font, action_font, (0,0,0), notification_color)
                            blockedText1.update(screen)
                            blockedText2.update(screen)
                            msg = "KEEP SAME PLAYER TURN"
                            print(msg)
                            s.send(msg.encode(form))
                            # pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                            # pygame.display.update()
                            currentButtons = []
                            # print(moveInput)
                            ##### UPDATE NOTIFICATION HERE!!!!!!! ####
                        else:
                            buttonList = moveOptionButtons(moveOptions)
                            print("&&&&&&&&&&")
                            print(buttonList)
                            currentButtons = buttonList
                    else: 
                        updateNotifications("", "You can only move once per turn.", "", "", "", "")
                        pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                        pygame.display.update()
                        noDoubleMove = "You can only move once per turn."
                        noDoubleMoveText = Text((1070, 525), noDoubleMove, action_font, action_font, (0,0,0), notification_color)
                        noDoubleMoveText.update(screen)
                        currentButtons = []
                        # pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                        # pygame.display.update()
                        msg = "KEEP SAME PLAYER TURN"
                        print(msg)
                        s.send(msg.encode(form))
                    # message = "move" 
                    # print('moving')
                    # s.send(message.encode())
                    
                if currentButtons != []:
                    print("CURRENT BUTTONS ISNT AN EMPTY LIST")
                    for button in currentButtons:
                        theButton = Button(button.image, (button.x_pos, button.y_pos), button.text_input, button.font, button.base_color, button.hovering_color)
                        if theButton.isOver(pos, theButton.rect.width, theButton.rect.height):
                            print(theButton.text_input)
                            clickedButton = theButton
                            buttonsClicked = True
                            print(buttonsClicked)
                            if suggesting == True:
                                print("SUGGESTING IS TRUE")
                                if clickedButton.text_input in names:
                                    personSuggested = clickedButton.text_input
                                    currentButtons = []
                                    buttonsClicked = False
                                    pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                                    pygame.display.update()
                                    weaponButtons = printWeaponButtons()
                                    currentButtons = weaponButtons
                                if clickedButton.text_input in weapons:
                                    weaponSuggested = clickedButton.text_input
                                    currentButtons = []
                                    buttonsClicked = False
                                    print("WEAPON SUGGESTED")
                                    print(weaponSuggested)
                                    pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                                    pygame.display.update()
                                    roomSuggested = p.playerLocation
                                    all = "suggest !!!" + personSuggested + "," + roomSuggested + "," + weaponSuggested
                                    print("INSIDE HANDLING SUGGESTION IN CLIENT")
                                    print(all)
                                    s.send(all.encode())
                                    print("Move " + personSuggested + " to " + roomSuggested + ".\n")
                                    print(",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")

                    if buttonsClicked == True:
                        # if(p.hasMoved == False) and (p.helpingSuggestion == False):
                        if(p.hasMoved == False):
                            print("INSIDE HERE")
                            ### NEED TO FIGURE OUT HOW TO MAKE MULTIPLE BUTTONS APPEAR ####
                            print("PRINTING BUTTON TEXT INPUT")
                            print(clickedButton.text_input)
                            print(choiceInput)
                            moveInput = clickedButton.text_input
                            print("PRINTING MOVE INPUT HERE")
                            print(moveInput)
                            if "room" not in moveInput:
                                p.playerLocation = moveInput
                                msg = "\nmove---" + p.playerName + "---" + p.playerLocation
                                print(msg)
                                # p.hasSuggested = True   
                                p.canEndTurn = True 
                                p.canSuggest = False

                            elif("room" in moveInput):
                                p.playerLocation = moveInput
                                print("\nmove " + p.playerName + " to " + p.playerLocation + ".")
                                msg = "\nmove---" + p.playerName + "---" + p.playerLocation
                                # msg = "Player must now suggest"
                                p.canEndTurn = False
                                p.hasSuggested = False
                                p.canSuggest = True
                                print(msg)

                            p.hasMoved = True
                            print("THIS IS THE MESSAGE MOVE WILL SEND")
                            print(msg)
                            s.send(msg.encode(form))
                            print(p.hasMoved)
                            currentButtons = []
                            pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                            pygame.display.update()


                if b_suggest.isOver(pos, button_width_1, button_height):
                    print('suggesting')
                    suggestionValidation = validateSuggestion(p)
                    if(suggestionValidation == True):
                        suggesting = True
                        playerButtons = printPlayerButtons()
                        currentButtons = playerButtons
                        print("HERE")
                    else:
                        print("IN CLIENT AND PLAYER CANNOT SUGGEST NOW")
                        pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                        pygame.display.update()
                        if p.hasSuggested:
                            noSuggesting = "You cannot make another suggestion."
                            noSuggestingText = Text((1070, 525), noSuggesting, action_font, action_font, (0,0,0), notification_color)
                            noSuggestingText.update(screen)
                        elif p.canSuggest == False and p.hasMoved:
                            noSuggesting = "You are not in a location to suggest."
                            noSuggestingText = Text((1070, 525), noSuggesting, action_font, action_font, (0,0,0), notification_color)
                            noSuggestingText.update(screen)
                        else:
                            noSuggesting = "You must either move or make a suggestion."
                            noSuggestingText = Text((1070, 525), noSuggesting, action_font, action_font, (0,0,0), notification_color)
                            noSuggestingText.update(screen)
                        msg = "KEEP SAME PLAYER TURN"
                        print(msg)
                        s.send(msg.encode(form))

                if b_end.isOver(pos, button_width_2, button_height):
                    print('ending')
                    # canTurnEnd = validateEndTurn(p)

                    # def validateEndTurn(p):
                    if(p.canEndTurn == True):
                        p.canSuggest = False
                        msg = "end \n"
                        print("<<<<!!!!!!!!!!!!<<<<<<<<<<<<<")
                        print(msg)
                        s.send(msg.encode(form))
                        print("<<<<<<<<<<<<<<<<<")
                        pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                        pygame.display.update()
                            
                    else:
                        if(p.canSuggest and not p.hasMoved):
                            # msg = "\nYou must either move or make a suggestion. && " + str(p.canEndTurn)
                            pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                            pygame.display.update()
                            endMsg1 = "You must either move or make a suggestion."
                            noEnd1 = Text((1070, 525), endMsg1, action_font, action_font, (0,0,0), notification_color)
                            noEnd1.update(screen)
                        if(p.canSuggest and p.hasMoved):
                            # msg = "\nYou must make a suggestion. && " + str(p.canEndTurn)
                            pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                            pygame.display.update()
                            endMsg2 = "You must make a suggestion."
                            noEnd2 = Text((1070, 525), endMsg2, action_font, action_font, (0,0,0), notification_color)
                            noEnd2.update(screen)
                        if(not p.canSuggest and p.hasMoved):
                            # msg = "\nYou must move to a new location. && " + str(p.canEndTurn)
                            pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                            pygame.display.update()
                            endMsg3 = "You are not in a location to suggest."
                            noEnd3 = Text((1070, 525), endMsg3, action_font, action_font, (0,0,0), notification_color)
                            noEnd3.update(screen)
                        if(not p.canSuggest and not p.hasMoved):
                            # msg = "\nYou must move to a new location. && " + str(p.canEndTurn)
                            pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                            pygame.display.update()
                            endMsg4 = "You must make a move to a new location."
                            noEnd4 = Text((1055, 525), endMsg4, action_font, action_font, (0,0,0), notification_color)
                            noEnd4.update(screen)
                        msg = "KEEP SAME PLAYER TURN"
                        print(msg)
                        s.send(msg.encode(form))
                        print("//////////")

            elif p.helpingSuggestion == True:
                print(currentButtons)
                print("HELPING SUGGESTIONS SO CAN CLICK")
                suggestionHelp = ""
                for button in currentButtons:
                    if button.isOver(pos, button.rect.width, button.rect.height):
                        print(button)
                        suggestionHelp = button.text_input
                pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                pygame.display.update()
                print("SUGGESTION HELP HERE")
                print(suggestionHelp)
                s.send(suggestionHelp.encode(form))
                print("SENT!")


pygame.quit()
s.close()
