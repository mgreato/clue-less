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
class Text():
    def __init__(self, position, text_input, font_input, bold_input, base_color, greyed_color):
        self.position = position
        self.text_input = text_input
        self.font_input = font_input
        self.bold_input = bold_input
        self.base_color = base_color
        self.greyed_color = greyed_color
        self.text = self.font_input.render(self.text_input, True, self.base_color)

    def update(self, screen):
        if self.text_input is not None:
            screen.blit(self.text, self.position)  # populate on screen

    def boldText(self):
        self.text = self.bold_input.render(self.text_input, True, self.base_color)

    def baseText(self):
        self.text = self.font_input.render(self.text_input, True, self.base_color)

    def greyText(self):
        self.text = self.font_input.render(self.text_input, True, self.greyed_color)


mustardChosen = False
peacockChosen = False
plumChosen = False
scarletChosen = False
whiteChosen = False
greenChosen = False
not_text1 = ""
not_text2 = ""
not_text3 = ""
not_text4 = ""
not_text5 = ""
not_text6 = ""
not_text7 = ""
not_text8 = ""
not_text9 = ""
not_text10 = ""


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
        x_p = self.x_pos - button_width / 2
        y_p = self.y_pos - button_height / 2
        if position[0] > x_p and position[0] < x_p + button_width:
            if position[1] > y_p and position[1] < y_p + button_height:
                return True
        return False


pygame.init()
pygame.event.clear()

mustardChosen = False
peacockChosen = False
plumChosen = False
scarletChosen = False
whiteChosen = False
greenChosen = False

not_text1 = ""
not_text2 = ""
not_text3 = ""
not_text4 = ""
not_text5 = ""
not_text6 = ""
not_text7 = ""
not_text8 = ""
not_text9 = ""
not_text10 = ""

# possible messages from server
CONNECTED_MSG = "Connection established"
BEGINNING_MSG = "Game is beginning"
TURN_MSG = "Next Turn"
MOVE_MSG = "another"
SUGGESTION = "is suggesting "
CARDS_MSG = "Your cards are"
WIN_MSG = "Won!"
WIN_MSG2 = "won!"
LOSE_MSG = "lost the game"
PLAYER_CHOICE_MESSAGE = "What player would you like to be?"
currentPlayer = 0

# names, locations, and weapons that can be indexed. This code is identical in the server.py file
names = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
locations = ["room1", "room2", "room3", "room4", "room5", "room6", "room7", "room8", "room9",
             "hallway12", "hallway23", "hallway34", "hallway45", "hallway56", "hallway67",
             "hallway78", "hallway81", "hallway89", "hallway29", "hallway49", "hallway69"]
roomsToNames = {"room1": "study", "room2": "hall", "room3": "lounge", "room4": "dining room",
                "room5": "kitchen", "room6": "ballroom", "room7": "conservatory", "room8": "library",
                "room9": "billiard room"}
allRoomsToNames = {"room1": "study", "room2": "hall", "room3": "lounge", "room4": "dining room",
                   "room5": "kitchen", "room6": "ballroom", "room7": "conservatory", "room8": "library",
                   "room9": "billiard room", "hallway12": "hallway12",
                   "hallway23": "hallway23", "hallway34": "hallway34", "hallway45": "hallway45",
                   "hallway56": "hallway56", "hallway67": "hallway67",
                   "hallway78": "hallway78", "hallway81": "hallway81", "hallway89": "hallway89",
                   "hallway29": "hallway29", "hallway49": "hallway49", "hallway69": "hallway69"}
allNamesToRooms = {"study": "room1", "hall": "room2", "lounge": "room3", "dining room": "room4",
                   "kitchen": "room5", "ballroom": "room6", "conservatory": "room7", "library": "room8",
                   "billiard room": "room9", "hallway12": "hallway12",
                   "hallway23": "hallway23", "hallway34": "hallway34", "hallway45": "hallway45",
                   "hallway56": "hallway56", "hallway67": "hallway67",
                   "hallway78": "hallway78", "hallway81": "hallway81", "hallway89": "hallway89",
                   "hallway29": "hallway29", "hallway49": "hallway49", "hallway69": "hallway69"}
weapons = ["rope", "candlestick", "dagger", "wrench", "lead pipe", "revolver"]
# playerStartLocations = {"Miss Scarlett": "hallway23", "Colonel Mustard": "hallway34", "Mrs. White": "hallway56", "Mr. Green": "hallway67",
#             "Mrs. Peacock": "hallway78", "Professor Plum": "hallway81"}
playerFirstLocations = {"Miss Scarlett": "hallway23", "Colonel Mustard": "hallway34", "Mrs. White": "hallway56",
                        "Reverend Green": "hallway67",
                        "Mrs. Peacock": "hallway78", "Professor Plum": "hallway81"}
rooms = ["study", "hall", "lounge", "dining room", "kitchen", "ballroom", "conservatory", "library", "billiard room"]

# connect to server
port = 5050
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), port))
form = 'utf-8'
playerChosen = False

playerText = ""
cardText = ""
currentButtons = []
buttonsClicked = False
clickedButton = ""
myNumber = 0
suggesting = False
accusing = False
personSuggested = ""
weaponSuggested = ""
roomSuggested = ""
waitingForSuggestion = False

# set up threading for pygame and server events
SERVER_MESSAGE = pygame.USEREVENT + 1


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
            new_event = pygame.event.Event(SERVER_MESSAGE, {"message": readmsg})
            pygame.event.post(new_event)


q = queue.Queue()
SocketListener(s, q).start()


def can_take_secret_passage(playerRoom):
    boolean = False
    diagonal_room_name = ""
    if playerRoom == "room1":
        diagonal_room_name = "room5"
        boolean = True
    if playerRoom == "room3":
        diagonal_room_name = "room7"
        boolean = True
    if playerRoom == "room5":
        diagonal_room_name = "room1"
        boolean = True
    if playerRoom == "room7":
        diagonal_room_name = "room3"
        boolean = True
    return boolean, diagonal_room_name


def moveOptionButtons(moveOptions):
    pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
    pygame.display.update()
    info_font = pygame.font.SysFont('Calibri', 14, False, False)
    info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
    where = Text((1075, 525), "Where would you like to move?", info_font, info_font_bold, (0, 0, 0), info_greyed_color)
    where.update(screen)
    size = (145, 65)
    font = pygame.font.SysFont('Calibri', 16, True, False)
    buttonType = pygame.transform.scale(button_image, size)  # transform size
    buttonList = []
    x = 250
    y = 250
    buttonCount = 1
    positions = [(1100, 575), (1270, 575), (1100, 650), (1270, 650)]
    for i in range(0, len(moveOptions)):
        option = allRoomsToNames.get(moveOptions[i])
        option = Button(buttonType, positions[i], option, font, (0, 255, 255), (0, 50, 50))
        buttonList.append(option)
        option.update(screen)
        x += 170
        buttonCount += 1
        pygame.display.update()
    return buttonList


def movePlayer(p, otherPlayerLocations):
    otherPlayerLocationsList = [h for h in ast.literal_eval(otherPlayerLocations) if ("room" not in h)]
    playerInRoom = p.playerLocation.__contains__("room")
    if (p.playerLocation == "None"):
        possibleHallways = playerFirstLocations.get(p.playerName)
        return [possibleHallways]
    if (playerInRoom):
        roomNumber = p.playerLocation.split("room")[1]
        possibleHallways = [h for h in locations if (
                ("hallway" and roomNumber in h) and ("room" not in h) and (h not in otherPlayerLocationsList))]
        check_diagonal_result = can_take_secret_passage(p.playerLocation)
        if (len(possibleHallways) == 0) and (check_diagonal_result[0] == False):
            moveInput = "NO POSSIBLE OPTIONS"
            return moveInput
        else:
            if check_diagonal_result[0] == True:
                if (len(possibleHallways) == 0):
                    return [check_diagonal_result[1]]
                else:
                    possible = possibleHallways
                    possible.append(check_diagonal_result[1])
                    return possible
            else:
                return possibleHallways
    else:
        if (p.playerLocation.__contains__("hallway")):
            hallwayRooms = p.playerLocation.split("hallway")[1]
            roomChoices = list(hallwayRooms)
            roomChoice1 = "room" + roomChoices[0]
            roomChoice2 = "room" + roomChoices[1]
            possibleRooms = []
            possibleRooms.append(roomChoice1)
            possibleRooms.append(roomChoice2)
            return possibleRooms


def printPlayerButtons(action):
    pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
    pygame.display.update()
    info_font = pygame.font.SysFont('Calibri', 14, False, False)
    info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
    messaging = "Who would you like to " + action + "?"
    who = Text((1075, 525), messaging, info_font, info_font_bold, (0, 0, 0), info_greyed_color)
    who.update(screen)
    size = (100, 55)
    positions = [(1075, 575), (1190, 575), (1305, 575), (1075, 650), (1190, 650), (1305, 650)]
    font = pygame.font.SysFont('Calibri', 14, True, False)
    buttonType = pygame.transform.scale(button_image, size)  # transform size
    playerButtons = []
    for i in range(0, len(names)):
        if (names[i] == "Reverend Green") or (names[i] == "Colonel Mustard"):
            font = pygame.font.SysFont('Calibri', 12, True, False)
            playerButton = Button(buttonType, (positions[i]), names[i], font, (0, 255, 255), (0, 50, 50))
            playerButtons.append(playerButton)
            playerButton.update(screen)
        else:
            playerButton = Button(buttonType, (positions[i]), names[i], font, (0, 255, 255), (0, 50, 50))
            playerButtons.append(playerButton)
            playerButton.update(screen)
    pygame.display.update()
    return playerButtons


def printWeaponButtons(action):
    pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
    pygame.display.update()
    info_font = pygame.font.SysFont('Calibri', 14, False, False)
    info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
    messaging = "What weapon would you like to " + action + "?"
    what = Text((1075, 525), messaging, info_font, info_font_bold, (0, 0, 0), info_greyed_color)
    what.update(screen)
    size = (100, 55)
    positions = [(1075, 575), (1190, 575), (1305, 575), (1075, 650), (1190, 650), (1305, 650)]
    font = pygame.font.SysFont('Calibri', 16, True, False)
    buttonType = pygame.transform.scale(button_image, size)  # transform size
    weaponButtons = []
    for i in range(0, len(weapons)):
        weaponButton = Button(buttonType, (positions[i]), weapons[i], font, (0, 255, 255), (0, 50, 50))
        weaponButtons.append(weaponButton)
        weaponButton.update(screen)
    pygame.display.update()
    return weaponButtons


