from operator import truediv
import pygame
import socket
from game import Game
from player import Player  
import ast
pygame.init()

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
## INSERT LOGIC TO read the current player
t_you = Text((t_x, t_y), "You are Player <so and so>", notification_font, info_font_bold, notification_color, notification_color)
t_you.update(screen)

# display current notification
t_y = t_y + notification_y_shift
t_Notification= Text((t_x, t_y), "THIS IS YOUR NOTIFICATION TEXT", notification_font, info_font_bold, notification_color, notification_color)
t_Notification.update(screen)
# NOTE logic to update the notification text will have to happenn in the loop


################################
# Start Updates Loop (no more STATIC udpates to board)
# this will be appropriately pasted into the game executino loop in client.py
#################################
# Initialize variables for loop
done = False
clock = pygame.time.Clock()
#Loop until the user closes the screen
while not done:
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user closes windo
            done = True  # Flag to exit the loop
        pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if b_move.isOver(pos, button_width_1, button_height):
                print('moving')
            if b_accuse.isOver(pos, button_width_1, button_height):
                print('accusing')
            if b_suggest.isOver(pos, button_width_1, button_height):
                print('suggesting')
            if b_show.isOver(pos, button_width_1, button_height):
                print('showing')
            if b_end.isOver(pos, button_width_2, button_height):
                print('ending')
        
        # code below would enable buttons changing color when hovered over
        # doesn't work now since buttons are an image, not a color
        #if event.type == pygame.MOUSEMOTION:
        #    if b_move.isOver(pos, button_width_1, button_height):
        #        b_move.color = button_greyed_color
        #    else:
        #        b_move.color = button_color
	
	################################ 
    # Update buttons, dropdowns, and text boxes
    ################################
    # Board (top left)
    pygame.draw.rect(screen, BLACK, [0, 0, vertical, hLeft], 2) #Draw a rectangle around the map
    
    ### INESRT logic to move user images around 
    #screen.blit(userImage, userLocation) ##populate on screen

   
	################################
    # Info Panel (top right)
    pygame.draw.rect(screen, GREEN, [vertical, 0, width, hRight], 2) #Information Panel

	###INSERT logic for users to interact with the text field and take notes ???
    
    ###############################
    # Notifications (bottom left)
    pygame.draw.rect(screen, RED, [0, hLeft, vertical, height], 2) #notification Panel
    
    ### INSERT textual updates for notifications
	#t_Notification.update(screen)

   
    ###############################
    # Actions (bottom right)
    pygame.draw.rect(screen, BLUE, [vertical, hRight, width, height], 2) #Action Panel
    
    ### INSERT LOGIC IF BUTTONS ARE CLICKED
    # Use checkForInput() to see if buttons have been clicked
    #b_move.checkForInput()
    #b_suggest.checkForInput()
    #b_accuse.checkForInput()
    #b_show.checkForInput()
    #b_end.checkForInput()

    ### INSERT DROPOWN MENUS HERE

   
    ################################
    #regular pygame updates here
    pygame.display.flip()
 
    # Limit the while loop to a max of 60 times per second, for CPS
    clock.tick(60)
 
pygame.quit() # Be IDLE friendly