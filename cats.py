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
        self.status_effects = [] # Liste aller im Kampf erhaltenen Statuseffekte
        self.immune = [] # Variable für die Immunität von Statuseffekten
        self.abilities = Ability() # Instanz des Ability-Dictonarys

        # Timer für Statuseffekte
        self.stun_timer = 0
        self.burn_timer = 0
        self.protect_timer = 0


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
        self.learned_abilities=[self.abilities.berserker_claw, self.abilities.knock_out, self.abilities.hammer_of_justice] # Die bisher gelernten Fähigkeiten der Klasse

class Cleric(Cat):
    """Klasse für den Heiler"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.actions = ["Attack","Item","Prayer"]
        
        # Das aktuelle Bild der Katze
        self.image = pygame.transform.scale_by(pygame.image.load("images/Cat-Healer/cat-healer-default.png").convert_alpha(), 3)
        # Der Wert für das Standardbild der Katze, wenn keine Kampf- oder Idleanimation festgesetzt ist.
        self.image_default = pygame.transform.scale_by(pygame.image.load("images/Cat-Healer/cat-healer-default.png").convert_alpha(), 3)
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

        self.frame_index = 0
        
        self.learned_abilities=[self.abilities.prayer_of_lesser_healing,self.abilities.prayer_of_ressurection, self.abilities.prayer_of_healing_wind]

# Standard Sprite, wenn keine Animation aktiv ist
        self.default_sprite = pygame.transform.scale_by(pygame.image.load("images/Cat-Healer/cat-healer-default.png").convert_alpha(),3)

        # Animationsframes laden 
        #Idle-Frames
        self.idle_frames = self.load_sprite_sheet("images/Cat-Healer/cat-healer-idle-sheet.png",frame_width=48,frame_height=48,frame_count=6,scale=3)
        
        # Die aktuellen Frames der Animation
        self.current_animation = [self.default_sprite]

        self.was_selected = False

        self.image = self.current_animation[self.frame_index]

        # Timer
        self.animation_timer = 0
        self.animation_delay = 250

            # Sprite Sheet laden und in einzelne Frames aufteilen
    def load_sprite_sheet(self,path,frame_width,frame_height,frame_count,scale=None):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []

        for i in range(frame_count):
            rect = pygame.Rect(i * frame_width,0,frame_width,frame_height)

            frame = sheet.subsurface(rect).copy()

            if scale:
                frame = pygame.transform.scale_by(frame, scale)
            frames.append(frame)
        return frames

    # Update-Methode mit zeitlich gesteuertem Sprite-Wechsel
    def update(self, is_selected=False):
        current_time = pygame.time.get_ticks()
        # Auswahlstatus geändert
        if is_selected != self.was_selected:

            self.frame_index = 0
            self.animation_timer = current_time
            
            if is_selected:
                self.current_animation = self.idle_frames

            else:
                self.current_animation = [self.default_sprite]

            self.was_selected = is_selected
            
        # Frame wechseln
        if current_time - self.animation_timer >= self.animation_delay:
            self.animation_timer = current_time
            self.frame_index += 1

            # Animation beendet?
            if self.frame_index >= len(self.current_animation):

                self.frame_index = 0
            self.image = self.current_animation[self.frame_index]


        

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

        self.learned_abilities=[self.abilities.fireball, self.abilities.whirlwind, self.abilities.protect]




