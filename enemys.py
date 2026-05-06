from sys import path
import pygame
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
        self.immune = [] 

        self.stun_timer = 1


class Necromancer(Enemy):

    def __init__(self, ct_game, start_x, start_y, name):
        super().__init__(ct_game, start_x, start_y, name)

        self.rect = pygame.Rect(self.x_position, self.y_position, 200, 200)

        self.max_hp = 1500
        self.current_hp = 1500
        self.mp = 3000
        self.defence = 50
        self.attack = 200
        self.magic = 300
        self.magic_defence = 50
        self.frame_index = 0 # Variable, um den aktuellen Frame der Animation zu verfolgen
        self.immune = ["stun"]

        self.available_skills = [self.abilities.simple_attack]
        """
        Animation für den Necromancer: 
        Startup-Animation, die abgespielt wird, wenn der Necromancer zum ersten Mal ausgewählt wird. 
        Idle-Animation, die abgespielt wird, wenn der Necromancer ausgewählt ist, aber keine Aktion ausführt. 
        Standard-Sprite, der angezeigt wird, wenn der Necromancer nicht ausgewählt ist.
        """
        # Standard Sprite, wenn keine Animation aktiv ist
        self.default_sprite = pygame.image.load("images/Necromancer/Necromancer.png").convert_alpha()
        self.default_sprite = pygame.transform.scale(self.default_sprite,(300, 300))

        # Animationsframes laden 
        #Startup-Frames 
        self.startup_frames = self.load_sprite_sheet("images/Necromancer/Startup/Necromancer-Startup-sheet.png",frame_width=96,frame_height=96,frame_count=5,scale=(300, 300))
        # Idle-Frames
        self.idle_frames = self.load_sprite_sheet("images/Necromancer/Idle/Necromancer-Idle-sheet.png",frame_width=96,frame_height=96,frame_count=4,scale=(300, 300))
        
        # Die aktuellen Frames der Animation
        self.current_animation = [self.default_sprite]

        self.was_selected = False
        self.startup_finished = False

        self.image = self.current_animation[self.frame_index]

        # Timer
        self.animation_timer = 0
        self.animation_delay = 300

    # Sprite Sheet laden und in einzelne Frames aufteilen
    def load_sprite_sheet(self,path,frame_width,frame_height,frame_count,scale=None):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []

        for i in range(frame_count):
            rect = pygame.Rect(i * frame_width,0,frame_width,frame_height)

            frame = sheet.subsurface(rect).copy()

            if scale:
                frame = pygame.transform.scale(frame, scale)
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
                self.current_animation = self.startup_frames

            else:
                self.current_animation = [self.default_sprite]

            self.was_selected = is_selected
            
        # Frame wechseln
        if current_time - self.animation_timer >= self.animation_delay:
            self.animation_timer = current_time
            self.frame_index += 1

            # Animation beendet?
            if self.frame_index >= len(self.current_animation):

                # Startup -> Idle
                if self.current_animation == self.startup_frames:

                    self.current_animation = self.idle_frames

                self.frame_index = 0

            self.image = self.current_animation[self.frame_index]
            
# TODO: Mit einem Sprite Sheet könnte ich alle Animationen in einer einzigen Datei speichern und dann die entsprechenden Bereiche für die Animationen verwenden.
# Das würde den Code deutlich vereinfachen und die Performance verbessern. Erledigt :)

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
