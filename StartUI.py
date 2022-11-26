import pygame, sys
from button import *

pygame.init()

SCREEN = pygame.display.set_mode((1100, 1100))
pygame.display.set_caption("Menu")

StartBG = pygame.image.load("StartBG.png")


def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("font.ttf", size)


def play():
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")

        PLAY_TEXT = get_font(45).render("This is the PLAY screen.", True, "White")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        PLAY_BACK = Button(image=None, pos=(640, 460),
                           text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")

        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

        pygame.display.update()


def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(640, 460),
                              text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()


def menu_buttons(option):

    if option == "numPlayer":
        num_3 = Button(image=None, pos=(200, 250),
                       text_input="3 Players", font=get_font(15), base_color="#d7fcd4", hovering_color="White")
        num_4 = Button(image=None, pos=(400, 250),
                       text_input="4 Players", font=get_font(15), base_color="#d7fcd4", hovering_color="White")
        num_5 = Button(image=None, pos=(600, 250),
                       text_input="5 Players", font=get_font(15), base_color="#d7fcd4", hovering_color="White")
        num_6 = Button(image=None, pos=(800, 250),
                       text_input="6 Players", font=get_font(15), base_color="#d7fcd4", hovering_color="White")

        # PLAY_BUTTON = Button(image=None, pos=(640, 250),
        #                      text_input="PLAY", font=get_font(35), base_color="#d7fcd4", hovering_color="White")
        # OPTIONS_BUTTON = Button(button_surface, pos=(640, 400),
        #                         text_input="OPTIONS", font=get_font(35), base_color="#d7fcd4", hovering_color="White")
        # QUIT_BUTTON = Button(button_surface, pos=(640, 550),
        #                      text_input="QUIT", font=get_font(35), base_color="#d7fcd4", hovering_color="White")

        btn_list = [num_3, num_4, num_5, num_6]
    if option == "character":
        names = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
        scarlett = Button(image=None, pos=(200, 250),
                          text_input="Miss Scarlett", font=get_font(15), base_color="#d7fcd4", hovering_color="White")
        mustard = Button(image=None, pos=(400, 250),
                       text_input="Colonel Mustard", font=get_font(15), base_color="#d7fcd4", hovering_color="White")
        white = Button(image=None, pos=(600, 250),
                       text_input="Mrs. White", font=get_font(15), base_color="#d7fcd4", hovering_color="White")
        green = Button(image=None, pos=(800, 250),
                       text_input="Reverend Green", font=get_font(15), base_color="#d7fcd4", hovering_color="White")
        peacock = Button(image=None, pos=(600, 250),
                       text_input="Mrs. Peacock", font=get_font(15), base_color="#d7fcd4", hovering_color="White")
        plum = Button(image=None, pos=(800, 250),
                       text_input="Professor Plum", font=get_font(15), base_color="#d7fcd4", hovering_color="White")

        btn_list = [scarlett, mustard, white, green, peacock, plum]

    return btn_list

def main_menu_setup():

    SCREEN.blit(StartBG, (0, 0))

    MENU_MOUSE_POS = pygame.mouse.get_pos()

    MENU_TEXT = get_font(40).render("Welcome To Clue-Less Game", True, "#b68f40")
    MENU_RECT = MENU_TEXT.get_rect(center=(550, 100))

    NUM_TEXT = get_font(25).render("Please choose the number of players", True, "#b68f40")
    NUM_RECT = NUM_TEXT.get_rect(center=(550, 200))

    SCREEN.blit(MENU_TEXT, MENU_RECT)
    SCREEN.blit(NUM_TEXT, NUM_RECT)



def main_menu():
    button_surface = pygame.image.load("button.png")
    button_surface = pygame.transform.scale(button_surface, (200, 50))

    main_menu_setup()

    while True:
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        #quit button
        quit_btn = Button(image=button_surface, pos=(650, 700),
                          text_input="Quit", font=get_font(15), base_color="#d7fcd4", hovering_color="White")
        quit_btn.changeColor(MENU_MOUSE_POS)
        quit_btn.update(SCREEN)

        #options to choose number of players
        numPlayer_btn = menu_buttons("numPlayer")
        for button in numPlayer_btn:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        #options to choose characters
        # character_btn = menu_buttons("character")
        # for button in character_btn:
        #     #if button.text in message
        #     button.changeColor(MENU_MOUSE_POS)
        #     button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if numPlayer_btn[0].checkForInput(MENU_MOUSE_POS):
                    number_of_players = 3
                if numPlayer_btn[1].checkForInput(MENU_MOUSE_POS):
                    number_of_players = 4
                if numPlayer_btn[2].checkForInput(MENU_MOUSE_POS):
                    number_of_players = 5
                if numPlayer_btn[3].checkForInput(MENU_MOUSE_POS):
                    number_of_players = 6

                #get available character from server

                if numPlayer_btn[3].checkForInput(MENU_MOUSE_POS):
                    pass
                if quit_btn.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()



