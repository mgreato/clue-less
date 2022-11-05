# class: Player
from game import Game
class Player: 

    # Player initialization
    def __init__(self,number,name,location, cards, hasMoved, hasSuggested, canEndTurn):
    # , hasMoved, hasSuggested):
        self.playerNumber = number
        self.playerName = name
        self.playerLocation = location
        # self.locationIndex = number-1
        self.cards = cards
        self.hasMoved = hasMoved
        self.hasSuggested = hasSuggested
        self.canEndTurn = canEndTurn
        # Game.chosenPlayers.append(name)
        
    # All other functionality
    #def move(self):

