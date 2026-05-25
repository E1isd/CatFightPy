import pygame
import os
from ability import Ability
from pygame.sprite import Sprite
import random

# Gemeinsame lokale Hurt-Image-Laderoutine für Cats
def _load_hurt_image(display_name, target_size=None, scale=None, hurt_dir=None):
    if hurt_dir is None:
        hurt_dir = os.path.join("images", "Character", "Hurt") # Standardverzeichnis für Hurt-Images, kann aber durch Argument überschrieben werden

    candidates = [f"hurt_{display_name}.png",f"hurt_{display_name.replace(' ', '-')}.png",f"hurt_{display_name.replace(' ', '_')}.png",f"hurt_{display_name.lower()}.png"]

    try:
        parts = [p.lower() for p in display_name.replace('-', ' ').replace('_', ' ').split()] # Teile des Namens in Kleinbuchstaben, um mehr Treffer zu ermöglichen (z.B. Warrior -> warrior)
        for fn in os.listdir(hurt_dir): # Alle Dateien im Hurt-Verzeichnis durchgehen und prüfen, ob sie zum Charakter passen könnten
            lower = fn.lower() 
            if any(part in lower for part in parts):
                candidates.append(fn) # Alle Dateien, die einen Teil des Namens enthalten, als Kandidaten hinzufügen
    except Exception: 
        pass

    seen = set()
    for fn in candidates: # Alle Kandidaten durchgehen und das erste passende Bild laden
        if fn in seen: # Verhindert doppelte Versuche bei mehrfachen Kandidaten
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
                    except Exception: # Falls scale_by nicht verfügbar ist, manuelle Skalierung durchführen
                        w, h = img.get_size()
                        return pygame.transform.scale(img, (int(w * scale), int(h * scale)))
                return img
        except Exception: # Fehler beim Laden der Datei ignorieren und zum nächsten Kandidaten gehen
            continue
    return None

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
        self.damage_negation = False

        # Timer für Statuseffekte
        self.stun_timer = 0
        self.burn_timer = 0
        self.protect_timer = 0
        # Hurt-Image (wird angezeigt, wenn der Charakter Schaden > 0 erleidet)
        self.hurt_image = None
        self.hurt_timer = None
        self.hurt_duration = 300  # ms
        self.hurt_scale = 3
        self.hurt_target_size = None

    def load_hurt_image(self, target_size=None):
        """Lazy-load das Hurt-Image beim ersten Schaden."""
        size = target_size or self.hurt_target_size
        self.hurt_image = _load_hurt_image(self.name, target_size=size, scale=None if size else self.hurt_scale)
        return self.hurt_image

class Warrior(Cat):
    """Klasse für den Krieger"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.actions = ["Attack","Items","Skills"]
        
        # Das aktuelle Bild der Katze
        self.image = pygame.transform.scale_by(pygame.image.load("images/Character/Warrior/Warrior.png").convert_alpha(), 3)
        # Der Wert für das Standardbild der Katze, wenn keine Kampf- oder Idleanimation festgesetzt ist.
        self.image_default = pygame.transform.scale_by(pygame.image.load("images/Character/Warrior/Warrior.png").convert_alpha(), 3)
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.current_hp = 800
        self.max_hp = 800
        self.current_mp = 25
        self.max_mp = 25
        self.defence = 150
        self.attack = 200
        self.magic = 50
        self.magic_defence = 50
        self.learned_abilities=[self.abilities.berserker_claw, self.abilities.knock_out, self.abilities.hammer_of_justice] # Die bisher gelernten Fähigkeiten der Klasse
        self.frame_index = 0

# Standard Sprite, wenn keine Animation aktiv ist
        self.default_sprite = pygame.transform.scale_by(pygame.image.load("images/Character/Warrior/Warrior.png").convert_alpha(),3)

        # Animationsframes laden 
        #Idle-Frames
        self.idle_frames = self.load_sprite_sheet("images/Character/Warrior/Warrior-idle-sheet.png",frame_width=48,frame_height=48,frame_count=4,scale=3)
        
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
        # Hurt-Image anzeigen falls aktiv
        if getattr(self, "hurt_timer", None):
            if current_time - self.hurt_timer < getattr(self, "hurt_duration", 300):
                if getattr(self, "hurt_image", None) is not None:
                    self.image = self.hurt_image
                return
            else:
                self.hurt_timer = None
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
            if len(self.current_animation) == 0:
                self.current_animation = [self.default_sprite]

            if is_selected:
                if self.frame_index >= len(self.current_animation):
                    self.frame_index = len(self.current_animation) - 2 if len(self.current_animation) > 1 else 0
            else:
                if self.frame_index >= len(self.current_animation): # Wenn das Ende der Animation erreicht ist, zurück zum Anfang
                    self.frame_index = 0

            self.image = self.current_animation[self.frame_index]

class Cleric(Cat):
    """Klasse für den Heiler"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.actions = ["Attack","Item","Prayer"]
        
        # Das aktuelle Bild der Katze
        self.image = pygame.transform.scale_by(pygame.image.load("images/Character/Cleric/Cleric.png").convert_alpha(), 3)
        # Der Wert für das Standardbild der Katze, wenn keine Kampf- oder Idleanimation festgesetzt ist.
        self.image_default = pygame.transform.scale_by(pygame.image.load("images/Character/Cleric/Cleric.png").convert_alpha(), 3)
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
        self.magic_defence = 50

        self.frame_index = 0
        
        self.learned_abilities=[self.abilities.prayer_of_lesser_healing,self.abilities.prayer_of_ressurection, self.abilities.prayer_of_healing_wind]

