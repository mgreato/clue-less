# class: Player
from game import Game
class Player: 

    # Player initialization
    def __init__(self,number,name,location, cards, hasMoved, hasSuggested, canEndTurn, canSuggest, helpingSuggestion):
        self.playerNumber = number
        self.playerName = name
        self.playerLocation = location
        self.cards = cards
        self.hasMoved = hasMoved
        self.hasSuggested = hasSuggested
        self.canEndTurn = canEndTurn
        self.canSuggest = canSuggest
        self.helpingSuggestion = helpingSuggestion


