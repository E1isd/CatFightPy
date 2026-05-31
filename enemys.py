import os
import pygame
from pygame.sprite import Sprite
from ability import Ability

# Gemeinsame lokale Hurt-Image-Laderoutine für Enemys
def _load_hurt_image(display_name, target_size=None, scale=None, hurt_dir=None):
    if hurt_dir is None:
        hurt_dir = os.path.join("images", "Character", "Hurt")

    candidates = [f"hurt_{display_name}.png",f"hurt_{display_name.replace(' ', '-')}.png",f"hurt_{display_name.replace(' ', '_')}.png",f"hurt_{display_name.lower()}.png"]

    try:
        parts = [p.lower() for p in display_name.replace('-', ' ').replace('_', ' ').split()]
        for fn in os.listdir(hurt_dir):
            lower = fn.lower()
            if any(part in lower for part in parts):
                candidates.append(fn)
    except Exception:
        pass

    seen = set()
    for fn in candidates:
        if fn in seen:
            continue
        seen.add(fn)
        path = os.path.join(hurt_dir, fn)
        try:
            if os.path.isfile(path):
                img = pygame.image.load(path).convert_alpha()
                if target_size:
                    return pygame.transform.scale(img, target_size)
                if scale:
                    try:
                        return pygame.transform.scale_by(img, scale)
                    except Exception:
                        w, h = img.get_size()
                        return pygame.transform.scale(img, (int(w * scale), int(h * scale)))
                return img
        except Exception:
            continue
    return None

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
        # Hurt-Image wird beim ersten Schaden geladen.
        self.hurt_image = None
        self.hurt_timer = None
        self.hurt_duration = 300
        self.hurt_target_size = None
        # Für spezielle Kampfeffekte (Initialwerte)
        self.revive_minions = False
        self.rage_modus = False
        self.minion_protection = False
        self.damage_negation = False
        

    def load_hurt_image(self, target_size=None):
        """Lazy-load das Hurt-Image beim ersten Schaden."""
        target_size = target_size or self.hurt_target_size
        try:
            self.hurt_image = _load_hurt_image(self.name, target_size=target_size)
        except Exception:
            self.hurt_image = None
        return self.hurt_image
        

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

        self.available_skills = [self.abilities.simple_attack, self.abilities.necro_punch, self.abilities.hellfire]
        self.revive_minions = True
        self.revive_counter = 4

        self.rage_modus = True
        self.rage_skills = [self.abilities.necro_punch,self.abilities.hellfire,self.abilities.poisonous_storm]

        self.minion_protection = True
        self.damage_negation = True
        





        """
        Animation für den Necromancer: 
        Startup-Animation, die abgespielt wird, wenn der Necromancer zum ersten Mal ausgewählt wird. 
        Idle-Animation, die abgespielt wird, wenn der Necromancer ausgewählt ist, aber keine Aktion ausführt. 
        Standard-Sprite, der angezeigt wird, wenn der Necromancer nicht ausgewählt ist.
        """
        # Standard Sprite, wenn keine Animation aktiv ist
        self.default_sprite = pygame.image.load("images/Character/Necromancer/Necromancer.png").convert_alpha()
        self.default_sprite = pygame.transform.scale(self.default_sprite,(300, 300))
        self.hurt_target_size = self.default_sprite.get_size()

        # Animationsframes laden 
        #Startup-Frames 
        self.startup_frames = self.load_sprite_sheet("images/Character/Necromancer/Startup/Necromancer-Startup-sheet.png",frame_width=96,frame_height=96,frame_count=5,scale=(300, 300))
        # Idle-Frames
        self.idle_frames = self.load_sprite_sheet("images/Character/Necromancer/Idle/Necromancer-Idle-sheet.png",frame_width=96,frame_height=96,frame_count=4,scale=(300, 300))
        
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
        # Wenn das Hurt-Image aktiv ist, wird es für die Dauer des Hurt-Timers angezeigt und die normale Animation wird übersprungen.
        if getattr(self, 'hurt_timer', None):
            if current_time - self.hurt_timer < getattr(self, 'hurt_duration', 300):
                if getattr(self, 'hurt_image', None) is not None:
                    self.image = self.hurt_image
                return
            else:
                self.hurt_timer = None
        # Auswahlstatus geändert
        
        #Gleiches Problem wie bei der Healer-Katze, wenn die Katze nicht mehr ausgewählt ist, 
        # dann bleibt sie im letzten Frame der Animation hängen, da die Animation nicht zurückgesetzt wird.
        #TODO: is_selected == False und frame_index != 0 -> frame_index = 0 und current_animation = default_sprite, damit die Katze zurück zum Standardbild wechselt, wenn sie nicht mehr ausgewählt ist. Muss ich aber nochmal überprüfen, da es sein könnte, das die Animation dann nicht mehr richtig abläuft, wenn die Katze wieder ausgewählt wird. Muss ich also nochmal testen.
        #Momentanes Prboelm: is_selected bleibt konstant True (Problem außerhalb von enemys.py, wahrscheinlich in cat_fight_main.py)

        
        if is_selected != self.was_selected:
            self.animation_timer = current_time

            if is_selected:
                # Startet normale Auswahlsequenz -> Startup-Animation -> Idle-Animation
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
                #Vorwärtsanimation (für Auswahl)
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
        self.current_hp = 500
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
        self.default_sprite = pygame.image.load("images/Character/Poison-Minion/Poison-Minion.png").convert_alpha()
        self.default_sprite = pygame.transform.scale(self.default_sprite,(150, 150))
        self.hurt_target_size = self.default_sprite.get_size()

        # Animationsframes laden 
        #Startup-Frames 
        self.startup_frames = self.load_sprite_sheet("images/Character/Poison-Minion/Startup/Poison-Minion-startup-sheet.png",frame_width=48,frame_height=48,frame_count=3,scale=(150, 150))
        # Idle-Frames
        self.idle_frames = self.load_sprite_sheet("images/Character/Poison-Minion/Idle/Poison-Minion-Idle2-Sheet.png",frame_width=48,frame_height=48,frame_count=3,scale=(150, 150))
        
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
        # Wenn das Hurt-Image aktiv ist, wird es für die Dauer des Hurt-Timers angezeigt und die normale Animation wird übersprungen.
        if getattr(self, 'hurt_timer', None):
            if current_time - self.hurt_timer < getattr(self, 'hurt_duration', 300):
                if getattr(self, 'hurt_image', None) is not None:
                    self.image = self.hurt_image
                return
            else:
                self.hurt_timer = None
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
        self.current_hp = 500
        self.mp = 500
        self.defence = 40
        self.attack = 300
        self.magic = 100
        self.magic_defence = 50
        self.frame_index = 0 # Variable, um den aktuellen Frame der Animation zu verfolgen
        self.available_skills = [self.abilities.simple_attack, self.abilities.fury_claws]


