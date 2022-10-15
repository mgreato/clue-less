# class: Player

class Player: 
    # Player initialization
    def __init__(self,number,name,location):
        self.playerNumber = number
        self.playerName = name
        self.playerLocation = location
        self.locationIndex = number-1
        
    # All other functionality
    #def move(self):

