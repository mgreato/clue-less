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

pygame.init()
pygame.event.clear()

class DropDown():
    def __init__(self, x, y, w, h, color, highlight_color, font, option_list, selected = 0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.highlight_color if i == self.active_option else self.color, rect)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center = rect.center))
            outer_rect = (self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_active:
                self.draw_menu = not self.draw_menu
            elif self.draw_menu and self.active_option >= 0:
                self.selected = self.active_option
                self.draw_menu = False
                return self.active_option
        return -1

    def isOver(self, position, button_width, button_height):
        x_p = self.rect.topleft[0]-button_width/2
        y_p = self.rect.topleft[1]-button_height/2
        if position[0] > x_p and position[0] < x_p + button_width:
            if position[1] > y_p and position[1] < y_p + button_height:
                return True
        return False

# possible messages from server
CONNECTED_MSG = "Connection established"
BEGINNING_MSG = "Game is beginning"
TURN_MSG = "Next Turn"
MOVE_MSG = "another"
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
    print("SHOULD DRAW RECTANGLE NOW")
    # Drawing Rectangle
    # textBox = pygame.draw.rect(screen, BLUE, [925, 525, 160, 40], 2)
    size = (150, 75)
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
            option = Button(buttonType, (750+x, 315+y), option, font, (0,255,255), (0,50,50))
            buttonList.append(option)
            option.update(screen)
            x += 170
            buttonCount += 1
        else:
            print("EVEN")
            print(x)
            print(y)
            option = Button(buttonType, (750+x, 315+y), option, font, (0,255,255), (0,50,50))
            buttonList.append(option)
            option.update(screen)
            y += 250
            buttonCount += 1
        pygame.display.update()
    return buttonList
    # if dropDown.isOver(mpos, dropDown.rect.topleft[0], dropDown.rect.topleft[1]):
    #     selected_option = dropDown.update(event_list)
    #     if selected_option >= 0:
    #         print(selected_option)
    
    # dropDown.draw(screen)

def whereToMove(p, moveTo, otherPlayerLocations):
    otherPlayerLocationsList = [h for h in ast.literal_eval(otherPlayerLocations) if ("room" not in h)]
    validMove = False
    while validMove == False:
        moveInput = moveTo
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


def movePlayer(p, otherPlayerLocations, screen):
    otherPlayerLocationsList = [h for h in ast.literal_eval(otherPlayerLocations) if ("room" not in h)]
    playerInRoom = p.playerLocation.__contains__("room")
    if(playerInRoom):
        roomNumber = p.playerLocation.split("room")[1]
        possibleHallways = [h for h in locations if (("hallway" and roomNumber in h) and ("room" not in h) and (h not in otherPlayerLocationsList))]
        check_diagonal_result = can_take_secret_passage(p.playerLocation)
    if(p.playerLocation == "None"):
        possibleHallways = playerFirstLocations.get(p.playerName)
        print(str(possibleHallways))
        print([possibleHallways])
        print(type(possibleHallways))
        print("Where would you like to move? Your first move must be to: " + str(possibleHallways))
        return [possibleHallways]
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
            return possibleRooms
        if(playerInRoom):
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

# def movePlayer(p, otherPlayerLocations): # break into 2 functions - first populates drop down correctly, second actually does action
    # otherPlayerLocationsList = [h for h in ast.literal_eval(otherPlayerLocations) if ("room" not in h)]
    # playerInRoom = p.playerLocation.__contains__("room")
    # if(playerInRoom):
    #     roomNumber = p.playerLocation.split("room")[1]
    #     possibleHallways = [h for h in locations if (("hallway" and roomNumber in h) and ("room" not in h) and (h not in otherPlayerLocationsList))]
    #     check_diagonal_result = can_take_secret_passage(p.playerLocation)
    # if(p.playerLocation == "None"):
    #     possibleHallways = playerFirstLocations.get(p.playerName)
    #     print("Where would you like to move? Your first move must be to: " + str(possibleHallways))
    # if(p.hasMoved == True):
    #     moveInput = "You can only move once per turn."
    #     print(moveInput)
    #     s.send(moveInput.encode())
    #     clientsMessage = s.recv(1024).decode()
    # elif(playerInRoom) and (len(possibleHallways) == 0) and (check_diagonal_result[0] == False):
    #     moveInput = "Your move options are all blocked. You can either make an accusation or end your turn."
    #     print(moveInput)
    #     s.send(moveInput.encode())
    #     clientsMessage = s.recv(1024).decode()
    #     print(clientsMessage)
    # else:
    #     if(p.playerLocation.__contains__("hallway")):
    #         hallwayRooms = p.playerLocation.split("hallway")[1]
    #         roomChoices = list(hallwayRooms)
    #         roomChoice1 = "room" + roomChoices[0]
    #         roomChoice2 = "room" + roomChoices[1]
    #         possibleRooms = []
    #         possibleRooms.append(roomChoice1)
    #         possibleRooms.append(roomChoice2)
    #         print("Where would you like to move? Your choices are: " + str(possibleRooms))
    #     if(playerInRoom):
    #         if check_diagonal_result[0] == True:
    #             if(len(possibleHallways) == 0):
    #                 print("Where would you like to move? Your only option is:  " + check_diagonal_result[1])
    #             else:
    #                 print("Where would you like to move? Your hallway choices are: " + str(possibleHallways) + ". Your diagonal room choice is: " + check_diagonal_result[1])
    #         else:
    #             print("Where would you like to move? Your choices are: " + str(possibleHallways))
    #     validMove = False
    #     while validMove == False:
    #         moveInput = input("->")
    #         if(moveInput not in otherPlayerLocationsList):
    #             validMove = True
    #         else:
    #             print("That room is already occupied, please enter another choice.")
    #     if("room" not in moveInput):
    #         p.hasSuggested = True   
    #         p.canEndTurn = True 
    #     moveMessage = moveInput + "," + p.playerName
    #     s.send(moveMessage.encode())
    #     clientsMessage = s.recv(1024).decode()
    #     p.hasMoved = True
    # return moveInput #actual moving of player happens later - this just gets a VALID move from player, which it returns

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

boardImage = pygame.image.load("board_image.png").convert() #load image
boardImage = pygame.transform.scale(boardImage, boardSize) #transform size
background_image = pygame.image.load("background.png").convert() #image to be used as button background PLAY WITH THIS
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
info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
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
info_text = info_font.render("click on cards to mark if you've seen them", True, BLACK) #
screen.blit(info_text, ((920, 450))) # populate on screen
# Names
t_x = vertical + (info_width/2)
t_y_1 = 195 + (info_height/2)
t_y = t_y_1
t_names = Button(button_type_3, (t_x, t_y), "NAMES", info_font, info_color, info_greyed_color)
#t_names = Text((t_x, t_y), "NAMES", info_font, info_font_bold, info_title_color, info_greyed_color)
t_names.update(screen)
# NOTE the following could be done in a loop like "for names in names_list", but I don't know how to create objects of unique names doing so

# Mustard
t_y = t_y_1 + info_y_shift
t_mustard= Button(button_type_3, (t_x, t_y), "Col. Mustard", info_font, info_color, info_greyed_color)
t_mustard.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   a boldText() function will have to be made in Button

# Peacock
t_y = t_y + info_y_shift
t_peacock= Button(button_type_3, (t_x, t_y), "Mrs. Peacock", info_font, info_color, info_greyed_color)
t_peacock.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Plum
t_y = t_y + info_y_shift
t_plum= Button(button_type_3, (t_x, t_y), "Prof. Plum", info_font, info_color, info_greyed_color)
t_plum.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Scarlet
t_y = t_y + info_y_shift
t_scarlet= Button(button_type_3, (t_x, t_y), "Ms. Scarlet", info_font, info_color, info_greyed_color)
t_scarlet.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# White
t_y = t_y + info_y_shift
t_white= Button(button_type_3, (t_x, t_y), "Mrs. White", info_font, info_color, info_greyed_color)
t_white.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Weapons
t_x = t_x + info_width # shift to the right for a new "column"
t_y = t_y_1
t_weapons = Button(button_type_3, (t_x, t_y), "WEAPONS", info_font, info_color, info_greyed_color)
t_weapons.update(screen)

# Candlestick
t_y = t_y + info_y_shift
t_candle= Button(button_type_3, (t_x, t_y), "Candlestick", info_font, info_color, info_greyed_color)
t_candle.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Dagger
t_y = t_y + info_y_shift
t_dagger= Button(button_type_3, (t_x, t_y), "Dagger", info_font, info_color, info_greyed_color)
t_dagger.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Lead Pipe
t_y = t_y + info_y_shift
t_pipe= Button(button_type_3, (t_x, t_y), "Lead Pipe", info_font, info_color, info_greyed_color)
t_pipe.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Rope
t_y = t_y + info_y_shift
t_rope= Button(button_type_3, (t_x, t_y), "Rope", info_font, info_color, info_greyed_color)
t_rope.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Wrench
t_y = t_y + info_y_shift
t_wrench= Button(button_type_3, (t_x, t_y), "Wrench", info_font, info_color, info_greyed_color)
t_wrench.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Rooms
t_x = t_x + info_width # shift to the right for a new "column"
t_y = t_y_1
t_rooms = Button(button_type_3, (t_x, t_y), "ROOMS", info_font, info_color, info_greyed_color)
t_rooms.update(screen)

# Study
t_y = t_y + info_y_shift
t_study= Button(button_type_3, (t_x, t_y), "Study", info_font, info_color, info_greyed_color)
t_study.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Hall
t_y = t_y + info_y_shift
t_hall= Button(button_type_3, (t_x, t_y), "Hall", info_font, info_color, info_greyed_color)
t_hall.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Lounc
t_y = t_y + info_y_shift
t_lounge= Button(button_type_3, (t_x, t_y), "Lounge", info_font, info_color, info_greyed_color)
t_lounge.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Library
t_y = t_y + info_y_shift
t_library= Button(button_type_3, (t_x, t_y), "Library", info_font, info_color, info_greyed_color)
t_library.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Billiard Room
t_y = t_y + info_y_shift
t_billiard= Button(button_type_3, (t_x, t_y), "Billiard", info_font, info_color, info_greyed_color)
t_billiard.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Dining Room
t_y = t_y + info_y_shift
t_dining= Button(button_type_3, (t_x, t_y), "Dining", info_font, info_color, info_greyed_color)
t_dining.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Conservatory
t_y = t_y + info_y_shift
t_conservatory= Button(button_type_3, (t_x, t_y), "Conservatory", info_font, info_color, info_greyed_color)
t_conservatory.update(screen)

# Ballroom
t_y = t_y + info_y_shift
t_ballroom= Button(button_type_3, (t_x, t_y), "Ballroom", info_font, info_color, info_greyed_color)
t_ballroom.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

# Kitchen
t_y = t_y + info_y_shift
t_kitchen= Button(button_type_3, (t_x, t_y), "Kitchen", info_font, info_color, info_greyed_color)
t_kitchen.update(screen)
##ADD LOGIC FOR ITEM TO BOLD IF USER HAS CARD
#if "user has this card in their deck":
#   boldText()

################################
# Notifications
################################# 
# what player are you
t_x = vertical + 5
t_y = 5
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

t_x_notification2 = t_x
t_y_notification2 = t_y + 3*notification_y_shift
t_notification2= Text((t_x_notification2, t_y_notification2), "Initial", notification_font, info_font_bold, notification_color, notification_color)
t_notification2.update(screen)

def updateNotifications(text1, text2, text3, text4):
    t_you = Text((t_x_you, t_y_you), text1, notification_font, info_font_bold, notification_color, notification_color)
    t_you.update(screen)
    t_cards = Text((t_x_cards, t_y_cards), text2, notification_font, info_font_bold, notification_color, notification_color)
    t_cards.update(screen)
    t_notification= Text((t_x_notification, t_y_notification), text3, notification_font, info_font_bold, notification_color, notification_color)
    t_notification.update(screen)
    t_notification2= Text((t_x_notification2, t_y_notification2), text4, notification_font, info_font_bold, notification_color, notification_color)
    t_notification2.update(screen)

playerText = ""
cardText = ""

choiceInput = ""
moveChoiceMade = False
currentButtons = []
buttonsClicked = False
clickedButton = ""
myNumber = 0

canClickButtons = False
done = False
clock = pygame.time.Clock()
while not done:
    pygame.draw.rect(screen, BLACK, [0, 0, vertical, height], 2) #Draw a rectangle around the map
    pygame.draw.rect(screen, RED, [vertical, 0, width, 192], 2) #Notification Palen
    pygame.draw.rect(screen, BLUE, [vertical, hRight, width, height], 2) #Action Panel
    
    pygame.display.flip()
    clock.tick(60)

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user closes window
            done = True  # Flag to exit the loop
        
        if event.type == SERVER_MESSAGE: # If the server sends a message
            readmsg = event.message
            print("PRINTING READ MSG HERE")
            print(readmsg)
            
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
                    updateNotifications(readmsg[1:]+".", "", "", "")
                    print("How many players are going to be playing in the game?")
                    numberOfPlayers = input("->")
                    # numberOfPlayers = "2" #dummy for now
                    s.send(numberOfPlayers.encode())

            if PLAYER_CHOICE_MESSAGE in readmsg:
                #readmsg = s.recv(1024).decode() # NEED TO GET RID OF THIS
                print(readmsg, "\n")
                # message = input(" -> ")
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
                playerText = p.playerName+", you are Player "+str(p.playerNumber)+"."
                cardText = readmsg[38:-2]
                cardText = cardText.replace('[','')
                cardText = cardText.replace(']','')
                cardText = cardText.replace('\'','')
                cardText = cardText+"."
                updateNotifications(playerText, cardText, readmsg[1:34], "")     

            if WIN_MSG in readmsg:
                pass # dummy right now
            if LOSE_MSG in readmsg:
                pass # dummy right now
                
            if ((TURN_MSG or MOVE_MSG) in readmsg) or (SUGGESTION in readmsg):
                suggestionValidation = None
                print("-------------------")
                print(readmsg)
                if "Player "+str(p.playerNumber) in readmsg:
                    canClickButtons = True
                    playerMoveActive = True # CAN I USE THIS TO ALLOW BUTTON CLICKS?
                else:
                    canClickButtons = False
                    playerMoveActive = False
                    p.hasSuggested = False
                    p.hasMoved = False
                    choiceInput = ""
                    moveChoiceMade = False
                    clickedButton = ""
                    buttonsClicked = False
                    currentButtons = []
            
            if "move" in readmsg and canClickButtons:
                choiceInput = readmsg.split("//")
                print(choiceInput)
                choice = choiceInput[0]
                player_choice = choice[1:]
                if("," in player_choice):
                    player_choice = player_choice.split(",")[0]
                moveChoiceMade = True
                print("PRINTING CHOICE INPUT")
                print(choiceInput)
                if moveChoiceMade:
                    print("MOVE CHOICE WAS MADE")
                    moveOptions = movePlayer(p, choiceInput[1], screen)
                    if moveOptions != "You can only move once per turn.":
                        buttonList = moveOptionButtons(moveOptions)
                        print("&&&&&&&&&&")
                        print(buttonList)
                        currentButtons = buttonList
            
            if "end" in readmsg and canClickButtons and ("rend" not in readmsg):
                print("PRINTING END HERE!!!!")
                # end = s.recv(1024).decode()
                print("PRINTING END HERE!!!!")
                # print(end)
                msg = "\nTurn Over. && " + str(p.canEndTurn)
                print("<<<<!!!!!!!!!!!!<<<<<<<<<<<<<")
                print(msg)
                s.send(msg.encode(form))
                # s.send("END".encode(form))
                print("^^^^^^^^^^^^^^^^^^^^^^^^")
                # if "//" in end:
                #     choiceInput = end
                # else:
                # choiceInput = s.recv(1024).decode().split("//")
                # print("***********")
                # playerMoveActive = False
                # print(choiceInput)
                # choice = choiceInput[0]
                # player_choice = choice[1:]
                # if("," in player_choice):
                #     player_choice = player_choice.split(",")[0]
                print("HERE AT THE BOTTOM OF END")
                # s.send("END".encode(form))
                # end = s.recv(1024).decode()
            
            if "end" in readmsg and (not canClickButtons) and ("rend" not in readmsg):
                player = readmsg.split("//")[0].split(",")[1]
                print("($#*@!(*(*!$(*$(!$)!@*($!@$#@")
                print(player)
                # message = s.recv(1024).decode()
                if(message == "True"):
                    print("Player " + player + " chose to end their turn.")
                playerMoveActive = False


        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # if ((TURN_MSG or MOVE_MSG) in readmsg) or (SUGGESTION in readmsg):
            #    suggestionValidation = None
            #    if "Player "+str(p.playerNumber) in readmsg:
            #        canClickButtons = True
            #        playerMoveActive = True # CAN I USE THIS TO ALLOW BUTTON CLICKS?
            #    else:
            #        canClickButtons = False
            if canClickButtons:
                if b_move.isOver(pos, button_width_1, button_height):
                    message = "move" 
                    print('moving')

                    s.send(message.encode())
                    # choiceInput = s.recv(1024).decode().split("//")
                    print("***********")
                    # print(choiceInput)
                    # choice = choiceInput[0]
                    # player_choice = choice[1:]
                    # if("," in player_choice):
                    #     player_choice = player_choice.split(",")[0]

                    # # if player_choice == "move":
                    # moveInput = movePlayer(p, choiceInput[1], screen)
                    

                if currentButtons != []:
                    for button in currentButtons:
                        if button.isOver(pos, button.x_pos, button.y_pos):
                            clickedButton = button
                            buttonsClicked = True


                if buttonsClicked == True:
                    if(p.hasMoved == False):
                        print("INSIDE HERE")
                        ### NEED TO FIGURE OUT HOW TO MAKE MULTIPLE BUTTONS APPEAR ####
                        print("PRINTING BUTTON TEXT INPUT")
                        print(clickedButton.text_input)
                        print(choiceInput)
                        moveInput = whereToMove(p, clickedButton.text_input, choiceInput[1])
                        print(moveInput)

                            # inputGiven = False
                            # # while moveInput == False:

                            # while inputGiven == False:
                            #     pygame.event.clear()
                            #     eventlist = pygame.event.get()
                            #     for event in eventlist:
                            #         if event.type == pygame.MOUSEBUTTONDOWN:
                            #             print("INSIDE HERE")
                            #             print(event)
                            #             ### NEED TO FIGURE OUT HOW TO MAKE MULTIPLE BUTTONS APPEAR ####
                            #             if buttonList[0].isOver(pos, buttonList[0].x_pos, buttonList[0].y_pos):
                            #                 print("PRINTING BUTTON TEXT INPUT")
                            #                 print(buttonList[0].text_input)
                            #                 moveInput = whereToMove(p, buttonList[0].text_input, choiceInput[1])
                            #                 print(moveInput)
                            #                 inputGiven = True
                            #             else:
                            #                 inputGiven = False


                        # print(moveOptions)
                        print("&&&&&&&")
                        print(moveInput)
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
                        print("IS PLAYER MOVE ACTIVE")
                        print(playerMoveActive)
                        pygame.draw.rect(screen, WHITE, [913, 516, 350, 201])
                        pygame.display.update()

                        # pygame.draw.rect(screen, WHITE, [0, hLeft, vertical, height])
                        # done = True


                if b_accuse.isOver(pos, button_width_1, button_height):
                    print('accusing')
                    message = "accuse"
                    s.send(message.encode())
                    choiceInput = s.recv(1024).decode().split("//")
                    print("***********")
                    print(choiceInput)
                    choice = choiceInput[0]
                    player_choice = choice[1:]
                    if("," in player_choice):
                        player_choice = player_choice.split(",")[0]


                    # if player_choice == "accuse":
                    msg = makeAccusation()
                    s.send(msg.encode())
                    if(msg == "endConnection for all"):
                        s.close()
                    playerMoveActive = False

                if b_suggest.isOver(pos, button_width_1, button_height):
                    print('suggesting')
                    # if player_choice == "suggest":
                    message = "suggest"
                    s.send(message.encode())
                    choiceInput = s.recv(1024).decode().split("//")
                    print("***********")
                    print(choiceInput)
                    choice = choiceInput[0]
                    player_choice = choice[1:]
                    if("," in player_choice):
                        player_choice = player_choice.split(",")[0]


                    suggestionValidation = validateSuggestion(p)
                    if(suggestionValidation == True):
                        handleSuggestion()
                        playerMoveActive = False
                    else:
                        print("You are are not able to make a suggestion \n")
                        suggestionError = "Player cannot make a suggestion!!!! \n"
                        s.send(suggestionError.encode())
                        playerMoveActive = False

                if b_show.isOver(pos, button_width_1, button_height):
                    message = "show"

                if b_end.isOver(pos, button_width_2, button_height):
                    print('ending')
                    message = "end"
                    s.send(message.encode())
                    
                    # if player_choice == "end":
                    canTurnEnd = validateEndTurn(p)
                    print("CAN PLAYER END TURN?")
                    print(canTurnEnd)
                    if(canTurnEnd == True):
                        msg = "\nTurn Over. && " + str(p.canEndTurn)
                        print("<<<<!!!!!!!!!!!!<<<<<<<<<<<<<")
                        print(msg)
                        s.send(msg.encode(form))
                        print("<<<<<<<<<<<<<<<<<")
                        # end = s.recv(1024).decode()
                        # print(end)
                        # s.send("END".encode(form))
                        # playerMoveActive = False
                        # done = True
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
                        # end = s.recv(1024).decode()
                        # s.send("END".encode(form))
                        playerMoveActive = False
                        print("//////////")
                        # done = True

                    
                    # msg = "\nTurn Over. && " + str(p.canEndTurn)
                    # s.send(msg.encode(form))
                    # end = s.recv(1024).decode()
                    # s.send("END".encode(form))
                    # playerMoveActive = False
                    # done = True
    pygame.event.clear()    

pygame.quit()
s.close()