def printRoomButtons(action):
    pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
    pygame.display.update()
    info_font = pygame.font.SysFont('Calibri', 14, False, False)
    info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
    messaging = "What room do you choose to " + action + "?"
    where = Text((1075, 525), messaging, info_font, info_font_bold, (0, 0, 0), info_greyed_color)
    where.update(screen)
    size = (95, 45)
    positions = [(1075, 575), (1190, 575), (1305, 575), (1075, 625), (1190, 625), (1305, 625), (1075, 675), (1190, 675),
                 (1305, 675)]
    font = pygame.font.SysFont('Calibri', 16, True, False)
    buttonType = pygame.transform.scale(button_image, size)  # transform size
    roomButtons = []
    for i in range(0, len(rooms)):
        if (rooms[i] == "dining room") or (rooms[i] == "conservatory") or (rooms[i] == "billiard room"):
            font = pygame.font.SysFont('Calibri', 14, True, False)
            roomButton = Button(buttonType, (positions[i]), rooms[i], font, (0, 255, 255), (0, 50, 50))
            roomButtons.append(roomButton)
            roomButton.update(screen)
        else:
            roomButton = Button(buttonType, (positions[i]), rooms[i], font, (0, 255, 255), (0, 50, 50))
            roomButtons.append(roomButton)
            roomButton.update(screen)
    pygame.display.update()
    return roomButtons


def printSuggestionHelpButtons(playerNumber, suggestionMatches):
    info_font = pygame.font.SysFont('Calibri', 14, False, False)
    info_font_bold = pygame.font.SysFont('Calibri', 14, True, True)
    helpMessage = "What card would you like to show to player" + str(playerNumber) + "?"
    help = Text((1025, 525), helpMessage, info_font, info_font_bold, (0, 0, 0), info_greyed_color)
    help.update(screen)
    size = (100, 50)
    positions = [(1100, 575), (1250, 575), (1175, 650)]
    font = pygame.font.SysFont('Calibri', 13, True, False)
    buttonType = pygame.transform.scale(button_image, size)  # transform size
    helpButtons = []
    for i in range(0, len(suggestionMatches)):
        helpButton = Button(buttonType, (positions[i]), suggestionMatches[i], font, (0, 255, 255), (0, 50, 50))
        helpButtons.append(helpButton)
        helpButton.update(screen)
    pygame.display.update()
    return helpButtons


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

# Define board areas
width = 1366
height = 768
size = (width, height)
screen = pygame.display.set_mode(size)
# Define the sectors for each section
vertical = 2 * width / 3  # = 911
hLeft = 3 * height / 4  # = 576
hRight = 2 * height / 3  # = 512

# Define other variables
# PI = 3.141592653

# Basic Sreen setup
pygame.display.set_caption("Ctrl-Alt-Elites Clueless")  # name of the tab
screen.fill(WHITE)  # background color

################################
# Import Images Here
################################# Boardgame Image
# Define sizes and locations of images
# Board
boardSize = (911, 768)  # set size of board image
boardLocation = (0, 0)

boardImage = pygame.image.load("gameboard.png").convert()  # load image
boardImage = pygame.transform.scale(boardImage, boardSize)  # transform size
background_image = pygame.image.load("background.png").convert()  # image to be used as button background PLAY WITH THIS
initialBoardImage = pygame.image.load("background.png").convert()
initialBoardImage = pygame.transform.scale(initialBoardImage, boardSize)
screen.blit(initialBoardImage, boardLocation)  ##populate on screen
# screen.blit(boardImage, boardLocation) ##populate on screen

playerSize = (32, 32)
mustardImage = pygame.image.load("Colonel Mustard.png").convert()
mustardImage = pygame.transform.scale(mustardImage, playerSize)
peacockImage = pygame.image.load("Mrs Peacock.png").convert()
peacockImage = pygame.transform.scale(peacockImage, playerSize)
plumImage = pygame.image.load("Professor Plum.png").convert()
plumImage = pygame.transform.scale(plumImage, playerSize)
scarlettImage = pygame.image.load("Miss Scarlett.png").convert()
scarlettImage = pygame.transform.scale(scarlettImage, playerSize)
whiteImage = pygame.image.load("Mrs White.png").convert()
whiteImage = pygame.transform.scale(whiteImage, playerSize)
greenImage = pygame.image.load("Reverend Green.png").convert()
greenImage = pygame.transform.scale(greenImage, playerSize)


def movePlayerImages(playerLocations):
    screen.blit(boardImage, boardLocation)
    disp = 6
    px = 32

    for player in playerLocations:
        location = playerLocations[player]
        if location == "none" or location == "None":
            pass
        else:
            if location == "hallway12":
                roomx = 255
                roomy = 133
            elif location == "hallway23":
                roomx = 575
                roomy = 133
            elif location == "hallway89":
                roomx = 255
                roomy = 358
            elif location == "hallway49":
                roomx = 575
                roomy = 358
            elif location == "hallway67":
                roomx = 255
                roomy = 585
            elif location == "hallway56":
                roomx = 575
                roomy = 585
            elif location == "hallway81":
                roomx = 110
                roomy = 253
            elif location == "hallway29":
                roomx = 425
                roomy = 253
            elif location == "hallway34":
                roomx = 737
                roomy = 253
            elif location == "hallway78":
                roomx = 110
                roomy = 475
            elif location == "hallway69":
                roomx = 425
                roomy = 475
            elif location == "hallway45":
                roomx = 737
                roomy = 475
            elif (
                    player == "Colonel Mustard" or player == "Mrs. Peacock" or player == "Professor Plum") and location == "study":
                roomx = 65
                roomy = 84
            elif (
                    player == "Miss Scarlett" or player == "Mrs. White" or player == "Reverend Green") and location == "study":
                roomx = 65
                roomy = 227 - px
            elif (
                    player == "Colonel Mustard" or player == "Mrs. Peacock" or player == "Professor Plum") and location == "hall":
                roomx = 380
                roomy = 84
            elif (
                    player == "Miss Scarlett" or player == "Mrs. White" or player == "Reverend Green") and location == "hall":
                roomx = 380
                roomy = 227 - px
            elif (
                    player == "Colonel Mustard" or player == "Mrs. Peacock" or player == "Professor Plum") and location == "lounge":
                roomx = 692
                roomy = 84
            elif (
                    player == "Miss Scarlett" or player == "Mrs. White" or player == "Reverend Green") and location == "lounge":
                roomx = 692
                roomy = 227 - px
            elif (
                    player == "Colonel Mustard" or player == "Mrs. Peacock" or player == "Professor Plum") and location == "library":
                roomx = 65
                roomy = 310
            elif (
                    player == "Miss Scarlett" or player == "Mrs. White" or player == "Reverend Green") and location == "library":
                roomx = 65
                roomy = 453 - px
            elif (
                    player == "Colonel Mustard" or player == "Mrs. Peacock" or player == "Professor Plum") and location == "billiard room":
                roomx = 380
                roomy = 310
            elif (
                    player == "Miss Scarlett" or player == "Mrs. White" or player == "Reverend Green") and location == "billiard room":
                roomx = 380
                roomy = 453 - px
            elif (
                    player == "Colonel Mustard" or player == "Mrs. Peacock" or player == "Professor Plum") and location == "dining room":
                roomx = 692
                roomy = 310
            elif (
                    player == "Miss Scarlett" or player == "Mrs. White" or player == "Reverend Green") and location == "dining room":
                roomx = 692
                roomy = 453 - px
            elif (
                    player == "Colonel Mustard" or player == "Mrs. Peacock" or player == "Professor Plum") and location == "conservatory":
                roomx = 65
                roomy = 535
            elif (
                    player == "Miss Scarlett" or player == "Mrs. White" or player == "Reverend Green") and location == "conservatory":
                roomx = 65
                roomy = 678 - px
            elif (
                    player == "Colonel Mustard" or player == "Mrs. Peacock" or player == "Professor Plum") and location == "ballroom":
                roomx = 380
                roomy = 535
            elif (
                    player == "Miss Scarlett" or player == "Mrs. White" or player == "Reverend Green") and location == "ballroom":
                roomx = 380
                roomy = 678 - px
            elif (
                    player == "Colonel Mustard" or player == "Mrs. Peacock" or player == "Professor Plum") and location == "kitchen":
                roomx = 692
                roomy = 535
            elif (
                    player == "Miss Scarlett" or player == "Mrs. White" or player == "Reverend Green") and location == "kitchen":
                roomx = 692
                roomy = 678 - px

            if "hallway" in location:
                if player == "Colonel Mustard":
                    screen.blit(mustardImage, (roomx, roomy))
                elif player == "Mrs. Peacock":
                    screen.blit(peacockImage, (roomx, roomy))
                elif player == "Professor Plum":
                    screen.blit(plumImage, (roomx, roomy))
                elif player == "Miss Scarlett":
                    screen.blit(scarlettImage, (roomx, roomy))
                elif player == "Mrs. White":
                    screen.blit(whiteImage, (roomx, roomy))
                elif player == "Reverend Green":
                    screen.blit(greenImage, (roomx, roomy))

            else:
                if player == "Colonel Mustard":
                    screen.blit(mustardImage, (roomx + disp, roomy))
                elif player == "Mrs. Peacock":
                    screen.blit(peacockImage, (roomx + 2 * disp + px, roomy))
                elif player == "Professor Plum":
                    screen.blit(plumImage, (roomx + 3 * disp + 2 * px, roomy))
                elif player == "Miss Scarlett":
                    screen.blit(scarlettImage, (roomx + disp, roomy))
                elif player == "Mrs. White":
                    screen.blit(whiteImage, (roomx + 2 * disp + px, roomy))
                elif player == "Reverend Green":
                    screen.blit(greenImage, (roomx + 3 * disp + 2 * px, roomy))


## INSERT PLAYER IMAGES IN HERE
# playerSize = (50, 50) #set size of character images
# for each of the images ....
# playerImage = pygame.image.load("player_image.png").convert() #load image
# boardImage = pygame.transform.scale(boardImage, boardSize) #transform size
#### screen.blit will have to happen in the loop


################################
# Make all of the Buttons Here
################################
# Declare all variables
button_font = pygame.font.SysFont('Calibri', 16, True, False)
button_color = (255, 249, 242)
button_greyed_color = (133, 105, 73)
button_image = pygame.image.load(
    "button_background.png").convert()  # image to be used as button background PLAY WITH THIS
