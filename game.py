# class: Game


class Game: 

    chosenPlayers = []
    playerNames = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]

    playerStartLocations = {"Miss Scarlett": "None", "Colonel Mustard": "None", "Mrs. White": "None", "Reverend Green": "None",
        "Mrs. Peacock": "None", "Professor Plum": "None"}
    
    playerStartLocations1 = {"Miss Scarlett": "hallway23", "Colonel Mustard": "hallway34", "Mrs. White": "hallway56", "Reverend Green": "hallway67",
        "Mrs. Peacock": "hallway78", "Professor Plum": "hallway81"}

    playerLocations = {"Miss Scarlett": "None", "Colonel Mustard": "None", "Mrs. White": "None", "Reverend Green": "None",
        "Mrs. Peacock": "None", "Professor Plum": "None"}

    # Game initialization
    def __init__(self,numPlayers):
        self.numPlayers = 0