#TODO: Animationen für die Minions hinzufügen, ähnlich wie beim Necromancer. Einfaches Idle- und Startup-Animationen sollten ausreichen, da die Minions keine eigenen Fähigkeiten haben, die eine spezielle Animation erfordern würden. Erledigt :)
        """
        Animation für den Rage Minion: 
        Startup-Animation, die abgespielt wird, wenn der Rage Minion zum ersten Mal ausgewählt wird. 
        Idle-Animation, die abgespielt wird, wenn der Rage Minion ausgewählt ist, aber keine Aktion ausführt. 
        Standard-Sprite, der angezeigt wird, wenn der Rage Minion nicht ausgewählt ist.
        """
        # Standard Sprite, wenn keine Animation aktiv ist
        self.default_sprite = pygame.image.load("images/Character/Rage-Minion/Rage-Minion.png").convert_alpha()
        self.default_sprite = pygame.transform.scale(self.default_sprite,(150, 150))
        self.hurt_target_size = self.default_sprite.get_size()

        # Animationsframes laden 
        #Startup-Frames 
        self.startup_frames = self.load_sprite_sheet("images/Character/Rage-Minion/Startup/Rage-Minion-startup-sheet.png",frame_width=48,frame_height=48,frame_count=3,scale=(150, 150))
        # Idle-Frames
        self.idle_frames = self.load_sprite_sheet("images/Character/Rage-Minion/Idle/Rage-Minion-Idle2-Sheet.png",frame_width=48,frame_height=48,frame_count=3,scale=(150, 150))
        
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
        # If hurt image is active, show it for the duration and skip normal animation
        if getattr(self, 'hurt_timer', None):
            if current_time - self.hurt_timer < getattr(self, 'hurt_duration', 300):
                if getattr(self, 'hurt_image', None) is not None:
                    self.image = self.hurt_image
                return
            else:
                self.hurt_timer = None
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
