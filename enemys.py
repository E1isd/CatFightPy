import pygame
from pygame.sprite import Sprite
from ability import Ability

class Enemy(Sprite):
    """Überklasse für die Gegner"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__()
        self.screen = ct_game.screen
        self.x_position = start_x
        self.y_position = start_y
        self.name = name
        self.action = True
        self.got_damage = 0
        self.is_alive = True
        self.abilities = Ability()
        self.status_effects = []

        self.stun_timer = 1


class Necromancer(Enemy):
    """Klasse für den Hauptboss"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.rect = pygame.Rect(self.x_position, self.y_position, 200,200)
        self.max_hp = 1500
        self.current_hp = 1500
        self.mp = 3000
        self.defence = 50
        self.attack = 200
        self.magic = 300
        self.magic_defence = 50
        self.frame_index = 0 # Variable, um den aktuellen Frame der Animation zu verfolgen

        self.available_skills = [self.abilities.simple_attack]
        
        """Laden der Sprites für die Animationen des Necromancers"""
        
        self.sprites = []
        sprite1 = pygame.image.load("images/Necromancer/Necromancer.png").convert_alpha() #standard Sprite, wenn der Charakter nicht ausgewählt ist
        sprite1 = pygame.transform.scale(sprite1, (300, 300))
        self.sprites.append(sprite1)
        
        sprite2 = pygame.image.load("images/Necromancer/Startup/Necromancer-Startup1.png").convert_alpha() # Laden der Startup-Sprites (die ersten 5 Bilder)
        sprite2 = pygame.transform.scale(sprite2, (300, 300))
        self.sprites.append(sprite2)
            
        sprite3 = pygame.image.load("images/Necromancer/Startup/Necromancer-Startup2.png").convert_alpha()  #convert_alpha() für bessere Performance + da transparente Pixel
        sprite3 = pygame.transform.scale(sprite3, (300, 300))
        self.sprites.append(sprite3)
            
        sprite4 = pygame.image.load("images/Necromancer/Startup/Necromancer-Startup3.png").convert_alpha()
        sprite4 = pygame.transform.scale(sprite4, (300, 300))
        self.sprites.append(sprite4)
            
        sprite5 = pygame.image.load("images/Necromancer/Startup/Necromancer-Startup4.png").convert_alpha()
        sprite5 = pygame.transform.scale(sprite5, (300, 300))
        self.sprites.append(sprite5)
            
        sprite6 = pygame.image.load("images/Necromancer/Startup/Necromancer-Startup5.png").convert_alpha()
        sprite6 = pygame.transform.scale(sprite6, (300, 300))
        self.sprites.append(sprite6)
        
        sprite7 = pygame.image.load("images/Necromancer/Idle/Necromancer-Idle1.png").convert_alpha() # Laden der Idle-Sprites (die letzten 4 Bilder)
        sprite7 = pygame.transform.scale(sprite7, (300, 300))
        self.sprites.append(sprite7)
        
        sprite8 = pygame.image.load("images/Necromancer/Idle/Necromancer-Idle2.png").convert_alpha()
        sprite8 = pygame.transform.scale(sprite8, (300, 300))
        self.sprites.append(sprite8)
        
        sprite9 = pygame.image.load("images/Necromancer/Idle/Necromancer-Idle3.png").convert_alpha()
        sprite9 = pygame.transform.scale(sprite9, (300, 300))
        self.sprites.append(sprite9)
        
        sprite10 = pygame.image.load("images/Necromancer/Idle/Necromancer-Idle4.png").convert_alpha()
        sprite10 = pygame.transform.scale(sprite10, (300, 300))
        self.sprites.append(sprite10)
        
        self.inactive_frames = [0, 1]
        self.startup_frames = [1, 2, 3, 4, 5]
        self.idle_frames = [6, 7, 8, 9]
        
        self.current_animation = self.inactive_frames # Startet mit der Inaktiv-Animation, wenn der Charakter nicht ausgewählt ist
        self.was_selected = False # Variable, um zu verfolgen, ob der Charakter jemals ausgewählt wurde (für die Startup-Animation)
        self.startup_finished = False # Variable, um zu verfolgen, ob die Startup-Animation abgeschlossen ist
        self.image = self.sprites[self.current_animation[self.frame_index]] # Aktuelles Sprite setzen
         
        # Timer für die Sprite-Animation (300ms)
        self.animation_timer = 0
        self.animation_delay = 300

    def update(self, is_selected=False):
        """Update-Methode mit zeitlich gesteuertem Sprite-Wechsel"""
        current_time = pygame.time.get_ticks() # Aktuelle Zeit in Millisekunden seit Pygame-Start
        if is_selected != self.was_selected: # Überprüfen, ob sich der Auswahlstatus geändert hat
            self.frame_index = 0 # Zurücksetzen des Frame-Index, wenn sich der Auswahlstatus ändert
            self.animation_timer = current_time # Timer zurücksetzen
            
            if is_selected:
                self.current_animation = self.startup_frames # Wechsel zur Startup-Animation, wenn der Charakter ausgewählt wird
                self.startup_finished = False # Startup-Animation ist noch nicht abgeschlossen
            else:
                self.current_animation = self.inactive_frames # Wechsel zur Inaktiv-Animation, wenn der Charakter nicht ausgewählt ist
            
            self.was_selected = is_selected # Aktualisieren des Auswahlstatus für die nächste Überprüfung
            
        if current_time - self.animation_timer >= self.animation_delay: # Überprüfen, ob genug Zeit für den nächsten Frame-Wechsel vergangen ist
            self.animation_timer = current_time # Timer zurücksetzen
            self.frame_index += 1 # Zum nächsten Frame wechseln
            
            if self.frame_index >= len(self.current_animation): # Wenn das Ende der aktuellen Animation erreicht ist
                if self.current_animation == self.startup_frames: # Wenn die Startup-Animation abgeschlossen ist
                    self.current_animation = self.idle_frames # Wechsel zur Idle-Animation
                self.frame_index = 0 # Zurücksetzen des Frame-Index, um die Animation zu wiederholen
                                
            # Aktuelles Sprite basierend auf der aktuellen Animation und dem Frame-Index setzen
            self.image = self.sprites[self.current_animation[self.frame_index]]
            
            print(is_selected) 
            # Debug-Ausgabe, um den Auswahlstatus zu überprüfen. 
            #Da konstant True, kann die Animation nicht wechseln, da die Startup-Animation immer wieder von vorne beginnt. 
            
# TODO: Mit einem Sprite Sheet könnte ich alle Animationen in einer einzigen Datei speichern und dann die entsprechenden Bereiche für die Animationen verwenden.
# Das würde den Code deutlich vereinfachen und die Performance verbessern.

class Poison_Minion(Enemy):
    """Klasse für Minion 1"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.max_hp = 500
        self.current_hp = 500
        self.mp = 500
        self.defence = 40
        self.attack = 100
        self.magic = 300
        self.magic_defence = 50
        self.available_skills = [self.abilities.simple_attack,self.abilities.poison_claw]

class Rage_Minion(Enemy):
    """Klasse für Minion 2"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.max_hp = 500
        self.current_hp = 500
        self.mp = 500
        self.defence = 40
        self.attack = 300
        self.magic = 100
        self.magic_defence = 50
        self.available_skills = [self.abilities.simple_attack, self.abilities.fury_claws]