button_width_1 = 100  # width of buttons PLAY WITH THIS
button_height = 64
button_size_1 = (button_width_1, button_height)
button_type_1 = pygame.transform.scale(button_image, button_size_1)  # transform size

button_width_2 = 455  # width of buttons PLAY WITH THIS
button_size_2 = (button_width_2, button_height)
button_type_2 = pygame.transform.scale(button_image, button_size_2)  # transform size

## height and width of info buttons
info_height = 32
info_width = 151
button_size_3 = (info_width, info_height)
button_type_3 = pygame.transform.scale(background_image, button_size_3)  # transform size

button_y_shift = (button_height)  # y-shift (spacing) of buttons PLAY WITH THIS

button_x_shift = (150)  # y-shift (spacing) of buttons PLAY WITH THIS

# Initialize and update individual BUTTONs: image, pos, text_input, font, base_color, hovering_color)
# Move Button
b_x = width - 455 + (button_width_1 / 2)
b_y = 512 + button_height / 2
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
# End Button
b_x = width - (button_width_2 / 2)
b_y = b_y + button_y_shift
b_end = Button(button_type_2, (b_x, b_y), "End Turn", button_font, button_color, button_greyed_color)
b_end.update(screen)

# Initialize Start Buttons
b_width_start = 140
b_height_start = 64
dist_between_buttons = 10
b_x_start = 10 + b_width_start / 2
b_y_start = 384 + b_height_start / 2
button_size_start = (b_width_start, b_height_start)
button_type_start = pygame.transform.scale(button_image, button_size_start)  # transform size

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
info_color = WHITE  ## UPDATE
info_title_color = (133, 105, 73)
info_greyed_color = (133, 105, 73)
notification_color = BLACK  ##UPDATE

# Initialize and update TEXTs: (self, position, text_input, font_input, bold_input, base_color, greyed_color)
################################
# Info Board
################################
# Print instrucdtions for how to use the info panel

# Names
t_x = vertical + (info_width / 2)
t_y_1 = 192 + (info_height / 2)
t_y = t_y_1
t_names = Button(button_type_3, (t_x, t_y), "NAMES", info_font, info_color, info_greyed_color)
# t_names = Text((t_x, t_y), "NAMES", info_font, info_font_bold, info_title_color, info_greyed_color)
t_names.update(screen)
# NOTE the following could be done in a loop like "for names in names_list", but I don't know how to create objects of unique names doing so

# Mustard
t_y = t_y_1 + info_y_shift
t_mustard = Button(button_type_3, (t_x, t_y), "Col. Mustard", info_font, info_color, info_greyed_color)
t_mustard.update(screen)

# Peacock
t_y = t_y + info_y_shift
t_peacock = Button(button_type_3, (t_x, t_y), "Mrs. Peacock", info_font, info_color, info_greyed_color)
t_peacock.update(screen)

# Plum
t_y = t_y + info_y_shift
t_plum = Button(button_type_3, (t_x, t_y), "Prof. Plum", info_font, info_color, info_greyed_color)
t_plum.update(screen)

# Scarlet
t_y = t_y + info_y_shift
t_scarlet = Button(button_type_3, (t_x, t_y), "Miss Scarlett", info_font, info_color, info_greyed_color)
t_scarlet.update(screen)

# White
t_y = t_y + info_y_shift
t_white = Button(button_type_3, (t_x, t_y), "Mrs. White", info_font, info_color, info_greyed_color)
t_white.update(screen)

# Green
t_y = t_y + info_y_shift
t_green = Button(button_type_3, (t_x, t_y), "Rev. Green", info_font, info_color, info_greyed_color)
t_green.update(screen)

# Weapons
t_x = t_x + info_width  # shift to the right for a new "column"
t_y = t_y_1
t_weapons = Button(button_type_3, (t_x, t_y), "WEAPONS", info_font, info_color, info_greyed_color)
t_weapons.update(screen)

# Candlestick
t_y = t_y + info_y_shift
t_candle = Button(button_type_3, (t_x, t_y), "Candlestick", info_font, info_color, info_greyed_color)
t_candle.update(screen)

# Dagger
t_y = t_y + info_y_shift
t_dagger = Button(button_type_3, (t_x, t_y), "Dagger", info_font, info_color, info_greyed_color)
t_dagger.update(screen)

# Lead Pipe
t_y = t_y + info_y_shift
t_pipe = Button(button_type_3, (t_x, t_y), "Lead Pipe", info_font, info_color, info_greyed_color)
t_pipe.update(screen)

# Rope
t_y = t_y + info_y_shift
t_rope = Button(button_type_3, (t_x, t_y), "Rope", info_font, info_color, info_greyed_color)
t_rope.update(screen)

# Wrench
t_y = t_y + info_y_shift
t_wrench = Button(button_type_3, (t_x, t_y), "Wrench", info_font, info_color, info_greyed_color)
t_wrench.update(screen)

# Revolver
t_y = t_y + info_y_shift
t_revolver = Button(button_type_3, (t_x, t_y), "Revolver", info_font, info_color, info_greyed_color)
t_revolver.update(screen)

# Rooms
t_x = t_x + info_width  # shift to the right for a new "column"
t_y = t_y_1
t_rooms = Button(button_type_3, (t_x, t_y), "ROOMS", info_font, info_color, info_greyed_color)
t_rooms.update(screen)

# Study
t_y = t_y + info_y_shift
t_study = Button(button_type_3, (t_x, t_y), "Study", info_font, info_color, info_greyed_color)
t_study.update(screen)

# Hall
t_y = t_y + info_y_shift
t_hall = Button(button_type_3, (t_x, t_y), "Hall", info_font, info_color, info_greyed_color)
t_hall.update(screen)

# Lounc
t_y = t_y + info_y_shift
t_lounge = Button(button_type_3, (t_x, t_y), "Lounge", info_font, info_color, info_greyed_color)
t_lounge.update(screen)

# Library
t_y = t_y + info_y_shift
t_library = Button(button_type_3, (t_x, t_y), "Library", info_font, info_color, info_greyed_color)
t_library.update(screen)

# Billiard Room
t_y = t_y + info_y_shift
t_billiard = Button(button_type_3, (t_x, t_y), "Billiard", info_font, info_color, info_greyed_color)
t_billiard.update(screen)

# Dining Room
t_y = t_y + info_y_shift
t_dining = Button(button_type_3, (t_x, t_y), "Dining", info_font, info_color, info_greyed_color)
t_dining.update(screen)

# Conservatory
t_y = t_y + info_y_shift
t_conservatory = Button(button_type_3, (t_x, t_y), "Conservatory", info_font, info_color, info_greyed_color)
t_conservatory.update(screen)

# Ballroom
t_y = t_y + info_y_shift
t_ballroom = Button(button_type_3, (t_x, t_y), "Ballroom", info_font, info_color, info_greyed_color)
t_ballroom.update(screen)

# Kitchen
t_y = t_y + info_y_shift
t_kitchen = Button(button_type_3, (t_x, t_y), "Kitchen", info_font, info_color, info_greyed_color)
t_kitchen.update(screen)

################################
# Notifications
#################################
t_x = vertical + 5
t_y = 5
fontHeight = 18
t_line1 = Text((vertical + 5, 5), "", notification_font, info_font_bold, notification_color, notification_color)
t_line1.update(screen)
t_line2 = Text((vertical + 5, 5 + 1 * fontHeight), "", notification_font, info_font_bold, notification_color,
               notification_color)
t_line2.update(screen)
t_line3 = Text((vertical + 5, 5 + 2 * fontHeight), "", notification_font, info_font_bold, notification_color,
               notification_color)
t_line3.update(screen)
t_line4 = Text((vertical + 5, 5 + 3 * fontHeight), "", notification_font, info_font_bold, notification_color,
               notification_color)
t_line4.update(screen)
t_line5 = Text((vertical + 5, 5 + 4 * fontHeight), "", notification_font, info_font_bold, notification_color,
               notification_color)
t_line5.update(screen)
t_line6 = Text((vertical + 5, 5 + 5 * fontHeight), "", notification_font, info_font_bold, notification_color,
               notification_color)
t_line6.update(screen)
t_line7 = Text((vertical + 5, 5 + 6 * fontHeight), "", notification_font, info_font_bold, notification_color,
               notification_color)
t_line7.update(screen)
t_line8 = Text((vertical + 5, 5 + 7 * fontHeight), "", notification_font, info_font_bold, notification_color,
               notification_color)
t_line8.update(screen)
t_line9 = Text((vertical + 5, 5 + 8 * fontHeight), "", notification_font, info_font_bold, notification_color,
               notification_color)
t_line9.update(screen)
t_line10 = Text((vertical + 5, 5 + 9 * fontHeight), "", notification_font, info_font_bold, notification_color,
                notification_color)
t_line10.update(screen)

numLinesFilled = 3


def updateNotifications(text1, text2, text3, text4, text5, text6, text7, text8, text9, text10):
    pygame.draw.rect(screen, WHITE, [vertical, 0, vertical, 192])
    pygame.draw.rect(screen, RED, [vertical, 0, vertical, 192], 2)
    t_line1 = Text((vertical + 5, 5), text1, notification_font, info_font_bold, notification_color, notification_color)
    t_line1.update(screen)
    t_line2 = Text((vertical + 5, 5 + 1 * fontHeight), text2, notification_font, info_font_bold, notification_color,
                   notification_color)
    t_line2.update(screen)
    t_line3 = Text((vertical + 5, 5 + 2 * fontHeight), text3, notification_font, info_font_bold, notification_color,
                   notification_color)
    t_line3.update(screen)
    t_line4 = Text((vertical + 5, 5 + 3 * fontHeight), text4, notification_font, info_font_bold, notification_color,
                   notification_color)
    t_line4.update(screen)
    t_line5 = Text((vertical + 5, 5 + 4 * fontHeight), text5, notification_font, info_font_bold, notification_color,
                   notification_color)
    t_line5.update(screen)
    t_line6 = Text((vertical + 5, 5 + 5 * fontHeight), text6, notification_font, info_font_bold, notification_color,
                   notification_color)
    t_line6.update(screen)
    t_line7 = Text((vertical + 5, 5 + 6 * fontHeight), text7, notification_font, info_font_bold, notification_color,
                   notification_color)
    t_line7.update(screen)
    t_line8 = Text((vertical + 5, 5 + 7 * fontHeight), text8, notification_font, info_font_bold, notification_color,
                   notification_color)
    t_line8.update(screen)
    t_line9 = Text((vertical + 5, 5 + 8 * fontHeight), text9, notification_font, info_font_bold, notification_color,
                   notification_color)
    t_line9.update(screen)
    t_line10 = Text((vertical + 5, 5 + 9 * fontHeight), text10, notification_font, info_font_bold, notification_color,
                    notification_color)
    t_line10.update(screen)
    global not_text1
    global not_text2
    global not_text3
    global not_text4
    global not_text5
    global not_text6
    global not_text7
    global not_text8
    global not_text9
    global not_text10
    not_text1 = text1
    not_text2 = text2
    not_text3 = text3
    not_text4 = text4
    not_text5 = text5
    not_text6 = text6
    not_text7 = text7
    not_text8 = text8
    not_text9 = text9
    not_text10 = text10


