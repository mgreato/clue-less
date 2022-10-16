# class: Player

class Player: 
    # Player initialization
    def __init__(self,number,name,location, cards):
        self.playerNumber = number
        self.playerName = name
        self.playerLocation = location
        self.locationIndex = number-1
        self.cards = cards
        
    # All other functionality
    #def move(self):

