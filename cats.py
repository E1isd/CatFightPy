import pygame
from ability import Ability
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
        self.got_damage = 0 # Variable für den Schaden, den ein Charakter erlitten hat
        self.got_heal = 0 # Variable für die Heilung, die ein Charakter erhalten hat
        self.status_effect = None # Bool-Variable, die überprüft, ob die Katze einen Statuseffekt hat
        self.abilities = Ability()



class Warrior(Cat):
    """Klasse für den Krieger"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.actions = ["Attack","Items","Skills"]
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.current_hp = 800
        self.max_hp = 800
        self.current_mp = 25
        self.max_mp = 25
        self.defence = 150
        self.attack = 200
        self.magic = 50
        self.learned_abilities=[self.abilities.berserker_claw] # Die bisher gelernten Fähigkeiten der Klasse

class Cleric(Cat):
    """Klasse für den Heiler"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.actions = ["Attack","Item","Prayer"]
        
        self.image = pygame.transform.scale(pygame.image.load("images/Cat-Healer/Cat-Healer new1.png").convert_alpha(), (150,150))
        self.rect = self.image.get_rect()
        self.rect.x = self.x_position
        self.rect.y = self.y_position
        self.current_hp = 500
        self.max_hp = 500
        self.current_mp = 150
        self.max_mp = 150
        self.defence = 70
        self.attack = 70
        self.magic = 150

        self.learned_abilities=[self.abilities.prayer_of_lesser_healing,self.abilities.prayer_of_ressurection]

        #Idle Animation, wenn der Charakter ausgewählt ist, aber keine Aktion ausführt
        self.sprites = []
        sprite1 = pygame.image.load("images/Cat-Healer/Cat-Healer new1.png").convert_alpha()
        sprite1 = pygame.transform.scale(sprite1, (150, 150))
        self.sprites.append(sprite1)
        
        sprite2 = pygame.image.load("images/Cat-Healer/Cat-Healer new1.png").convert_alpha()
        sprite2 = pygame.transform.scale(sprite2, (150, 150))
        self.sprites.append(sprite2)
        
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        
        # Timer für die Sprite-Animation (200ms)
        self.animation_timer = 0
        self.animation_delay = 200  # 200ms Zeitabstand

    def update(self, is_selected=False):
        """Update-Methode mit zeitlich gesteuertem Sprite-Wechsel"""
        if is_selected:
            # Nur wenn der Charakter ausgewählt ist, wird die Animation abgespielt
            current_time = pygame.time.get_ticks()
            if current_time - self.animation_timer >= self.animation_delay:
                self.animation_timer = current_time
                self.current_sprite += 1
                if self.current_sprite >= len(self.sprites): # Wenn das Ende der Sprite-Liste erreicht ist, wieder von vorne beginnen
                    self.current_sprite = 0
                self.image = self.sprites[self.current_sprite]
        

class Mage(Cat):
    """Klasse für den Zauberer"""
    def __init__(self,ct_game,start_x,start_y, name):
        super().__init__(ct_game,start_x,start_y, name)
        self.actions = ["Attack","Item","Magic"]
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.current_hp = 500
        self.max_hp = 500
        self.current_mp = 250
        self.max_mp = 250
        self.defence = 70
        self.attack = 50
        self.magic = 200

        self.learned_abilities=[self.abilities.fireball, self.abilities.whirlwind]