def addNewNotificationLine(text):
    global not_text1
    global not_text2
    global not_text3
    global not_text4
    global not_text5
    global not_text6
    global not_text7
    global not_text8
    global not_text9
    global not_text10
    global numLinesFilled

    if "\n" in not_text1:
        not_text1 = not_text1.split("\n")[0]
    if "\n" in not_text2:
        not_text1 = not_text1.split("\n")[0]
    if "\n" in not_text3:
        not_text1 = not_text1.split("\n")[0]
    if "\n" in not_text4:
        not_text1 = not_text1.split("\n")[0]
    if "\n" in not_text5:
        not_text1 = not_text1.split("\n")[0]
    if "\n" in not_text6:
        not_text1 = not_text1.split("\n")[0]
    if "\n" in not_text7:
        not_text1 = not_text1.split("\n")[0]
    if "\n" in not_text8:
        not_text1 = not_text1.split("\n")[0]
    if "\n" in not_text9:
        not_text1 = not_text1.split("\n")[0]
    if "\n" in not_text10:
        not_text1 = not_text1.split("\n")[0]

    numLinesFilled = numLinesFilled + 1
    if numLinesFilled == 4:
        if (("is suggesting" not in not_text2) or (text not in not_text2)) and (text not in not_text3):
            
            updateNotifications(not_text1, not_text2, not_text3, text, "", "", "", "", "", "")
    elif numLinesFilled == 5:
        if (("is suggesting" not in not_text3) or (text not in not_text3)) and (text not in not_text4):
            updateNotifications(not_text1, not_text2, not_text3, not_text4, text, "", "", "", "", "")
    elif numLinesFilled == 6:
        if (("is suggesting" not in not_text4) or (text not in not_text4)) and (text not in not_text5):
            updateNotifications(not_text1, not_text2, not_text3, not_text4, not_text5, text, "", "", "", "")
    elif numLinesFilled == 7:
        if (("is suggesting" not in not_text5) or (text not in not_text5)) and (text not in not_text6):
            updateNotifications(not_text1, not_text2, not_text3, not_text4, not_text5, not_text6, text, "", "", "")
    elif numLinesFilled == 8:
        if (("is suggesting" not in not_text6) or (text not in not_text6)) and (text not in not_text7):
            updateNotifications(not_text1, not_text2, not_text3, not_text4, not_text5, not_text6, not_text7, text, "", "")
    elif numLinesFilled == 9:
        if (("is suggesting" not in not_text7) or (text not in not_text7)) and (text not in not_text8):
            updateNotifications(not_text1, not_text2, not_text3, not_text4, not_text5, not_text6, not_text7, not_text8,
                            text, "")
    elif numLinesFilled == 10:
        if (("is suggesting" not in not_text8) or (text not in not_text8)) and (text not in not_text9):
            updateNotifications(not_text1, not_text2, not_text3, not_text4, not_text5, not_text6, not_text7, not_text8,
                            not_text9, text)
    else:
        if (("is suggesting" not in not_text9) or (text not in not_text9)) and (text not in not_text10):
            not_text3 = not_text4
            not_text4 = not_text5
            not_text5 = not_text6
            not_text6 = not_text7
            not_text7 = not_text8
            not_text8 = not_text9
            not_text9 = not_text10
            not_text10 = (text)
            updateNotifications(not_text1, not_text2, not_text3, not_text4, not_text5, not_text6, not_text7, not_text8,
                                not_text9, not_text10)


currentPlayerLocations = ""

first_beginning_screen = False
second_beginning_screen = False
gameStarted = False
gDefined = False
gameOver = False

playerLocDict = {"Miss Scarlett": "None", "Colonel Mustard": "None", "Mrs. White": "None", "Reverend Green": "None",
                 "Mrs. Peacock": "None", "Professor Plum": "None"}

t_x_notification2 = t_x
t_y_notification2 = t_y + 3*notification_y_shift
t_notification2= Text((t_x_notification2, t_y_notification2), "Initial", notification_font, info_font_bold, notification_color, notification_color)
t_notification2.update(screen)

def updateNotifications(text1, text2, text3, text4):
    pygame.draw.rect(screen, WHITE, [0, hLeft, vertical, height])
    pygame.draw.rect(screen, RED, [0, hLeft, vertical, height], 2)
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
canClickButtons = False
done = False
clock = pygame.time.Clock()
gameStarted = False

start_button_list = []
start_char_button_list = []

