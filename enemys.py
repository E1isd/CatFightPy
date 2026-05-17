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


        self.stun_timer = 0
        self.burn_timer = 0

    # Für spezielle Kampfeffekte 
        self.revive_minions = False
        self.rage_modus = False


class Necromancer(Enemy):

    def __init__(self, ct_game, start_x, start_y, name):
        super().__init__(ct_game, start_x, start_y, name)

        self.rect = pygame.Rect(self.x_position, self.y_position, 200, 200)

        self.max_hp = 1500
        self.current_hp = 600
        self.mp = 3000
        self.defence = 50
        self.attack = 200
        self.magic = 300
        self.magic_defence = 50
        self.frame_index = 0 # Variable, um den aktuellen Frame der Animation zu verfolgen
        self.immune = ["stun"]

        self.available_skills = [self.abilities.simple_attack, self.abilities.necro_punch, self.abilities.hellfire]
        self.revive_minions = True
        self.revive_counter = 4

        self.rage_modus = True
        self.rage_skills = [self.abilities.necro_punch,self.abilities.hellfire,self.abilities.poisonous_storm]





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
        self.animation_direction = 1
        self.deselection_active = False

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
        
        #Gleiches Problem wie bei der Healer-Katze, wenn die Katze nicht mehr ausgewählt ist, 
        # dann bleibt sie im letzten Frame der Animation hängen, da die Animation nicht zurückgesetzt wird.
        #TODO: is_selected == False und frame_index != 0 -> frame_index = 0 und current_animation = default_sprite, damit die Katze zurück zum Standardbild wechselt, wenn sie nicht mehr ausgewählt ist. Muss ich aber nochmal überprüfen, da es sein könnte, das die Animation dann nicht mehr richtig abläuft, wenn die Katze wieder ausgewählt wird. Muss ich also nochmal testen.
        #Momentanes Prboelm: is_selected bleibt konstant True (Problem außerhalb von enemys.py, wahrscheinlich in cat_fight_main.py)

        
        if is_selected != self.was_selected:
            self.animation_timer = current_time

            if is_selected:
                # Start normal startup -> idle forward sequence
                self.current_animation = self.startup_frames
                self.frame_index = 0
                self.animation_direction = 1
                self.deselection_active = False
            else:
                # Begin deselection reverse sequence if currently in idle/startup
                if self.current_animation is self.idle_frames or self.current_animation is self.startup_frames:
                    self.animation_direction = -1
                    self.deselection_active = True
                    # reverse starts from current idle frame
                else:
                    # Not in an anim state -> just show default
                    self.current_animation = [self.default_sprite]
                    self.frame_index = 0
                    self.animation_direction = 1
                    self.deselection_active = False

                self.frame_index = min(self.frame_index, len(self.current_animation) - 1)

            self.image = self.current_animation[self.frame_index]
            self.was_selected = is_selected

        # Frame wechseln (mit fester Verzögerung zwischen Frames)
        if current_time - self.animation_timer >= self.animation_delay:
            # Timner wird zurückgesetzt, damit die Verzögerung zwischen Frames konstant bleibt
            self.animation_timer = current_time

            if self.animation_direction == 1: # Die Richtung der Animation (1 = vorwärts, -1 = rückwärts)
                # forward
                self.frame_index += 1 # Nächster Frame der Animation
                if self.frame_index >= len(self.current_animation):
                    
                    # Wenn das Startup zu Ende ist, wechsle zur Idle-Animation
                    if self.current_animation is self.startup_frames:
                        self.current_animation = self.idle_frames
                        self.frame_index = 0
                        self.animation_timer = current_time
                    else:
                        # Wenn die Idle-Animation zu Ende ist, bleibe im letzten Frame der Idle-Animation (statt zurück zum Anfang zu springen)
                        self.frame_index = len(self.current_animation) - 1

            else:
                # Rückwärts animation (für Deselection) 
                self.frame_index -= 1
                if self.frame_index < 0:
                    # Fertiger Rückwärtslauf der Startup-Animation -> Wechsel zum Default-Sprite
                    if self.deselection_active and self.current_animation is self.idle_frames:
                        self.current_animation = self.startup_frames
                        self.frame_index = len(self.startup_frames) - 1
                        self.animation_timer = current_time
                    # Fertiger Rückwärtslauf der Startup-Animation -> Wechsel zum Default-Sprite
                    elif self.deselection_active and self.current_animation is self.startup_frames:
                        self.current_animation = [self.default_sprite]
                        self.frame_index = 0
                        self.animation_direction = 1
                        self.deselection_active = False
                        self.animation_timer = current_time
                    else:
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
        self.current_hp = 10
        self.mp = 500
        self.defence = 40
        self.attack = 100
        self.magic = 300
        self.magic_defence = 50
        self.frame_index = 0 # Variable, um den aktuellen Frame der Animation zu verfolgen
        self.available_skills = [self.abilities.simple_attack,self.abilities.poison_claw]
        
        """
        Animation für den Poison Minion: 
        Startup-Animation, die abgespielt wird, wenn der Poison Minion zum ersten Mal ausgewählt wird. 
        Idle-Animation, die abgespielt wird, wenn der Poison Minion ausgewählt ist, aber keine Aktion ausführt. 
        Standard-Sprite, der angezeigt wird, wenn der Poison Minion nicht ausgewählt ist.
        """
        # Standard Sprite, wenn keine Animation aktiv ist
        self.default_sprite = pygame.image.load("images/Poison-Minion/Poison-Minion.png").convert_alpha()
        self.default_sprite = pygame.transform.scale(self.default_sprite,(150, 150))

        # Animationsframes laden 
        #Startup-Frames 
        self.startup_frames = self.load_sprite_sheet("images/Poison-Minion/Startup/Poison-Minion-startup-sheet.png",frame_width=48,frame_height=48,frame_count=3,scale=(150, 150))
        # Idle-Frames
        self.idle_frames = self.load_sprite_sheet("images/Poison-Minion/Idle/Poison-Minion-Idle2-Sheet.png",frame_width=48,frame_height=48,frame_count=3,scale=(150, 150))
        
        # Die aktuellen Frames der Animation
        self.current_animation = [self.default_sprite]

        self.was_selected = False
        self.startup_finished = False

        self.image = self.current_animation[self.frame_index]

        # Timer
        self.animation_timer = 0
        self.animation_delay = 300
        self.animation_direction = 1 # 1 = vorwärts, -1 = rückwärts um später eine Rückwärtsanimation zu ermöglichen, wenn der Necromancer nicht mehr ausgewählt ist

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
                self.animation_direction = 1
            else:
                self.current_animation = [self.default_sprite]
                self.animation_direction = 1
                
            self.image = self.current_animation[self.frame_index]
            self.was_selected = is_selected
            
        # Frame wechseln
        if current_time - self.animation_timer >= self.animation_delay:
            self.animation_timer = current_time
            self.frame_index += 1

            # Animation beendet?
            if self.frame_index >= len(self.current_animation):

                # Startup -> Idle
                if self.current_animation is self.startup_frames:
                    self.current_animation = self.idle_frames
                    self.animation_timer = current_time

                self.frame_index = 0

            self.image = self.current_animation[self.frame_index]


class Rage_Minion(Enemy):
    """Klasse für Minion 2"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.max_hp = 500
        self.current_hp = 10
        self.mp = 500
        self.defence = 40
        self.attack = 300
        self.magic = 100
        self.magic_defence = 50
        self.available_skills = [self.abilities.simple_attack, self.abilities.fury_claws]


#TODO: Animationen für die Minions hinzufügen, ähnlich wie beim Necromancer. Einfaches Idle- und Startup-Animationen sollten ausreichen, da die Minions keine eigenen Fähigkeiten haben, die eine spezielle Animation erfordern würden. Erledigt :)
        self.default_sprite = pygame.Surface((100, 100), pygame.SRCALPHA) # Transparenter Sprite als Platzhalter
        self.default_sprite.fill((160, 0, 160, 180))
        self.current_animation = [self.default_sprite]
        self.frame_index = 0
        self.image = self.current_animation[self.frame_index]
        self.animation_timer = 0
        self.animation_delay = 300
        self.animation_direction = 1
        self.was_selected = False