# Standard Sprite, wenn keine Animation aktiv ist
        self.default_sprite = pygame.transform.scale_by(pygame.image.load("images/Character/Cleric/Cleric.png").convert_alpha(),3)

        # Animationsframes laden 
        #Idle-Frames
        self.idle_frames = self.load_sprite_sheet("images/Character/Cleric/Cleric-idle-sheet.png",frame_width=48,frame_height=48,frame_count=6,scale=3)
        
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
        # Hurt-Image anzeigen falls aktiv
        if getattr(self, "hurt_timer", None):
            if current_time - self.hurt_timer < getattr(self, "hurt_duration", 300):
                if getattr(self, "hurt_image", None) is not None:
                    self.image = self.hurt_image
                return
            else:
                self.hurt_timer = None
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
            
            if self.frame_index == 3:
                if not random.randint(1, 5) == 1: # 20% Chance, dass die Animation das umdrehen zeigt, ansonsten zurück zum Anfang
                    self.frame_index = 0
            if self.frame_index >= len(self.current_animation): # Wenn das Ende der Animation erreicht ist, zurück zum Anfang
                self.frame_index = 0
            self.image = self.current_animation[self.frame_index]
            #Gleiches Problem wie bei der Necroamncer Katze, wenn die Katze nicht mehr ausgewählt ist, 
            # dann bleibt sie im letzten Frame der Animation hängen, da die Animation nicht zurückgesetzt wird (siehe Update-Methode der Necromancer-Klasse in enemys.py).
            #TODO: is_selected == False und frame_index != 0 -> frame_index = 0 und current_animation = default_sprite, damit die Katze zurück zum Standardbild wechselt, wenn sie nicht mehr ausgewählt ist. Muss ich aber nochmal überprüfen, da es sein könnte, das die Animation dann nicht mehr richtig abläuft, wenn die Katze wieder ausgewählt wird. Muss ich also nochmal testen.
            #Momentanes Prboelm: is_selected bleibt konstant True (Problem außerhalb von enemys.py, wahrscheinlich in cat_fight_main.py)

            # Ich denke, ich habe das Problem gelöst: Katze bleibt jetzt nicht mehr im letzten Frame hängen, allerdings ist das Problem nur für die 
            # healer-cat gelöst. Wenn jede Katze und Gegner eine Grafik hat, können wir das algemein als Code formulieren.
            # Das Problem mit dem Cursor konnte ich auch lösen, wir müssen die Cursor nur noch skalieren.

        

class Mage(Cat):
    """Klasse für den Zauberer"""
    def __init__(self,ct_game,start_x,start_y, name):
        super().__init__(ct_game,start_x,start_y, name)
        self.actions = ["Attack","Item","Magic"]
        
          # Das aktuelle Bild der Katze
        self.image = pygame.transform.scale_by(pygame.image.load("images/Character/Mage/Mage.png").convert_alpha(), 3)
        # Der Wert für das Standardbild der Katze, wenn keine Kampf- oder Idleanimation festgesetzt ist.
        self.image_default = pygame.transform.scale_by(pygame.image.load("images/Character/Mage/Mage.png").convert_alpha(), 3)
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.current_hp = 500
        self.max_hp = 500
        self.current_mp = 250
        self.max_mp = 250
        self.defence = 70
        self.attack = 50
        self.magic = 200
        self.magic_defence = 50
        self.learned_abilities=[self.abilities.fireball, self.abilities.whirlwind, self.abilities.protect]
        self.frame_index = 0
        
# Standard Sprite, wenn keine Animation aktiv ist
        self.default_sprite = pygame.transform.scale_by(pygame.image.load("images/Character/Mage/Mage.png").convert_alpha(),3)

        # Animationsframes laden 
        #Idle-Frames
        self.idle_frames = self.load_sprite_sheet("images/Character/Mage/Mage-idle-sheet.png",frame_width=48,frame_height=48,frame_count=5,scale=3)
        
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
        # Hurt-Image anzeigen falls aktiv
        if getattr(self, "hurt_timer", None):
            if current_time - self.hurt_timer < getattr(self, "hurt_duration", 300):
                if getattr(self, "hurt_image", None) is not None:
                    self.image = self.hurt_image
                return
            else:
                self.hurt_timer = None
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
            if len(self.current_animation) == 0:
                self.current_animation = [self.default_sprite]

            if is_selected:
                if self.frame_index >= len(self.current_animation):
                    self.frame_index = len(self.current_animation) - 2 if len(self.current_animation) > 1 else 0
            else:
                if self.frame_index >= len(self.current_animation): # Wenn das Ende der Animation erreicht ist, zurück zum Anfang
                    self.frame_index = 0

            self.image = self.current_animation[self.frame_index]