while not done:
    pygame.draw.rect(screen, BLACK, [0, 0, vertical, height], 2)  # Draw a rectangle around the map
    pygame.draw.rect(screen, RED, [vertical, 0, width - vertical, 192], 2)  # Notification Panel
    pygame.draw.rect(screen, BLACK, [vertical, 192, width - vertical, 320], 2)  # Scorecard Panel
    pygame.draw.rect(screen, BLUE, [vertical, hRight, width - vertical, height], 2)  # Action Panel

    pygame.display.flip()
    clock.tick(60)

    pos = pygame.mouse.get_pos()
    game_buttons = [b_move, b_suggest, b_accuse, b_end, t_kitchen, t_ballroom, t_billiard, t_candle,
                    t_conservatory, t_dagger, t_dining, t_hall, t_library, t_lounge, t_mustard,
                    t_peacock, t_pipe, t_plum, t_candle, t_green, t_revolver,
                    t_scarlet, t_study, t_white, t_wrench, t_rope]

    if first_beginning_screen is False and second_beginning_screen is False:
        for button in game_buttons:
            button.update(screen)
            button.changeColor(pos)

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user closes window
            done = True  # Flag to exit the loop

        if event.type == SERVER_MESSAGE:  # If the server sends a message
            readmsg = event.message

            if ((WIN_MSG in readmsg) and canClickButtons) or ((WIN_MSG2 in readmsg) and canClickButtons):
                accusationStatement = readmsg.split("****")[1].split("accusing ")
                addNewNotificationLine(accusationStatement[0]+" accusing:")
                if "\n" in accusationStatement[1]:
                    accusationStatement[1] = accusationStatement[1].split("\n")[0]
                addNewNotificationLine(accusationStatement[1]+".")
                addNewNotificationLine("Player " +currentPlayer + " won the game!")
                winning = pygame.image.load("winScreen.png").convert()  # load image
                winning = pygame.transform.scale(winning, boardSize)  # transform size
                screen.blit(winning, boardLocation)  ##populate on screen
                pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                pygame.display.update()
                msg = "endConnection for all"
            elif ((WIN_MSG in readmsg) or (WIN_MSG2 in readmsg) and not canClickButtons):
                accusationStatement = readmsg.split("****")[1].split("accusing ")
                addNewNotificationLine(accusationStatement[0]+" accusing:")
                if "\n" in accusationStatement[1]:
                    accusationStatement[1] = accusationStatement[1].split("\n")[0]
                addNewNotificationLine(accusationStatement[1]+".")
                addNewNotificationLine("Player " +currentPlayer + " won the game!")
                if "\n" in accusationStatement:
                    accusationStatement = accusationStatement.split("\n")[0]
                losing = pygame.image.load("loseScreen.png").convert()  # load image
                losing = pygame.transform.scale(losing, boardSize)  # transform size
                screen.blit(losing, boardLocation)  ##populate on screen
                pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                pygame.display.update()
                msg = "endConnection for player"
                pygame.event.clear()

            if ((LOSE_MSG in readmsg) and canClickButtons) or ((WIN_MSG in readmsg) and (not canClickButtons)):
                accusationStatement = readmsg.split("****")[1].split("accusing ")
                addNewNotificationLine(accusationStatement[0]+" accusing:")
                if "\n" in accusationStatement[1]:
                    accusationStatement[1] = accusationStatement[1].split("\n")[0]
                addNewNotificationLine(accusationStatement[1]+".")
                addNewNotificationLine("Player " +currentPlayer + " lost the game.")
                losing = pygame.image.load("loseScreen.png").convert()  # load image
                losing = pygame.transform.scale(losing, boardSize)  # transform size
                screen.blit(losing, boardLocation)  ##populate on screen
                pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                pygame.display.update()
                msg = "endConnection for player"
                pygame.event.clear()

            if (LOSE_MSG in readmsg) and not canClickButtons:
                if "****" in readmsg:
                    accusation = readmsg.split("****")[1].split("accusing ")
                    addNewNotificationLine(accusation[0]+" accusing:")
                if "\n" in accusation[1]:
                    accusation[1] = accusation[1].split("\n")[0]
                    addNewNotificationLine(accusation[1]+".")
                addNewNotificationLine("Player " +currentPlayer + " lost the game.")

            if ("CLOSE ALL CONNECTION" in readmsg):
                if("****" in readmsg):
                    readmsg = readmsg.split("****")[1].split(",")
                    if (readmsg[2]) and (int(readmsg[2]) == int(p.playerNumber)):
                        defaultWon = readmsg[2]
                        defaultWonText = Text((1055, 525), defaultWon, action_font, action_font, (0, 0, 0), notification_color)
                        defaultWonText.update(screen)
                        winning = pygame.image.load("winScreen.png").convert()  # load image
                        winning = pygame.transform.scale(winning, boardSize)  # transform size
                        screen.blit(winning, boardLocation)  ##populate on screen
                        pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                        pygame.display.update()
                        pygame.event.clear()
                    else:
                        losing = pygame.image.load("loseScreen.png").convert()  # load image
                        losing = pygame.transform.scale(losing, boardSize)  # transform size
                        screen.blit(losing, boardLocation)  ##populate on screen
                        pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                        pygame.display.update()
                        msg = "endConnection for player"
                        pygame.event.clear()
                else:
                    readmsg = readmsg = readmsg.split(",")
                    if (readmsg[2]) and (int(readmsg[2]) == int(p.playerNumber)):
                        defaultWon = readmsg[2]
                        defaultWonText = Text((1055, 525), defaultWon, action_font, action_font, (0, 0, 0), notification_color)
                        defaultWonText.update(screen)
                        winning = pygame.image.load("winScreen.png").convert()  # load image
                        winning = pygame.transform.scale(winning, boardSize)  # transform size
                        screen.blit(winning, boardLocation)  ##populate on screen
                        pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                        pygame.display.update()
                        pygame.event.clear()
                    else:
                        losing = pygame.image.load("loseScreen.png").convert()  # load image
                        losing = pygame.transform.scale(losing, boardSize)  # transform size
                        screen.blit(losing, boardLocation)  ##populate on screen
                        msg = "endConnection for player"
                        pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                        pygame.display.update()
                        pygame.event.clear()

            if CONNECTED_MSG in readmsg and waitingForSuggestion == False:
                myNumber = readmsg.split("You are Player ")[1].split(".")[0]
                if (int(myNumber) == 1):
                    updateNotifications(readmsg[1:] + ".", "", "", "", "", "", "", "", "", "")
                    first_beginning_screen = True
                    second_beginning_screen = False
                    firstBoardImage = pygame.image.load("firstStartScreen.png").convert()
                    firstBoardImage = pygame.transform.scale(firstBoardImage, boardSize)
                    screen.blit(firstBoardImage, boardLocation)

                    b_x_start_updated = b_x_start + 75
                    b_start2 = Button(button_type_start,
                                      (b_x_start_updated + 0 * (b_width_start + dist_between_buttons), b_y_start), "2",
                                      button_font, button_color, button_greyed_color)
                    b_start2.update(screen)

                    b_start3 = Button(button_type_start,
                                      (b_x_start_updated + 1 * (b_width_start + dist_between_buttons), b_y_start), "3",
                                      button_font, button_color, button_greyed_color)
                    b_start3.update(screen)

                    b_start4 = Button(button_type_start,
                                      (b_x_start_updated + 2 * (b_width_start + dist_between_buttons), b_y_start), "4",
                                      button_font, button_color, button_greyed_color)
                    b_start4.update(screen)

                    b_start5 = Button(button_type_start,
                                      (b_x_start_updated + 3 * (b_width_start + dist_between_buttons), b_y_start), "5",
                                      button_font, button_color, button_greyed_color)
                    b_start5.update(screen)

                    b_start6 = Button(button_type_start,
                                      (b_x_start_updated + 4 * (b_width_start + dist_between_buttons), b_y_start), "6",
                                      button_font, button_color, button_greyed_color)
                    b_start6.update(screen)

                    start_buttons = [b_start2, b_start3, b_start4, b_start5, b_start6]
                    for button in start_buttons:
                        start_button_list.append(button)

                else:
                    first_beginning_screen = False
                    second_beginning_screen = True
                    secondBoardImage = pygame.image.load("secondStartScreen.png").convert()
                    secondBoardImage = pygame.transform.scale(secondBoardImage, boardSize)
                    screen.blit(secondBoardImage, boardLocation)
                    updateNotifications(readmsg[1:41] + ".", "", "", "", "", "", "", "", "", "")

            if PLAYER_CHOICE_MESSAGE in readmsg and waitingForSuggestion == False:
                if "Mustard" in readmsg:
                    mustardChosen = False
                else:
                    mustardChosen = True
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
                    b_startMustard = Button(button_type_start, (b_x_start, b_y_start), "Colonel Mustard", button_font,
                                            button_color, button_greyed_color)
                    b_startMustard.update(screen)
                    start_char_button_list.append(b_startMustard)
                if peacockChosen == False:
                    b_startPeacock = Button(button_type_start,
                                            (b_x_start + 1 * (b_width_start + dist_between_buttons), b_y_start),
                                            "Mrs. Peacock", button_font, button_color, button_greyed_color)
                    b_startPeacock.update(screen)
                    start_char_button_list.append(b_startPeacock)
                if plumChosen == False:
                    b_startPlum = Button(button_type_start,
                                         (b_x_start + 2 * (b_width_start + dist_between_buttons), b_y_start),
                                         "Professor Plum", button_font, button_color, button_greyed_color)
                    b_startPlum.update(screen)
                    start_char_button_list.append(b_startPlum)
                if scarletChosen == False:
                    b_startScarlet = Button(button_type_start,
                                            (b_x_start + 3 * (b_width_start + dist_between_buttons), b_y_start),
                                            "Miss Scarlett", button_font, button_color, button_greyed_color)
                    b_startScarlet.update(screen)
                    start_char_button_list.append(b_startScarlet)
                if whiteChosen == False:
                    b_startWhite = Button(button_type_start,
                                          (b_x_start + 4 * (b_width_start + dist_between_buttons), b_y_start),
                                          "Mrs. White", button_font, button_color, button_greyed_color)
                    b_startWhite.update(screen)
                    start_char_button_list.append(b_startWhite)
                if greenChosen == False:
                    b_startGreen = Button(button_type_start,
                                          (b_x_start + 5 * (b_width_start + dist_between_buttons), b_y_start),
                                          "Reverend Green", button_font, button_color, button_greyed_color)
                    b_startGreen.update(screen)
                    start_char_button_list.append(b_startGreen)

            if BEGINNING_MSG in readmsg and waitingForSuggestion == False:
                cards = readmsg.split("Your cards are: ")[1]
                if ("Next Turn" in cards):
                    cards = cards.split("N")[0]
                setattr(p, 'cards', ast.literal_eval(cards))
                playerText = p.playerName + ", you are Player " + str(p.playerNumber) + "."
                cardText = cards[:-3]
                cardText = cardText.replace('[', '')
                cardText = cardText.replace(']', '')
                cardText = cardText.replace('\'', '')
                cardText = cardText.replace('Colonel', 'Col.')
                cardText = cardText.replace('Reverend', 'Rev.')
                cardText = cardText.replace('Professor', 'Prof.')
                cardText = cardText + "."
                cardTextForCount = cardText.split(", ")
                updateNotifications(playerText, "", readmsg[1:34], "", "", "", "", "", "", "")

                numPlayersInGame = int(readmsg[24])
                t_card1 = Text((911 + 5, 33 + 387), "Click on cards to track what you know.", action_font, action_font,
                               notification_color, notification_color)
                t_card1.update(screen)
                t_card2 = Text((911 + 5, 25 + 385 + 2 * (fontHeight - 2)),
                               "Your " + str(len(cardTextForCount)) + " cards are:", action_font, action_font,
                               notification_color, notification_color)
                t_card2.update(screen)

                if len(cardTextForCount) == 0:
                    cardLine3 = ""
                elif len(cardTextForCount) == 1:
                    cardLine3 = cardTextForCount[0]
                elif len(cardTextForCount) == 2:
                    cardLine3 = cardTextForCount[0] + ", " + cardTextForCount[1]
                elif len(cardTextForCount) == 3:
                    cardLine3 = cardTextForCount[0] + ", " + cardTextForCount[1] + ", " + cardTextForCount[2]
                else:
                    cardLine3 = cardTextForCount[0] + ", " + cardTextForCount[1] + ", " + cardTextForCount[2] + ","
                t_card3 = Text((911 + 5, 25 + 385 + 3 * (fontHeight - 2)), cardLine3, action_font, action_font,
                               notification_color, notification_color)
                t_card3.update(screen)

                if len(cardTextForCount) <= 3:
                    cardLine4 = ""
                elif len(cardTextForCount) == 4:
                    cardLine4 = cardTextForCount[3]
                elif len(cardTextForCount) == 5:
                    cardLine4 = cardTextForCount[3] + ", " + cardTextForCount[4]
                elif len(cardTextForCount) == 6:
                    cardLine4 = cardTextForCount[3] + ", " + cardTextForCount[4] + ", " + cardTextForCount[5]
                else:
                    cardLine4 = cardTextForCount[3] + ", " + cardTextForCount[4] + ", " + cardTextForCount[5] + ","
                t_card4 = Text((911 + 5, 25 + 385 + 4 * (fontHeight - 2)), cardLine4, action_font, action_font,
                               notification_color, notification_color)
                t_card4.update(screen)

                if len(cardTextForCount) <= 6:
                    cardLine5 = ""
                elif len(cardTextForCount) == 7:
                    cardLine5 = cardTextForCount[6]
                elif len(cardTextForCount) == 8:
                    cardLine5 = cardTextForCount[6] + ", " + cardTextForCount[7]
                else:
                    cardLine5 = cardTextForCount[6] + ", " + cardTextForCount[7] + ", " + cardTextForCount[8]
                t_card5 = Text((911 + 5, 25 + 385 + 5 * (fontHeight - 2)), cardLine5, action_font, action_font,
                               notification_color, notification_color)
                t_card5.update(screen)

                boardImage = pygame.image.load("gameboard.png").convert()  # load image
                boardImage = pygame.transform.scale(boardImage, boardSize)  # transform size
                screen.blit(boardImage, boardLocation)  ##populate on screen

            if TURN_MSG in readmsg:
                if "****" in readmsg:
                    split = readmsg.split("\n")
                    readmsg = readmsg.split("\n")[1]
                    if(split[3] != ""):
                        currentPlayerLocations = split[3].split("|||||")[1]
                    else:
                        currentPlayerLocations = split[4].split("|||||")[1]
                else:
                    currentPlayerLocations = readmsg.split("|||||")[1]
                
                playerTurn = readmsg.split("Player ")[1].split(".")[0]
                if "is suggesting" in playerTurn:
                    playerTurn = playerTurn.split(" is suggesting")[0]
                if "is accusing" in playerTurn:
                    playerTurn = playerTurn.split(" is accusing")[0]
                if int(playerTurn) != int(currentPlayer):
                    currentPlayer = playerTurn
                    addNewNotificationLine("Next Turn: Player" + str(playerTurn))
                if "Player " + str(p.playerNumber) in readmsg:
                    canClickButtons = True
                    addNewNotificationLine("It's your turn.")
                else:
                    canClickButtons = False
                    p.hasMoved = False
                    p.canEndTurn = False
                    p.hasSuggested = False
                    currentButtons = []
                    buttonsClicked = False
                    suggesting = False
                    accusing = False
                    addNewNotificationLine(readmsg.split("|||||")[0][1:])

            if "is moving to" in readmsg:
                if "Next Turn" in readmsg:
                    readmsg = readmsg.split("\nNext Turn")[0]
                tempMsg = readmsg
                tempMsg = tempMsg.replace("room1", "study")
                tempMsg = tempMsg.replace("room2", "hall")
                tempMsg = tempMsg.replace("room3", "lounge")
                tempMsg = tempMsg.replace("room4", "dining room")
                tempMsg = tempMsg.replace("room5", "kitchen")
                tempMsg = tempMsg.replace("room6", "ballroom")
                tempMsg = tempMsg.replace("room7", "conservatory")
                tempMsg = tempMsg.replace("room8", "library")
                tempMsg = tempMsg.replace("room9", "billiard room")
                addNewNotificationLine(tempMsg)

                if "Mustard" in readmsg:
                    player = "Colonel Mustard"
                if "Peacock" in readmsg:
                    player = "Mrs. Peacock"
                if "Plum" in readmsg:
                    player = "Professor Plum"
                if "Scarlett" in readmsg:
                    player = "Miss Scarlett"
                if "White" in readmsg:
                    player = "Mrs. White"
                if "Green" in readmsg:
                    player = "Reverend Green"

                if "study" in readmsg or "room1" in readmsg:
                    location = "study"
                if "hall" in readmsg or "room2" in readmsg:
                    location = "hall"
                if "lounge" in readmsg or "room3" in readmsg:
                    location = "lounge"
                if "dining room" in readmsg or "room4" in readmsg:
                    location = "dining room"
                if "kitchen" in readmsg or "room5" in readmsg:
                    location = "kitchen"
                if "ballroom" in readmsg or "room6" in readmsg:
                    location = "ballroom"
                if "conservatory" in readmsg or "room7" in readmsg:
                    location = "conservatory"
                if "library" in readmsg or "room8" in readmsg:
                    location = "library"
                if "billiard room" in readmsg or "room9" in readmsg:
                    location = "billiard room"
                if "hallway12" in readmsg:
                    location = "hallway12"
                if "hallway23" in readmsg:
                    location = "hallway23"
                if "hallway89" in readmsg:
                    location = "hallway89"
                if "hallway49" in readmsg:
                    location = "hallway49"
                if "hallway67" in readmsg:
                    location = "hallway67"
                if "hallway56" in readmsg:
                    location = "hallway56"
                if "hallway81" in readmsg:
                    location = "hallway81"
                if "hallway29" in readmsg:
                    location = "hallway29"
                if "hallway34" in readmsg:
                    location = "hallway34"
                if "hallway78" in readmsg:
                    location = "hallway78"
                if "hallway69" in readmsg:
                    location = "hallway69"
                if "hallway45" in readmsg:
                    location = "hallway45"
                playerLocDict[player] = location
                movePlayerImages(playerLocDict)

            if "is suggesting" in readmsg:
                addNewNotificationLine(readmsg[:23] + ":")
                tempText = readmsg[23:]
                tempText = tempText.split("///")[0]
                addNewNotificationLine(tempText[:-2])

                if "Mustard" in readmsg:
                    player = "Colonel Mustard"
                if "Peacock" in readmsg:
                    player = "Mrs. Peacock"
                if "Plum" in readmsg:
                    player = "Professor Plum"
                if "Scarlett" in readmsg:
                    player = "Miss Scarlett"
                if "White" in readmsg:
                    player = "Mrs. White"
                if "Green" in readmsg:
                    player = "Reverend Green"

                if "study" in readmsg or "room1" in readmsg:
                    location = "study"
                if "hall" in readmsg or "room2" in readmsg:
                    location = "hall"
                if "lounge" in readmsg or "room3" in readmsg:
                    location = "lounge"
                if "dining room" in readmsg or "room4" in readmsg:
                    location = "dining room"
                if "kitchen" in readmsg or "room5" in readmsg:
                    location = "kitchen"
                if "ballroom" in readmsg or "room6" in readmsg:
                    location = "ballroom"
                if "conservatory" in readmsg or "room7" in readmsg:
                    location = "conservatory"
                if "library" in readmsg or "room8" in readmsg:
                    location = "library"
                if "billiard room" in readmsg or "room9" in readmsg:
                    location = "billiard room"
                playerLocDict[player] = location
                movePlayerImages(playerLocDict)

            if ("is suggesting" in readmsg) and canClickButtons and suggesting:
                waitingForSuggestion = True
                clientsMessage = readmsg.split("///")[0]

            if waitingForSuggestion == True and ("suggestionHelpMade" in readmsg):
                suggestionHelpMessage = readmsg.split(" ///")
                if "No player has cards that match your suggestion" in suggestionHelpMessage:
                    suggestion = suggestionHelpMessage
                    noSuggestionFont = pygame.font.SysFont('Calibri', 14, False, False)
                    noSuggestionHelp = "No player has cards that match your suggestion."
                    noSuggestionHelpText = Text((1030, 525), noSuggestionHelp, noSuggestionFont, noSuggestionFont,
                                                (0, 0, 0), notification_color)
                    noSuggestionHelpText.update(screen)
                    p.hasSuggested = True
                    p.hasMoved = True
                    p.canEndTurn = True
                    suggesting = False
                    msg = "KEEP SAME PLAYER TURN"
                    s.send(msg.encode(form))
                else:
                    suggestionHelp1 = "Another player is suggesting that"
                    suggestionHelpText1 = Text((1055, 525), suggestionHelp1, action_font, action_font, (0, 0, 0),
                                               notification_color)
                    suggestionHelpText1.update(screen)
                    suggestionHelp2 = "[ " + str(suggestionHelpMessage[0]) + " ]"
                    suggestionHelpText2 = Text((1105, 545), suggestionHelp2, action_font, action_font, (0, 0, 0),
                                               notification_color)
                    suggestionHelpText2.update(screen)
                    suggestionHelp3 = "is not in the solution."
                    suggestionHelpText3 = Text((1085, 565), suggestionHelp3, action_font, action_font, (0, 0, 0),
                                               notification_color)
                    suggestionHelpText3.update(screen)
                    msg = "KEEP SAME PLAYER TURN"
                    s.send(msg.encode(form))
                    suggesting = False
                    p.hasSuggested = True
                    p.hasMoved = True
                    p.canEndTurn = True

            if ("is suggesting" in readmsg) and (not canClickButtons):
                playerSuggesting = readmsg.split("///")[0][7]
                cardsToCheck = readmsg.split("///")[1]
                suggestions = cardsToCheck.split(",")
                if (p.playerName == suggestions[0]):
                    keys = [k for k, v in roomsToNames.items() if v == suggestions[1]]
                    p.playerLocation = keys[0]
                    p.canSuggest = True
                if p.playerNumber in cardsToCheck:
                    count = 0
                    matches = []
                    playerCards = getattr(p, 'cards')
                    if ((suggestions[0] in p.cards) or (suggestions[1] in p.cards) or (suggestions[2] in p.cards)):
                        count += 1
                        for i in suggestions:
                            if i in p.cards:
                                matches.append(i)
                        p.helpingSuggestion = True
                        helpButtons = printSuggestionHelpButtons(playerSuggesting, matches)
                        currentButtons = helpButtons
                    else:
                        count += 1
                        message = "No matches please move to next player"
                        s.send(message.encode())
                    nextMessage = "Move " + suggestions[0] + " to " + suggestions[1] + ".\n"
                    playerMoveActive = False


        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if second_beginning_screen == True:
                updateSecondBeginningScreen = False
                if mustardChosen == False:
                    if b_startMustard.isOver(pos, b_width_start, b_height_start):
                        updateSecondBeginningScreen = True
                        message = ("Colonel Mustard")
                if peacockChosen == False:
                    if b_startPeacock.isOver(pos, b_width_start, b_height_start):
                        updateSecondBeginningScreen = True
                        message = "Mrs. Peacock"
                if plumChosen == False:
                    if b_startPlum.isOver(pos, b_width_start, b_height_start):
                        updateSecondBeginningScreen = True
                        message = "Professor Plum"
                if scarletChosen == False:
                    if b_startScarlet.isOver(pos, b_width_start, b_height_start):
                        updateSecondBeginningScreen = True
                        message = "Miss Scarlett"
                if whiteChosen == False:
                    if b_startWhite.isOver(pos, b_width_start, b_height_start):
                        updateSecondBeginningScreen = True
                        message = "Mrs. White"
                if greenChosen == False:
                    if b_startGreen.isOver(pos, b_width_start, b_height_start):
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
                    updateFirstBeginningScreen = True
                    inputNumPlayers = "2"

                if b_start3.isOver(pos, b_width_start, b_height_start):
                    updateFirstBeginningScreen = True
                    inputNumPlayers = "3"

                if b_start4.isOver(pos, b_width_start, b_height_start):
                    updateFirstBeginningScreen = True
                    inputNumPlayers = "4"

                if b_start5.isOver(pos, b_width_start, b_height_start):
                    updateFirstBeginningScreen = True
                    inputNumPlayers = "5"

                if b_start6.isOver(pos, b_width_start, b_height_start):
                    updateFirstBeginningScreen = True
                    inputNumPlayers = "6"

                if updateFirstBeginningScreen == True:
                    first_beginning_screen = False
                    second_beginning_screen = True
                    secondBoardImage = pygame.image.load("secondStartScreen.png").convert()
                    secondBoardImage = pygame.transform.scale(secondBoardImage, boardSize)
                    screen.blit(secondBoardImage, boardLocation)
                    b_startMustard = Button(button_type_start, (b_x_start, b_y_start), "Colonel Mustard", button_font,
                                            button_color, button_greyed_color)
                    b_startMustard.update(screen)
                    b_startPeacock = Button(button_type_start,
                                            (b_x_start + 1 * (b_width_start + dist_between_buttons), b_y_start),
                                            "Mrs. Peacock", button_font, button_color, button_greyed_color)
                    b_startPeacock.update(screen)
                    b_startPlum = Button(button_type_start,
                                         (b_x_start + 2 * (b_width_start + dist_between_buttons), b_y_start),
                                         "Professor Plum", button_font, button_color, button_greyed_color)
                    b_startPlum.update(screen)
                    b_startScarlet = Button(button_type_start,
                                            (b_x_start + 3 * (b_width_start + dist_between_buttons), b_y_start),
                                            "Miss Scarlett", button_font, button_color, button_greyed_color)
                    b_startScarlet.update(screen)
                    b_startWhite = Button(button_type_start,
                                          (b_x_start + 4 * (b_width_start + dist_between_buttons), b_y_start),
                                          "Mrs. White", button_font, button_color, button_greyed_color)
                    b_startWhite.update(screen)
                    b_startGreen = Button(button_type_start,
                                          (b_x_start + 5 * (b_width_start + dist_between_buttons), b_y_start),
                                          "Reverend Green", button_font, button_color, button_greyed_color)
                    b_startGreen.update(screen)
                    s.send(inputNumPlayers.encode())

            # updating player card: people
            if t_mustard.isOver(pos, info_width, info_height):
                if t_mustard.bolded == False:
                    t_mustard = Button(t_mustard.image, (t_mustard.x_pos, t_mustard.y_pos), t_mustard.text_input,
                                       info_font_bold, t_mustard.base_color, t_mustard.hovering_color)
                    t_mustard.bolded = True
                    t_mustard.update(screen)
                else:
                    t_mustard = Button(t_mustard.image, (t_mustard.x_pos, t_mustard.y_pos), t_mustard.text_input,
                                       info_font, t_mustard.base_color, t_mustard.hovering_color)
                    t_mustard.bolded = False
                    t_mustard.update(screen)
            if t_peacock.isOver(pos, info_width, info_height):
                if t_peacock.bolded == False:
                    t_peacock = Button(t_peacock.image, (t_peacock.x_pos, t_peacock.y_pos), t_peacock.text_input,
                                       info_font_bold, t_peacock.base_color, t_peacock.hovering_color)
                    t_peacock.bolded = True
                    t_peacock.update(screen)
                else:
                    t_peacock = Button(t_peacock.image, (t_peacock.x_pos, t_peacock.y_pos), t_peacock.text_input,
                                       info_font, t_peacock.base_color, t_peacock.hovering_color)
                    t_peacock.bolded = False
                    t_peacock.update(screen)
            if t_plum.isOver(pos, info_width, info_height):
                if t_plum.bolded == False:
                    t_plum = Button(t_plum.image, (t_plum.x_pos, t_plum.y_pos), t_plum.text_input, info_font_bold,
                                    t_plum.base_color, t_plum.hovering_color)
                    t_plum.bolded = True
                    t_plum.update(screen)
                else:
                    t_plum = Button(t_plum.image, (t_plum.x_pos, t_plum.y_pos), t_plum.text_input, info_font,
                                    t_plum.base_color, t_plum.hovering_color)
                    t_plum.bolded = False
                    t_plum.update(screen)
            if t_scarlet.isOver(pos, info_width, info_height):
                if t_scarlet.bolded == False:
                    t_scarlet = Button(t_scarlet.image, (t_scarlet.x_pos, t_scarlet.y_pos), t_scarlet.text_input,
                                       info_font_bold, t_scarlet.base_color, t_scarlet.hovering_color)
                    t_scarlet.bolded = True
                    t_scarlet.update(screen)
                else:
                    t_scarlet = Button(t_scarlet.image, (t_scarlet.x_pos, t_scarlet.y_pos), t_scarlet.text_input,
                                       info_font, t_scarlet.base_color, t_scarlet.hovering_color)
                    t_scarlet.bolded = False
                    t_scarlet.update(screen)
            if t_white.isOver(pos, info_width, info_height):
                if t_white.bolded == False:
                    t_white = Button(t_white.image, (t_white.x_pos, t_white.y_pos), t_white.text_input, info_font_bold,
                                     t_white.base_color, t_white.hovering_color)
                    t_white.bolded = True
                    t_white.update(screen)
                else:
                    t_white = Button(t_white.image, (t_white.x_pos, t_white.y_pos), t_white.text_input, info_font,
                                     t_white.base_color, t_white.hovering_color)
                    t_white.bolded = False
                    t_white.update(screen)
            if t_green.isOver(pos, info_width, info_height):
                if t_green.bolded == False:
                    t_green = Button(t_green.image, (t_green.x_pos, t_green.y_pos), t_green.text_input, info_font_bold,
                                     t_green.base_color, t_green.hovering_color)
                    t_green.bolded = True
                    t_green.update(screen)
                else:
                    t_green = Button(t_green.image, (t_green.x_pos, t_green.y_pos), t_green.text_input, info_font,
                                     t_green.base_color, t_green.hovering_color)
                    t_green.bolded = False
                    t_green.update(screen)

                    # updating player card: weapons
            if t_candle.isOver(pos, info_width, info_height):
                if t_candle.bolded == False:
                    t_candle = Button(t_candle.image, (t_candle.x_pos, t_candle.y_pos), t_candle.text_input,
                                      info_font_bold, t_candle.base_color, t_candle.hovering_color)
                    t_candle.bolded = True
                    t_candle.update(screen)
                else:
                    t_candle = Button(t_candle.image, (t_candle.x_pos, t_candle.y_pos), t_candle.text_input, info_font,
                                      t_candle.base_color, t_candle.hovering_color)
                    t_candle.bolded = False
                    t_candle.update(screen)
            if t_dagger.isOver(pos, info_width, info_height):
                if t_dagger.bolded == False:
                    t_dagger = Button(t_dagger.image, (t_dagger.x_pos, t_dagger.y_pos), t_dagger.text_input,
                                      info_font_bold, t_dagger.base_color, t_dagger.hovering_color)
                    t_dagger.bolded = True
                    t_dagger.update(screen)
                else:
                    t_dagger = Button(t_dagger.image, (t_dagger.x_pos, t_dagger.y_pos), t_dagger.text_input, info_font,
                                      t_dagger.base_color, t_dagger.hovering_color)
                    t_dagger.bolded = False
                    t_dagger.update(screen)
            if t_pipe.isOver(pos, info_width, info_height):
                if t_pipe.bolded == False:
                    t_pipe = Button(t_pipe.image, (t_pipe.x_pos, t_pipe.y_pos), t_pipe.text_input, info_font_bold,
                                    t_pipe.base_color, t_pipe.hovering_color)
                    t_pipe.bolded = True
                    t_pipe.update(screen)
                else:
                    t_pipe = Button(t_pipe.image, (t_pipe.x_pos, t_pipe.y_pos), t_pipe.text_input, info_font,
                                    t_pipe.base_color, t_pipe.hovering_color)
                    t_pipe.bolded = False
                    t_pipe.update(screen)
            if t_rope.isOver(pos, info_width, info_height):
                if t_rope.bolded == False:
                    t_rope = Button(t_rope.image, (t_rope.x_pos, t_rope.y_pos), t_rope.text_input, info_font_bold,
                                    t_rope.base_color, t_rope.hovering_color)
                    t_rope.bolded = True
                    t_rope.update(screen)
                else:
                    t_rope = Button(t_rope.image, (t_rope.x_pos, t_rope.y_pos), t_rope.text_input, info_font,
                                    t_rope.base_color, t_rope.hovering_color)
                    t_rope.bolded = False
                    t_rope.update(screen)
            if t_wrench.isOver(pos, info_width, info_height):
                if t_wrench.bolded == False:
                    t_wrench = Button(t_wrench.image, (t_wrench.x_pos, t_wrench.y_pos), t_wrench.text_input,
                                      info_font_bold, t_wrench.base_color, t_wrench.hovering_color)
                    t_wrench.bolded = True
                    t_wrench.update(screen)
                else:
                    t_wrench = Button(t_wrench.image, (t_wrench.x_pos, t_wrench.y_pos), t_wrench.text_input, info_font,
                                      t_wrench.base_color, t_wrench.hovering_color)
                    t_wrench.bolded = False
                    t_wrench.update(screen)
            if t_revolver.isOver(pos, info_width, info_height):
                if t_revolver.bolded == False:
                    t_revolver = Button(t_revolver.image, (t_revolver.x_pos, t_revolver.y_pos), t_revolver.text_input,
                                        info_font_bold, t_revolver.base_color, t_revolver.hovering_color)
                    t_revolver.bolded = True
                    t_revolver.update(screen)
                else:
                    t_revolver = Button(t_revolver.image, (t_revolver.x_pos, t_revolver.y_pos), t_revolver.text_input,
                                        info_font, t_revolver.base_color, t_revolver.hovering_color)
                    t_revolver.bolded = False
                    t_revolver.update(screen)

            # updating player card: roomsToNames
            if t_study.isOver(pos, info_width, info_height):
                if t_study.bolded == False:
                    t_study = Button(t_study.image, (t_study.x_pos, t_study.y_pos), t_study.text_input, info_font_bold,
                                     t_study.base_color, t_study.hovering_color)
                    t_study.bolded = True
                    t_study.update(screen)
                else:
                    t_study = Button(t_study.image, (t_study.x_pos, t_study.y_pos), t_study.text_input, info_font,
                                     t_study.base_color, t_study.hovering_color)
                    t_study.bolded = False
                    t_study.update(screen)
            if t_hall.isOver(pos, info_width, info_height):
                if t_hall.bolded == False:
                    t_hall = Button(t_hall.image, (t_hall.x_pos, t_hall.y_pos), t_hall.text_input, info_font_bold,
                                    t_hall.base_color, t_hall.hovering_color)
                    t_hall.bolded = True
                    t_hall.update(screen)
                else:
                    t_hall = Button(t_hall.image, (t_hall.x_pos, t_hall.y_pos), t_hall.text_input, info_font,
                                    t_hall.base_color, t_hall.hovering_color)
                    t_hall.bolded = False
                    t_hall.update(screen)
            if t_lounge.isOver(pos, info_width, info_height):
                if t_lounge.bolded == False:
                    t_lounge = Button(t_lounge.image, (t_lounge.x_pos, t_lounge.y_pos), t_lounge.text_input,
                                      info_font_bold, t_lounge.base_color, t_lounge.hovering_color)
                    t_lounge.bolded = True
                    t_lounge.update(screen)
                else:
                    t_lounge = Button(t_lounge.image, (t_lounge.x_pos, t_lounge.y_pos), t_lounge.text_input, info_font,
                                      t_lounge.base_color, t_lounge.hovering_color)
                    t_lounge.bolded = False
                    t_lounge.update(screen)
            if t_library.isOver(pos, info_width, info_height):
                if t_library.bolded == False:
                    t_library = Button(t_library.image, (t_library.x_pos, t_library.y_pos), t_library.text_input,
                                       info_font_bold, t_library.base_color, t_library.hovering_color)
                    t_library.bolded = True
                    t_library.update(screen)
                else:
                    t_library = Button(t_library.image, (t_library.x_pos, t_library.y_pos), t_library.text_input,
                                       info_font, t_library.base_color, t_library.hovering_color)
                    t_library.bolded = False
                    t_library.update(screen)
            if t_billiard.isOver(pos, info_width, info_height):
                if t_billiard.bolded == False:
                    t_billiard = Button(t_billiard.image, (t_billiard.x_pos, t_billiard.y_pos), t_billiard.text_input,
                                        info_font_bold, t_billiard.base_color, t_billiard.hovering_color)
                    t_billiard.bolded = True
                    t_billiard.update(screen)
                else:
                    t_billiard = Button(t_billiard.image, (t_billiard.x_pos, t_billiard.y_pos), t_billiard.text_input,
                                        info_font, t_billiard.base_color, t_billiard.hovering_color)
                    t_billiard.bolded = False
                    t_billiard.update(screen)
            if t_dining.isOver(pos, info_width, info_height):
                if t_dining.bolded == False:
                    t_dining = Button(t_dining.image, (t_dining.x_pos, t_dining.y_pos), t_dining.text_input,
                                      info_font_bold, t_dining.base_color, t_dining.hovering_color)
                    t_dining.bolded = True
                    t_dining.update(screen)
                else:
                    t_dining = Button(t_dining.image, (t_dining.x_pos, t_dining.y_pos), t_dining.text_input, info_font,
                                      t_dining.base_color, t_dining.hovering_color)
                    t_dining.bolded = False
                    t_dining.update(screen)
            if t_conservatory.isOver(pos, info_width, info_height):
                if t_conservatory.bolded == False:
                    t_conservatory = Button(t_conservatory.image, (t_conservatory.x_pos, t_conservatory.y_pos),
                                            t_conservatory.text_input, info_font_bold, t_conservatory.base_color,
                                            t_conservatory.hovering_color)
                    t_conservatory.bolded = True
                    t_conservatory.update(screen)
                else:
                    t_conservatory = Button(t_conservatory.image, (t_conservatory.x_pos, t_conservatory.y_pos),
                                            t_conservatory.text_input, info_font, t_conservatory.base_color,
                                            t_conservatory.hovering_color)
                    t_conservatory.bolded = False
                    t_conservatory.update(screen)
            if t_ballroom.isOver(pos, info_width, info_height):
                if t_ballroom.bolded == False:
                    t_ballroom = Button(t_ballroom.image, (t_ballroom.x_pos, t_ballroom.y_pos), t_ballroom.text_input,
                                        info_font_bold, t_ballroom.base_color, t_ballroom.hovering_color)
                    t_ballroom.bolded = True
                    t_ballroom.update(screen)
                else:
                    t_ballroom = Button(t_ballroom.image, (t_ballroom.x_pos, t_ballroom.y_pos), t_ballroom.text_input,
                                        info_font, t_ballroom.base_color, t_ballroom.hovering_color)
                    t_ballroom.bolded = False
                    t_ballroom.update(screen)
            if t_kitchen.isOver(pos, info_width, info_height):
                if t_kitchen.bolded == False:
                    t_kitchen = Button(t_kitchen.image, (t_kitchen.x_pos, t_kitchen.y_pos), t_kitchen.text_input,
                                       info_font_bold, t_kitchen.base_color, t_kitchen.hovering_color)
                    t_kitchen.bolded = True
                    t_kitchen.update(screen)
                else:
                    t_kitchen = Button(t_kitchen.image, (t_kitchen.x_pos, t_kitchen.y_pos), t_kitchen.text_input,
                                       info_font, t_kitchen.base_color, t_kitchen.hovering_color)
                    t_kitchen.bolded = False
                    t_kitchen.update(screen)

            if gameStarted:
                if canClickButtons:
                    if b_move.isOver(pos, button_width_1, button_height):
                        if p.hasMoved == False:
                            moveOptions = movePlayer(p, currentPlayerLocations)
                            if moveOptions == "NO POSSIBLE OPTIONS":
                                moveInput1 = "Your move options are all blocked."
                                moveInput2 = "You can either accuse or end your turn."
                                blockedText1 = Text((1070, 525), moveInput1, action_font, action_font, (0, 0, 0),
                                                    notification_color)
                                blockedText2 = Text((1050, 540), moveInput2, action_font, action_font, (0, 0, 0),
                                                    notification_color)
                                blockedText1.update(screen)
                                blockedText2.update(screen)
                                msg = "KEEP SAME PLAYER TURN"
                                s.send(msg.encode(form))
                                p.canEndTurn = True
                                currentButtons = []
                            else:
                                buttonList = moveOptionButtons(moveOptions)
                                currentButtons = buttonList
                        else:
                            pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                            pygame.display.update()
                            noDoubleMove = "You can only move once per turn."
                            noDoubleMoveText = Text((1070, 525), noDoubleMove, action_font, action_font, (0, 0, 0),
                                                    notification_color)
                            noDoubleMoveText.update(screen)
                            currentButtons = []
                            msg = "KEEP SAME PLAYER TURN"
                            s.send(msg.encode(form))

                    if currentButtons != []:
                        for button in currentButtons:
                            theButton = Button(button.image, (button.x_pos, button.y_pos), button.text_input,button.font, button.base_color, button.hovering_color)
                            if theButton.isOver(pos, theButton.rect.width, theButton.rect.height):
                                clickedButton = theButton
                                buttonsClicked = True
                                if suggesting == True:
                                    if clickedButton.text_input in names:
                                        personSuggested = clickedButton.text_input
                                        currentButtons = []
                                        buttonsClicked = False
                                        pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                                        pygame.display.update()
                                        weaponButtons = printWeaponButtons("suggest")
                                        currentButtons = weaponButtons
                                    if clickedButton.text_input in weapons:
                                        weaponSuggested = clickedButton.text_input
                                        currentButtons = []
                                        buttonsClicked = False
                                        pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                                        pygame.display.update()
                                        roomSuggested = p.playerLocation
                                        all = "suggest !!!" + personSuggested + "," + roomSuggested + "," + weaponSuggested
                                        s.send(all.encode())
                                if accusing == True:
                                    suggesting = False
                                    if clickedButton.text_input in names:
                                        personAccused = clickedButton.text_input
                                        currentButtons = []
                                        buttonsClicked = False
                                        pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                                        pygame.display.update()
                                        weaponButtons = printWeaponButtons("accuse")
                                        currentButtons = weaponButtons
                                    if clickedButton.text_input in weapons:
                                        weaponAccused = clickedButton.text_input
                                        currentButtons = []
                                        buttonsClicked = False
                                        pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                                        pygame.display.update()
                                        roomButtons = printRoomButtons("accuse")
                                        currentButtons = roomButtons
                                    if clickedButton.text_input in rooms:
                                        roomAccused = clickedButton.text_input
                                        pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                                        pygame.display.update()
                                        allAccusations = "accuse !!!" + personAccused + "," + roomAccused + "," + weaponAccused
                                        s.send(allAccusations.encode())

                        if buttonsClicked == True:
                            if (p.hasMoved == False):
                                moveInput = allNamesToRooms.get(clickedButton.text_input)
                                if "room" not in moveInput:
                                    p.playerLocation = moveInput
                                    msg = "\nmove---" + p.playerName + "---" + p.playerLocation
                                    p.canEndTurn = True
                                    p.canSuggest = False

                                elif ("room" in moveInput):
                                    p.playerLocation = moveInput
                                    msg = "\nmove---" + p.playerName + "---" + p.playerLocation
                                    p.canEndTurn = False
                                    p.hasSuggested = False
                                    p.canSuggest = True

                                p.hasMoved = True
                                s.send(msg.encode(form))
                                currentButtons = []
                                pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                                pygame.display.update()

                    if b_suggest.isOver(pos, button_width_1, button_height):
                        suggestionValidation = validateSuggestion(p)
                        if (suggestionValidation == True):
                            suggesting = True
                            playerButtons = printPlayerButtons("suggest")
                            currentButtons = playerButtons
                        else:
                            pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                            pygame.display.update()
                            if p.hasSuggested:
                                noSuggesting = "You cannot make another suggestion."
                                noSuggestingText = Text((1070, 525), noSuggesting, action_font, action_font, (0, 0, 0),
                                                        notification_color)
                                noSuggestingText.update(screen)
                            elif p.canSuggest == False and p.hasMoved:
                                noSuggesting = "You are not in a location to suggest."
                                noSuggestingText = Text((1070, 525), noSuggesting, action_font, action_font, (0, 0, 0),
                                                        notification_color)
                                noSuggestingText.update(screen)
                            elif not p.hasMoved:
                                noSuggesting = "You must move before you can suggest."
                                noSuggestingText = Text((1060, 525), noSuggesting, action_font, action_font, (0, 0, 0),
                                                        notification_color)
                                noSuggestingText.update(screen)
                            else:
                                noSuggesting = "You must either move or make a suggestion."
                                noSuggestingText = Text((1070, 525), noSuggesting, action_font, action_font, (0, 0, 0),
                                                        notification_color)
                                noSuggestingText.update(screen)
                            msg = "KEEP SAME PLAYER TURN"
                            s.send(msg.encode(form))

                    if b_end.isOver(pos, button_width_2, button_height):
                        if (p.canEndTurn == True):
                            p.canSuggest = False
                            msg = "end \n"
                            s.send(msg.encode(form))
                            pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                            pygame.display.update()

                        else:
                            if (p.canSuggest and p.hasMoved):
                                pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                                pygame.display.update()
                                endMsg2 = "You must make a suggestion."
                                noEnd2 = Text((1070, 525), endMsg2, action_font, action_font, (0, 0, 0),notification_color)
                                noEnd2.update(screen)
                            elif (not p.canSuggest and not p.hasMoved):
                                pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                                pygame.display.update()
                                endMsg4 = "You must make a move to a new location."
                                noEnd4 = Text((1055, 525), endMsg4, action_font, action_font, (0, 0, 0),notification_color)
                                noEnd4.update(screen)
                            msg = "KEEP SAME PLAYER TURN"
                            s.send(msg.encode(form))

                    if b_accuse.isOver(pos, button_width_1, button_height):
                        accusing = True
                        playerButtons = printPlayerButtons("accuse")
                        currentButtons = playerButtons

                elif p.helpingSuggestion == True and gameStarted:
                    suggestionHelp = ""
                    for button in currentButtons:
                        if button.isOver(pos, button.rect.width, button.rect.height):
                            suggestionHelp = button.text_input
                    currentButtons = []
                    pygame.draw.rect(screen, WHITE, [1011, 512, 350, 187])
                    pygame.display.update()
                    s.send(suggestionHelp.encode(form))

    if first_beginning_screen is True:
        for button in start_button_list:
            button.changeColor(pygame.mouse.get_pos())
            button.update(screen)

    if second_beginning_screen is True:
        for button in start_char_button_list:
            button.changeColor(pygame.mouse.get_pos())
            button.update(screen)
    
    if currentButtons != []:
        for button in currentButtons:
            button.changeColor(pygame.mouse.get_pos())
            button.update(screen)