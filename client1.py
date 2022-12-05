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


mustardChosen = False
peacockChosen = False
plumChosen = False
scarletChosen = False
whiteChosen = False
greenChosen = False

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
            option = Button(buttonType, (850+x, 315+y), option, font, (0,255,255), (0,50,50))
            buttonList.append(option)
            option.update(screen)
            x += 170
            buttonCount += 1
        else:
            print("EVEN")
            print(x)
            print(y)
            option = Button(buttonType, (850+x, 315+y), option, font, (0,255,255), (0,50,50))
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
        # clientsMessage = s.recv(1024).decode()
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

def printPlayerButtons():
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
    return helpButtons
    

def handleSuggestion(suggestPerson, suggestRoom, suggestWeapon):
# def handleSuggestion():
    print("Who would you like to suggest?")

    suggestPersonInput = suggestPerson
    suggestRoomInput = suggestRoom
    suggestWeaponInput = suggestWeapon
    all = suggestPersonInput + "," + suggestRoomInput + "," + suggestWeaponInput
    s.send(all.encode())
    print("Move " + suggestPersonInput + " to " + suggestRoomInput + ".\n")
    print(",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
    # while empty == True:
    #     clientsMessage = s.recv(1024).decode().split("///")[0]
    #     if(clientsMessage != ""):
    #         empty = False

    # again = True
    # while (again == True) and (clientsMessage != "No Matches for this client"):
    #     suggestionHelpMessage = s.recv(1024).decode()
    #     if((suggestionHelpMessage != "") or (suggestionHelpMessage != None)) and ("is suggesting" not in suggestionHelpMessage) and (("Next" not in suggestionHelpMessage)):
    #         again = False
    # if(" ///" in suggestionHelpMessage):
    #     suggestion = suggestionHelpMessage.split(" ///")[0]
    #     print("Another player is suggesting that [" + suggestion + "] is not in the solution")
    # else:
    #     suggestion = suggestionHelpMessage
    #     print("No players had cards that matched your suggestion")
    # msg = "\n SUGGEST " + suggestPersonInput + " in the " + roomsToNames.get(suggestRoomInput) + " with the " + suggestWeaponInput + "\n"
    # s.send(msg.encode(form))
    # p.hasSuggested = True
    # p.hasMoved = True
    # p.canEndTurn = True

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
button_height = 64
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

button_y_shift = (button_height) #y-shift (spacing) of buttons PLAY WITH THIS

button_x_shift = (150) #y-shift (spacing) of buttons PLAY WITH THIS

# Initialize and update individual BUTTONs: image, pos, text_input, font, base_color, hovering_color)
# Move Button
b_x = width - 455 + (button_width_1/2)
b_y = 512 + button_height/2
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
#b_y = b_y + button_y_shift
#b_show = Button(button_type_1, (b_x, b_y), "Show", button_font, button_color, button_greyed_color)
#b_show.update(screen)
# End Button
b_x = width - (button_width_2/2)
b_y = b_y + button_y_shift
b_end = Button(button_type_2, (b_x, b_y), "End Turn", button_font, button_color, button_greyed_color)
b_end.update(screen)

# Initialize Start Buttons
b_width_start = 140
b_height_start = 64
dist_between_buttons = 10
b_x_start = 10+b_width_start/2
b_y_start = 384+b_height_start/2
button_size_start = (b_width_start, b_height_start)
button_type_start = pygame.transform.scale(button_image, button_size_start) #transform size


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
t_scarlet= Button(button_type_3, (t_x, t_y), "Miss Scarlett", info_font, info_color, info_greyed_color)
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

# Green
t_y = t_y + info_y_shift
t_green= Button(button_type_3, (t_x, t_y), "Rev. Green", info_font, info_color, info_greyed_color)
t_green.update(screen)
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

# Revolver
t_y = t_y + info_y_shift
t_revolver= Button(button_type_3, (t_x, t_y), "Revolver", info_font, info_color, info_greyed_color)
t_revolver.update(screen)
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
t_x = vertical + 5
t_y = 5
fontHeight = 18
t_line1 = Text((vertical+5, 5), "", notification_font, info_font_bold, notification_color, notification_color)
t_line1.update(screen)
t_line2 = Text((vertical+5, 5+1*fontHeight), "", notification_font, info_font_bold, notification_color, notification_color)
t_line2.update(screen)
t_line3 = Text((vertical+5, 5+2*fontHeight), "", notification_font, info_font_bold, notification_color, notification_color)
t_line3.update(screen)
t_line4 = Text((vertical+5, 5+3*fontHeight), "", notification_font, info_font_bold, notification_color, notification_color)
t_line4.update(screen)
t_line5 = Text((vertical+5, 5+4*fontHeight), "", notification_font, info_font_bold, notification_color, notification_color)
t_line5.update(screen)
t_line6 = Text((vertical+5, 5+5*fontHeight), "", notification_font, info_font_bold, notification_color, notification_color)
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
    
playerText = ""
cardText = ""

choiceInput = ""
moveChoiceMade = False
currentButtons = []
buttonsClicked = False
clickedButton = ""
myNumber = 0

first_beginning_screen = False
second_beginning_screen = False
suggesting = False
personSuggested = ""
weaponSuggested = ""
roomSuggested = ""
collectSuggestionHelp = False
waitingForSuggestion = False
suggestionHelpPlayer = 0
gameStarted = False

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
            print("==============================")
            print("==============================")
            
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
                    updateNotifications(readmsg[1:]+".", "", "", "", "", "")
                    print("How many players are going to be playing in the game?")
                    first_beginning_screen = True
                    second_beginning_screen = False
                    firstBoardImage = pygame.image.load("firstStartScreen.png").convert()
                    firstBoardImage = pygame.transform.scale(firstBoardImage, boardSize)
                    screen.blit(firstBoardImage, boardLocation)
                    
                    b_x_start_updated = b_x_start+75
                    b_start2 = Button(button_type_start, (b_x_start_updated+0*(b_width_start+dist_between_buttons), b_y_start), "2", button_font, button_color, button_greyed_color)
                    b_start2.update(screen)

                    b_start3 = Button(button_type_start, (b_x_start_updated+1*(b_width_start+dist_between_buttons), b_y_start), "3", button_font, button_color, button_greyed_color)
                    b_start3.update(screen)

                    b_start4 = Button(button_type_start, (b_x_start_updated+2*(b_width_start+dist_between_buttons), b_y_start), "4", button_font, button_color, button_greyed_color)
                    b_start4.update(screen)

                    b_start5 = Button(button_type_start, (b_x_start_updated+3*(b_width_start+dist_between_buttons), b_y_start), "5", button_font, button_color, button_greyed_color)
                    b_start5.update(screen)

                    b_start6 = Button(button_type_start, (b_x_start_updated+4*(b_width_start+dist_between_buttons), b_y_start), "6", button_font, button_color, button_greyed_color)
                    b_start6.update(screen)
                    #numberOfPlayers = input("->")
                    #numberOfPlayers = "2" #dummy for now
                    #s.send(numberOfPlayers.encode())

                else:
                    first_beginning_screen = False
                    second_beginning_screen = True
                    secondBoardImage = pygame.image.load("secondStartScreen.png").convert()
                    secondBoardImage = pygame.transform.scale(secondBoardImage, boardSize)
                    screen.blit(secondBoardImage, boardLocation)
                    print("mustardChosen: ", mustardChosen)


            if PLAYER_CHOICE_MESSAGE in readmsg:
                #readmsg = s.recv(1024).decode() # NEED TO GET RID OF THIS
                print(readmsg, "\n")
                if "Mustard" in readmsg:
                    mustardChosen = False
                    print("mustard in read message")
                else:

                    mustardChosen = True
                    print("mustard not in read message")
                if "Peacock" in readmsg:
                    peacockChosen = False
                else:
                    peacockChosen = True
                if "Plum" in readmsg:
                    plumChosen = False
                else:
                    plumChosen = True
                if "Scarlet" in readmsg:
                    scarletChosen = False
                else:
                    scarletChosen = True                    
                if "White" in readmsg:
                    whiteChosen = False
                else:
                    whiteChosen = True
                if "Green" in readmsg:
                    greenChosen = False
                else:
                    greenChosen = True
                    
                if mustardChosen == False:
                    b_startMustard = Button(button_type_start, (b_x_start, b_y_start), "Colonel Mustard", button_font, button_color, button_greyed_color)
                    b_startMustard.update(screen)
                if peacockChosen == False:
                    b_startPeacock = Button(button_type_start, (b_x_start+1*(b_width_start+dist_between_buttons), b_y_start), "Mrs. Peacock", button_font, button_color, button_greyed_color)
                    b_startPeacock.update(screen)
                if plumChosen == False:  
                    b_startPlum = Button(button_type_start, (b_x_start+2*(b_width_start+dist_between_buttons), b_y_start), "Professor Plum", button_font, button_color, button_greyed_color)
                    b_startPlum.update(screen)
                if scarletChosen == False:
                    b_startScarlet = Button(button_type_start, (b_x_start+3*(b_width_start+dist_between_buttons), b_y_start), "Miss Scarlett", button_font, button_color, button_greyed_color)
                    b_startScarlet.update(screen)
                if whiteChosen == False:
                    b_startWhite = Button(button_type_start, (b_x_start+4*(b_width_start+dist_between_buttons), b_y_start), "Mrs. White", button_font, button_color, button_greyed_color)
                    b_startWhite.update(screen)
                if greenChosen == False:
                    b_startGreen = Button(button_type_start, (b_x_start+5*(b_width_start+dist_between_buttons), b_y_start), "Reverend Green", button_font, button_color, button_greyed_color)
                    b_startGreen.update(screen)
                    
                # message = input(" -> ")
                #if int(myNumber) == 1: # dummy for now
                #    message = "Mrs. White"
                #else:
                #    message = "Colonel Mustard"
                #playerLocation = Game.playerStartLocations.get(message) #-- > merge conflict
                #p = Player(myNumber, message, playerLocation, None, False, False, False, False) # --> merge conflict 
                #sendMessage = p.playerName + "," + playerLocation
                #s.send(sendMessage.encode())

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
                

            if WIN_MSG in readmsg:
                winning = pygame.image.load("winScreen.png").convert() #load image
                winning = pygame.transform.scale(winning, boardSize) #transform size
                screen.blit(winning, boardLocation) ##populate on screen
            if LOSE_MSG in readmsg:
                losing = pygame.image.load("loseScreen.png").convert() #load image
                losing = pygame.transform.scale(losing, boardSize) #transform size
                screen.blit(losing, boardLocation) ##populate on screen
                
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
                    suggesting = False
                    personCollected = False

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
                    print(p.hasMoved)
                    if(len(choiceInput) > 1):
                        moveOptions = movePlayer(p, choiceInput[1], screen)
                    else:
                        moveOptions = movePlayer(p, choiceInput[0], screen)
                    if moveOptions != "You can only move once per turn.":
                        buttonList = moveOptionButtons(moveOptions)
                        print("&&&&&&&&&&")
                        print(buttonList)
                        currentButtons = buttonList
                    elif moveOptions == "You can only move once per turn.":
                        msg = moveInput
                        print(msg)
                        s.send(msg.encode(form))
                        playerMoveActive = False


                # blockedOptions = (moveInput == "Your move options are all blocked. You can either make an accusation or end your turn.")
                #     if(moveInput != "You can only move once per turn.") and ("room" not in moveInput) and (blockedOptions == False):
                #         p.playerLocation = moveInput
                #         msg = "\nMove " + p.playerName + " to " + p.playerLocation + "."
                #         print(msg)
                #     elif("room" in moveInput):
                #         p.playerLocation = moveInput
                #         print("\nMove " + p.playerName + " to " + p.playerLocation + ".")
                #         msg = "Player must now suggest"
                #         p.canEndTurn = False
                #         p.hasSuggested = False
                #         p.canSuggest = True
                #         print(msg)
                #     elif(moveInput != "You can only move once per turn.") and (blockedOptions == False):
                #         msg = "Player cannot move again."
                #     elif(blockedOptions):
                #         msg = moveInput
                #         print(msg)
                #     s.send(msg.encode(form))
                #     playerMoveActive = False
                
                
            
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
            
            if gameStarted == True:
                if "suggest" in readmsg and canClickButtons and p.hasSuggested == False:
                    print("||||||||||||")
                
                    print(p.hasSuggested)
                    # choiceInput = s.recv(1024).decode().split("//")
                    print("***********")
                    # print(choiceInput)
                    # choice = choiceInput[0]
                    # player_choice = choice[1:]
                    # if("," in player_choice):
                    #     player_choice = player_choice.split(",")[0]
                    suggestionValidation = validateSuggestion(p)
                    if(suggestionValidation == True):
                        suggesting = True
                        playerButtons = printPlayerButtons()
                        currentButtons = playerButtons
                        print("HERE")
                        # handleSuggestion()
                        # playerMoveActive = False
                    # else:
                    #     print("You are are not able to make a suggestion \n")
                    #     suggestionError = "Player cannot make a suggestion!!!! \n"
                    #     s.send(suggestionError.encode())
                    #     playerMoveActive = False
            
            if "is suggesting" in readmsg:
                print(readmsg.split("///"))
                clientsMessage = readmsg.split("///")[0]
                again = True
                while (again == True) and (clientsMessage != "No Matches for this client"):
                    collectSuggestionHelp = True
                    again = False

            if gameStarted == True:
                if (collectSuggestionHelp == True) and ("///" in readmsg) and (p.hasSuggested == False):
                    print("COLLECTSUGGESTIONHELP IS TRUE")
                    print(readmsg)
                    print(readmsg.split("///")[1])
                    if p.playerNumber in readmsg.split("///")[1]:
                        print("AT THE END PART OF SUGGESTION NOW")
                        suggestions = readmsg.split("///")[1].split(",")
                        print(suggestions)
                        nextPlayer = int(suggestions[3])
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
                                # print("You have a card to disprove an item in player " + str(playerNum[0]) + "'s suggestion. ")
                                # print("Your options to show player " +str(playerNum[0]) + " are " + str(matches))
                                # print("Which would you like to show?")
                                print("You have a card to disprove an item in player " + str(9999) + "'s suggestion. ")
                                print("Your options to show player " +str(9999) + " are " + str(matches))
                                print("Which would you like to show?")
                                suggestionHelpPlayer = nextPlayer
                                # canClickButtons = True
                                p.helpingSuggestion = True
                                helpButtons = printSuggestionHelpButtons(9999, matches)
                                currentButtons = helpButtons
                                print("HERE IN SUGGESTION HELP LOGIC")
                                # message = input(" -> ")
                                print(message)
                                # s.send(message.encode())
                            else:
                                count += 1
                                message = "No matches please move to next player"
                                s.send(message.encode())
                        # nextMessage = "Move " + suggestions[0] + " to " + suggestions[1] + ".\n"
                        # print(nextMessage)
                        # playerMoveActive = False

                        # suggestionHelpMessage = s.recv(1024).decode()
                        # if((suggestionHelpMessage != "") or (suggestionHelpMessage != None)) and ("is suggesting" not in suggestionHelpMessage) and (("Next" not in suggestionHelpMessage)):
                        #     again = False
                    elif p.playerNumber in readmsg.split("///")[0] and ("suggestionHelpMade" not in readmsg.split("///")[1]):
                        waitingForSuggestion = True

                    elif "suggestionHelpMade" in readmsg.split("///")[1] and canClickButtons:
                        suggestion = readmsg.split(" ///")[0]
                        print("Another player is suggesting that [" + suggestion + "] is not in the solution")
                        msg = "\n SUGGEST " + personSuggested + " in the " + roomsToNames.get(roomSuggested) + " with the " + weaponSuggested + "\n"
                        s.send(msg.encode(form))
                        p.hasSuggested = True
                        p.hasMoved = True
                        p.canEndTurn = True
                        collectSuggestionHelp = False
                        waitingForSuggestion = False
                        suggestionHelpPlayer = 0
                        currentButtons = []
                        playerMoveActive = False
                        choiceInput = ""
                        clickedButton = ""
                        buttonsClicked = False
                        suggesting = False

            if collectSuggestionHelp == True and "///" not in readmsg and canClickButtons:
                print(readmsg)
                choiceInput = s.recv(1024).decode().split("//")
                suggestion = readmsg
                print("No players had cards that matched your suggestion")
                # print(roomSuggested)
                # msg = "\n SUGGEST " + personSuggested + " in the " + roomsToNames.get(roomSuggested) + " with the " + weaponSuggested + "\n"
                # msg = "No players had cards that matched your suggestion"
                # print(msg)
                # s.send(msg.encode(form))
                p.hasSuggested = True
                p.hasMoved = True
                p.canEndTurn = True
                collectSuggestionHelp = False
                waitingForSuggestion = False
                suggestionHelpPlayer = 0
                currentButtons = []
                playerMoveActive = False
                choiceInput = ""
                clickedButton = ""
                buttonsClicked = False
                suggesting = False
                    

                    # if(" ///" in suggestionHelpMessage):
                    #     suggestion = suggestionHelpMessage.split(" ///")[0]
                    #     print("Another player is suggesting that [" + suggestion + "] is not in the solution")
                    # else:
                    #     suggestion = suggestionHelpMessage
                    #     print("No players had cards that matched your suggestion")
                    # msg = "\n SUGGEST " + suggestPersonInput + " in the " + roomsToNames.get(suggestRoomInput) + " with the " + suggestWeaponInput + "\n"
                    # s.send(msg.encode(form))
                    # p.hasSuggested = True
                    # p.hasMoved = True
                    # p.canEndTurn = True
                

                ### WHEN SUGGESTION HELP IS FINISHED set suggestionHelpPlayer back to 0 and reset current Buttons, set can click buttons back to false
            
            if waitingForSuggestion == True:
                print("WAITING")





        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
                                
            if second_beginning_screen == True:
                updateSecondBeginningScreen = False
                if mustardChosen == False:
                    if b_startMustard.isOver(pos, b_width_start, b_height_start):
                        print("Mustard")
                        updateSecondBeginningScreen = True
                        message = ("Colonel Mustard")
                if peacockChosen == False:    
                    if b_startPeacock.isOver(pos, b_width_start, b_height_start):
                        print("Peacock")
                        updateSecondBeginningScreen = True
                        message = "Mrs. Peacock"
                if plumChosen == False:   
                    if b_startPlum.isOver(pos, b_width_start, b_height_start):
                        print("Plum")
                        updateSecondBeginningScreen = True
                        message = "Professor Plum"
                if scarletChosen == False:
                    if b_startScarlet.isOver(pos, b_width_start, b_height_start):
                        print("Scarlet")
                        updateSecondBeginningScreen = True
                        message = "Miss Scarlett"
                if whiteChosen == False:
                    if b_startWhite.isOver(pos, b_width_start, b_height_start):
                        print("white")
                        updateSecondBeginningScreen = True
                        message = "Mrs. White"
                if greenChosen == False:   
                    if b_startGreen.isOver(pos, b_width_start, b_height_start):
                        print("green")  
                        updateSecondBeginningScreen = True
                        message = "Reverend Green"
                    
                if updateSecondBeginningScreen == True:
                    first_beginning_screen = False
                    second_beginning_screen = False
                    playerLocation = Game.playerStartLocations.get(message)
                    p = Player(myNumber, message, playerLocation, None, False, False, False, False, False)
                    sendMessage = p.playerName + "," + playerLocation
                    s.send(sendMessage.encode())
                    screen.blit(boardImage, boardLocation)
                    gameStarted = True
                 
            
            if first_beginning_screen == True:
                updateFirstBeginningScreen = False
 
                if b_start2.isOver(pos, b_width_start, b_height_start):
                    print("2")
                    updateFirstBeginningScreen = True
                    inputNumPlayers = "2"
                    
                if b_start3.isOver(pos, b_width_start, b_height_start):
                    print("3")
                    updateFirstBeginningScreen = True
                    inputNumPlayers = "3"

                if b_start4.isOver(pos, b_width_start, b_height_start):
                    print("4")
                    updateFirstBeginningScreen = True
                    inputNumPlayers = "4"

                if b_start5.isOver(pos, b_width_start, b_height_start):
                    print("5")
                    updateFirstBeginningScreen = True
                    inputNumPlayers = "5"                    
                    
                if b_start6.isOver(pos, b_width_start, b_height_start):
                    print("6") 
                    updateFirstBeginningScreen = True
                    inputNumPlayers = "6"                    

                if updateFirstBeginningScreen == True:
                    first_beginning_screen = False
                    second_beginning_screen = True
                    secondBoardImage = pygame.image.load("secondStartScreen.png").convert()
                    secondBoardImage = pygame.transform.scale(secondBoardImage, boardSize)
                    screen.blit(secondBoardImage, boardLocation)
                    b_startMustard = Button(button_type_start, (b_x_start, b_y_start), "Colonel Mustard", button_font, button_color, button_greyed_color)
                    b_startMustard.update(screen)
                    b_startPeacock = Button(button_type_start, (b_x_start+1*(b_width_start+dist_between_buttons), b_y_start), "Mrs. Peacock", button_font, button_color, button_greyed_color)
                    b_startPeacock.update(screen)
                    b_startPlum = Button(button_type_start, (b_x_start+2*(b_width_start+dist_between_buttons), b_y_start), "Professor Plum", button_font, button_color, button_greyed_color)
                    b_startPlum.update(screen)
                    b_startScarlet = Button(button_type_start, (b_x_start+3*(b_width_start+dist_between_buttons), b_y_start), "Miss Scarlett", button_font, button_color, button_greyed_color)
                    b_startScarlet.update(screen)
                    b_startWhite = Button(button_type_start, (b_x_start+4*(b_width_start+dist_between_buttons), b_y_start), "Mrs. White", button_font, button_color, button_greyed_color)
                    b_startWhite.update(screen)
                    b_startGreen = Button(button_type_start, (b_x_start+5*(b_width_start+dist_between_buttons), b_y_start), "Reverend Green", button_font, button_color, button_greyed_color)
                    b_startGreen.update(screen)
                    s.send(inputNumPlayers.encode())
            
            
            # updating player card: people
            if t_mustard.isOver(pos, info_width, info_height):
                if t_mustard.bolded==False:
                    t_mustard = Button(t_mustard.image, (t_mustard.x_pos, t_mustard.y_pos), t_mustard.text_input, info_font_bold, t_mustard.base_color, t_mustard.hovering_color)
                    t_mustard.bolded = True
                    t_mustard.update(screen)
                else:
                    t_mustard = Button(t_mustard.image, (t_mustard.x_pos, t_mustard.y_pos), t_mustard.text_input, info_font, t_mustard.base_color, t_mustard.hovering_color)
                    t_mustard.bolded = False
                    t_mustard.update(screen)
            if t_peacock.isOver(pos, info_width, info_height):
                if t_peacock.bolded==False:
                    t_peacock = Button(t_peacock.image, (t_peacock.x_pos, t_peacock.y_pos), t_peacock.text_input, info_font_bold, t_peacock.base_color, t_peacock.hovering_color)
                    t_peacock.bolded = True
                    t_peacock.update(screen)
                else:
                    t_peacock = Button(t_peacock.image, (t_peacock.x_pos, t_peacock.y_pos), t_peacock.text_input, info_font, t_peacock.base_color, t_peacock.hovering_color)
                    t_peacock.bolded = False
                    t_peacock.update(screen)                   
            if t_plum.isOver(pos, info_width, info_height):
                if t_plum.bolded==False:
                    t_plum = Button(t_plum.image, (t_plum.x_pos, t_plum.y_pos), t_plum.text_input, info_font_bold, t_plum.base_color, t_plum.hovering_color)
                    t_plum.bolded = True
                    t_plum.update(screen)
                else:
                    t_plum = Button(t_plum.image, (t_plum.x_pos, t_plum.y_pos), t_plum.text_input, info_font, t_plum.base_color, t_plum.hovering_color)
                    t_plum.bolded = False
                    t_plum.update(screen)
            if t_scarlet.isOver(pos, info_width, info_height):
                if t_scarlet.bolded==False:
                    t_scarlet = Button(t_scarlet.image, (t_scarlet.x_pos, t_scarlet.y_pos), t_scarlet.text_input, info_font_bold, t_scarlet.base_color, t_scarlet.hovering_color)
                    t_scarlet.bolded = True
                    t_scarlet.update(screen)
                else:
                    t_scarlet = Button(t_scarlet.image, (t_scarlet.x_pos, t_scarlet.y_pos), t_scarlet.text_input, info_font, t_scarlet.base_color, t_scarlet.hovering_color)
                    t_scarlet.bolded = False
                    t_scarlet.update(screen)
            if t_white.isOver(pos, info_width, info_height):
                if t_white.bolded==False:
                    t_white = Button(t_white.image, (t_white.x_pos, t_white.y_pos), t_white.text_input, info_font_bold, t_white.base_color, t_white.hovering_color)
                    t_white.bolded = True
                    t_white.update(screen)
                else:
                    t_white = Button(t_white.image, (t_white.x_pos, t_white.y_pos), t_white.text_input, info_font, t_white.base_color, t_white.hovering_color)
                    t_white.bolded = False
                    t_white.update(screen)          
            if t_green.isOver(pos, info_width, info_height):
                if t_green.bolded==False:
                    t_green = Button(t_green.image, (t_green.x_pos, t_green.y_pos), t_green.text_input, info_font_bold, t_green.base_color, t_green.hovering_color)
                    t_green.bolded = True
                    t_green.update(screen)
                else:
                    t_green = Button(t_green.image, (t_green.x_pos, t_green.y_pos), t_green.text_input, info_font, t_green.base_color, t_green.hovering_color)
                    t_green.bolded = False
                    t_green.update(screen) 

            # updating player card: weapons
            if t_candle.isOver(pos, info_width, info_height):
                if t_candle.bolded==False:
                    t_candle = Button(t_candle.image, (t_candle.x_pos, t_candle.y_pos), t_candle.text_input, info_font_bold, t_candle.base_color, t_candle.hovering_color)
                    t_candle.bolded = True
                    t_candle.update(screen)
                else:
                    t_candle = Button(t_candle.image, (t_candle.x_pos, t_candle.y_pos), t_candle.text_input, info_font, t_candle.base_color, t_candle.hovering_color)
                    t_candle.bolded = False
                    t_candle.update(screen)
            if t_dagger.isOver(pos, info_width, info_height):
                if t_dagger.bolded==False:
                    t_dagger = Button(t_dagger.image, (t_dagger.x_pos, t_dagger.y_pos), t_dagger.text_input, info_font_bold, t_dagger.base_color, t_dagger.hovering_color)
                    t_dagger.bolded = True
                    t_dagger.update(screen)
                else:
                    t_dagger = Button(t_dagger.image, (t_dagger.x_pos, t_dagger.y_pos), t_dagger.text_input, info_font, t_dagger.base_color, t_dagger.hovering_color)
                    t_dagger.bolded = False
                    t_dagger.update(screen)
            if t_pipe.isOver(pos, info_width, info_height):
                if t_pipe.bolded==False:
                    t_pipe = Button(t_pipe.image, (t_pipe.x_pos, t_pipe.y_pos), t_pipe.text_input, info_font_bold, t_pipe.base_color, t_pipe.hovering_color)
                    t_pipe.bolded = True
                    t_pipe.update(screen)
                else:
                    t_pipe = Button(t_pipe.image, (t_pipe.x_pos, t_pipe.y_pos), t_pipe.text_input, info_font, t_pipe.base_color, t_pipe.hovering_color)
                    t_pipe.bolded = False
                    t_pipe.update(screen)
            if t_rope.isOver(pos, info_width, info_height):
                if t_rope.bolded==False:
                    t_rope = Button(t_rope.image, (t_rope.x_pos, t_rope.y_pos), t_rope.text_input, info_font_bold, t_rope.base_color, t_rope.hovering_color)
                    t_rope.bolded = True
                    t_rope.update(screen)
                else:
                    t_rope = Button(t_rope.image, (t_rope.x_pos, t_rope.y_pos), t_rope.text_input, info_font, t_rope.base_color, t_rope.hovering_color)
                    t_rope.bolded = False
                    t_rope.update(screen)
            if t_wrench.isOver(pos, info_width, info_height):
                if t_wrench.bolded==False:
                    t_wrench = Button(t_wrench.image, (t_wrench.x_pos, t_wrench.y_pos), t_wrench.text_input, info_font_bold, t_wrench.base_color, t_wrench.hovering_color)
                    t_wrench.bolded = True
                    t_wrench.update(screen)
                else:
                    t_wrench = Button(t_wrench.image, (t_wrench.x_pos, t_wrench.y_pos), t_wrench.text_input, info_font, t_wrench.base_color, t_wrench.hovering_color)
                    t_wrench.bolded = False
                    t_wrench.update(screen)
            if t_revolver.isOver(pos, info_width, info_height):
                if t_revolver.bolded==False:
                    t_revolver = Button(t_revolver.image, (t_revolver.x_pos, t_revolver.y_pos), t_revolver.text_input, info_font_bold, t_revolver.base_color, t_revolver.hovering_color)
                    t_revolver.bolded = True
                    t_revolver.update(screen)
                else:
                    t_revolver = Button(t_revolver.image, (t_revolver.x_pos, t_revolver.y_pos), t_revolver.text_input, info_font, t_revolver.base_color, t_revolver.hovering_color)
                    t_revolver.bolded = False
                    t_revolver.update(screen)

            # updating player card: roomsToNames
            if t_study.isOver(pos, info_width, info_height):
                if t_study.bolded==False:
                    t_study = Button(t_study.image, (t_study.x_pos, t_study.y_pos), t_study.text_input, info_font_bold, t_study.base_color, t_study.hovering_color)
                    t_study.bolded = True
                    t_study.update(screen)
                else:
                    t_study = Button(t_study.image, (t_study.x_pos, t_study.y_pos), t_study.text_input, info_font, t_study.base_color, t_study.hovering_color)
                    t_study.bolded = False
                    t_study.update(screen)
            if t_hall.isOver(pos, info_width, info_height):
                if t_hall.bolded==False:
                    t_hall = Button(t_hall.image, (t_hall.x_pos, t_hall.y_pos), t_hall.text_input, info_font_bold, t_hall.base_color, t_hall.hovering_color)
                    t_hall.bolded = True
                    t_hall.update(screen)
                else:
                    t_hall = Button(t_hall.image, (t_hall.x_pos, t_hall.y_pos), t_hall.text_input, info_font, t_hall.base_color, t_hall.hovering_color)
                    t_hall.bolded = False
                    t_hall.update(screen)
            if t_lounge.isOver(pos, info_width, info_height):
                if t_lounge.bolded==False:
                    t_lounge = Button(t_lounge.image, (t_lounge.x_pos, t_lounge.y_pos), t_lounge.text_input, info_font_bold, t_lounge.base_color, t_lounge.hovering_color)
                    t_lounge.bolded = True
                    t_lounge.update(screen)
                else:
                    t_lounge = Button(t_lounge.image, (t_lounge.x_pos, t_lounge.y_pos), t_lounge.text_input, info_font, t_lounge.base_color, t_lounge.hovering_color)
                    t_lounge.bolded = False
                    t_lounge.update(screen)
            if t_library.isOver(pos, info_width, info_height):
                if t_library.bolded==False:
                    t_library = Button(t_library.image, (t_library.x_pos, t_library.y_pos), t_library.text_input, info_font_bold, t_library.base_color, t_library.hovering_color)
                    t_library.bolded = True
                    t_library.update(screen)
                else:
                    t_library = Button(t_library.image, (t_library.x_pos, t_library.y_pos), t_library.text_input, info_font, t_library.base_color, t_library.hovering_color)
                    t_library.bolded = False
                    t_library.update(screen)
            if t_billiard.isOver(pos, info_width, info_height):
                if t_billiard.bolded==False:
                    t_billiard = Button(t_billiard.image, (t_billiard.x_pos, t_billiard.y_pos), t_billiard.text_input, info_font_bold, t_billiard.base_color, t_billiard.hovering_color)
                    t_billiard.bolded = True
                    t_billiard.update(screen)
                else:
                    t_billiard = Button(t_billiard.image, (t_billiard.x_pos, t_billiard.y_pos), t_billiard.text_input, info_font, t_billiard.base_color, t_billiard.hovering_color)
                    t_billiard.bolded = False
                    t_billiard.update(screen)
            if t_dining.isOver(pos, info_width, info_height):
                if t_dining.bolded==False:
                    t_dining = Button(t_dining.image, (t_dining.x_pos, t_dining.y_pos), t_dining.text_input, info_font_bold, t_dining.base_color, t_dining.hovering_color)
                    t_dining.bolded = True
                    t_dining.update(screen)
                else:
                    t_dining = Button(t_dining.image, (t_dining.x_pos, t_dining.y_pos), t_dining.text_input, info_font, t_dining.base_color, t_dining.hovering_color)
                    t_dining.bolded = False
                    t_dining.update(screen)
            if t_conservatory.isOver(pos, info_width, info_height):
                if t_conservatory.bolded==False:
                    t_conservatory = Button(t_conservatory.image, (t_conservatory.x_pos, t_conservatory.y_pos), t_conservatory.text_input, info_font_bold, t_conservatory.base_color, t_conservatory.hovering_color)
                    t_conservatory.bolded = True
                    t_conservatory.update(screen)
                else:
                    t_conservatory = Button(t_conservatory.image, (t_conservatory.x_pos, t_conservatory.y_pos), t_conservatory.text_input, info_font, t_conservatory.base_color, t_conservatory.hovering_color)
                    t_conservatory.bolded = False
                    t_conservatory.update(screen)
            if t_ballroom.isOver(pos, info_width, info_height):
                if t_ballroom.bolded==False:
                    t_ballroom = Button(t_ballroom.image, (t_ballroom.x_pos, t_ballroom.y_pos), t_ballroom.text_input, info_font_bold, t_ballroom.base_color, t_ballroom.hovering_color)
                    t_ballroom.bolded = True
                    t_ballroom.update(screen)
                else:
                    t_ballroom = Button(t_ballroom.image, (t_ballroom.x_pos, t_ballroom.y_pos), t_ballroom.text_input, info_font, t_ballroom.base_color, t_ballroom.hovering_color)
                    t_ballroom.bolded = False
                    t_ballroom.update(screen)
            if t_kitchen.isOver(pos, info_width, info_height):
                if t_kitchen.bolded==False:
                    t_kitchen = Button(t_kitchen.image, (t_kitchen.x_pos, t_kitchen.y_pos), t_kitchen.text_input, info_font_bold, t_kitchen.base_color, t_kitchen.hovering_color)
                    t_kitchen.bolded = True
                    t_kitchen.update(screen)
                else:
                    t_kitchen = Button(t_kitchen.image, (t_kitchen.x_pos, t_kitchen.y_pos), t_kitchen.text_input, info_font, t_kitchen.base_color, t_kitchen.hovering_color)
                    t_kitchen.bolded = False
                    t_kitchen.update(screen)
                    
            # if ((TURN_MSG or MOVE_MSG) in readmsg) or (SUGGESTION in readmsg):
            #    suggestionValidation = None
            #    if "Player "+str(p.playerNumber) in readmsg:
            #        canClickButtons = True
            #        playerMoveActive = True # CAN I USE THIS TO ALLOW BUTTON CLICKS?
            #    else:
            #        canClickButtons = False
            if gameStarted == True:
                if canClickButtons or p.helpingSuggestion:
                    print("INSIDE THIS PART!!!")
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
                                        print(weaponButtons)
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
                                        handleSuggestion(personSuggested, roomSuggested, weaponSuggested)



                    if buttonsClicked == True:
                        if(p.hasMoved == False) and (p.helpingSuggestion == False):
                            print("INSIDE HERE")
                            ### NEED TO FIGURE OUT HOW TO MAKE MULTIPLE BUTTONS APPEAR ####
                            print("PRINTING BUTTON TEXT INPUT")
                            print(clickedButton.text_input)
                            print(choiceInput)
                            moveInput = whereToMove(p, clickedButton.text_input, choiceInput[1])
                            print(moveInput)

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
                            pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                            pygame.display.update()

                            # pygame.draw.rect(screen, WHITE, [0, hLeft, vertical, height])
                            # done = True
                        if p.helpingSuggestion == True and buttonsClicked == True:
                            print("IN THIS SPOT")
                            currentButtons = []
                            buttonsClicked = False
                            pygame.draw.rect(screen, WHITE, [1013, 516, 350, 201])
                            pygame.display.update()
                            s.send(clickedButton.text_input.encode())
                            clickedButton = ""
                            p.hasMoved = False



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
