import pygame
from pygame.sprite import Sprite

class Cat(Sprite):
    """Überklasse für die Spielercharaktere"""
    def __init__(self, ct_game, start_x, start_y, name):
        super().__init__()
        self.screen = ct_game.screen
        self.x_position = start_x
        self.y_position = start_y
        self.name = name # Name des Charakters
        self.action = True # Bool-Variable, ob der Charakter noch eine Funktion ausführen kann
        self.is_alive = True # Bool-Variable, ob der Charakter noch am Leben ist
        self.got_damage = 0

        self.status_effect = None

    def standard_attack(self, target): 
        """Funktion für den einfachen Angriff des Spielers"""
        target.got_damage = self.attack - target.defence # Ermittelt den Schaden
        if target.got_damage < 0: 
            target.got_damage = 0
        target.current_hp -= target.got_damage # Der Schaden wird von den aktuellen Lebenspunkten abgezogen
        self.action = False # Nach dem Angriff hat der Spieler keine Aktionen mehr
        print(f"{self.name} hit {target.name}. Damage: {target.got_damage}.  HP: {target.current_hp} / {target.max_hp} ")
        target.got_damage = 0

        
        
        

class Warrior(Cat):
    """Klasse für den Krieger"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.actions = ["Attack","Items","Skills"]
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.current_hp = 300
        self.max_hp = 300
        self.current_mp = 25
        self.max_mp = 25
        self.defence = 150
        self.attack = 200
        self.magic = 50

        self.abilitys = {
            "attack":{"power": self.attack}
        }
    


class Cleric(Cat):
    """Klasse für den Heiler"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.actions = ["Attack","Item","Prayer"]
        
        self.image = pygame.image.load("images/Cat-Healer-FINAL2.png")
        self.rect = self.image.get_rect()
        self.rect.x = self.x_position
        self.rect.y = self.y_position
        self.current_hp = 150
        self.max_hp = 150
        self.current_mp = 150
        self.max_mp = 150
        self.defence = 70
        self.attack = 70
        self.magic = 150

        self.abilitys = {
            "attack":{"power": self.attack}
        }

class Mage(Cat):
    """Klasse für den Zauberer"""
    def __init__(self,ct_game,start_x,start_y, name):
        super().__init__(ct_game,start_x,start_y, name)
        self.actions = ["Attack","Item","Magic"]
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.current_hp = 150
        self.max_hp = 150
        self.current_mp = 250
        self.max_mp = 250
        self.defence = 70
        self.attack = 50
        self.magic = 300

        self.abilitys = {
            "attack":{"power": self.attack}
        }