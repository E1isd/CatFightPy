import os
import ctypes
import sys
import random
from random import choice

# ==============================================================================
# MODULE-LEVEL COMMENTS
# ==============================================================================
# Entfernung eines erzwungenen Dummy-Audiotreibers, falls er extern gesetzt wurde.
# Verhindert, dass SDL einen stillen Dummy-Treiber verwendet, wenn ein echtes Audiosystem verfügbar ist.

if os.getenv("SDL_AUDIODRIVER", "").lower() == "dummy":
    del os.environ["SDL_AUDIODRIVER"]
    
import pygame
from cats import *  # noqa: F403
from enemys import *
from boxes import *
from cursor import Cursor
from action_sequence import Action


# ==============================================================================
# CLASS: Cat_Fight
# ==============================================================================
# Die Hauptklasse des Spiels. Verantwortlich für die Initialisierung, die Hauptschleife,
# das Rendering, die Eingabeereignisse, die Verwaltung der Runden und die Kampfmechanik.
# ==============================================================================

class Cat_Fight:

    def __init__(self):
        # ----------------------------------------------------------------------
        # DISPLAY SETUP
        # Diese Zeile hindert Windows daran, eine Skalierung auf das Spiel anzuwenden.
        # Ohne diese Zeile könnten die Grafiken unscharf oder falsch skaliert erscheinen, 
        # und die Positionierung könnte sich verschieben,
        # ----------------------------------------------------------------------
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except AttributeError:
            pass 

        # Pre-initialisiert den Pygame-Mixer mit einer kleineren Buffergröße (512 statt 1024 &2048),
        # welche wichtig ist, um Sounds mit Animationen zu synchronisieren.
        pygame.mixer.pre_init(44100, -16, 2, 512)
        # Initialisiert alle Pygame-Module. Muss nach der Mixer-Pre-Init erfolgen, damit die angepasste Buffergröße wirksam wird.
        pygame.init()

        # Das Icon für das Spiel.
        icon = pygame.image.load("images/Icon/Icon.ico")
        pygame.display.set_icon(icon)
        
        # ----------------------------------------------------------------------
        # AUDIO SETUP
        # Wenn die Audiodatei nicht geladen werden kann, wird eine Warnung ausgegeben
        # und das Spiel startet ohne Ton, anstatt zu crashen.
        # ----------------------------------------------------------------------
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            music_path = os.path.join("audio", "background", "Opening.mp3")
            if not os.path.isfile(music_path):
                raise FileNotFoundError(f"Music file not found: {music_path}")
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(0.5)
        except Exception as e:
            print("Warning: Audio could not be started. Game will run without sound.")
            print("Audio error:", e)
            
        self.arcade_click_sound = None
        try:
            self.arcade_click_sound = pygame.mixer.Sound("audio/sound_effects/arcade-click.mp3")
        except Exception:
            self.arcade_click_sound = None

        # ----------------------------------------------------------------------
        # SCREEN SETUP
        # Erster Versuch, den Vollbildmodus zu aktivieren, 
        # damit das Spiel auf verschiedenen Bildschirmgrößen korrekt aussieht. 
        # Falls dies fehlschlägt (z.B. auf einem System, das keinen Vollbildmodus unterstützt), 
        # wird stattdessen ein reguläres Fenster mit der gleichen Auflösung geöffnet.
        # ----------------------------------------------------------------------
        try:
            self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        except pygame.error:
            print("Warning: Fullscreen not available. Starting in windowed mode instead.")
            self.screen = pygame.display.set_mode((1920, 1080))

        self.screen_rect = self.screen.get_rect()
        self.bg_color = (200, 205, 220)  # Hintergrundfarbe in RGB.
        self.background = pygame.transform.scale(
            pygame.image.load("images/Start/start_background.png").convert_alpha(), (1920, 1080)
        )
        self.start_background = self.background  # Bleibt unverändert für den Startbildschirm
        
        # Die Clock-Instanz wird verwendet, um die Zeit zwischen den Frames zu messen und die Bildrate zu steuern.
        self.clock = pygame.time.Clock()

        # ----------------------------------------------------------------------
        # HERO CATS
        # ----------------------------------------------------------------------
        self.warrior_cat = Warrior(self, 1100, 350, "Warrior")
        self.healer_cat   = Cleric (self, 1150, 460, "Cleric")
        self.casting_cat  = Mage   (self, 1200, 590, "Mage")

        # ----------------------------------------------------------------------
        # ENEMIES
        # ----------------------------------------------------------------------
        self.boss     = Necromancer (self, 350, 350, "Evil Necromancer Cat")
        self.minion_1 = Poison_Minion(self, 650, 370, "Cat Minion 1")
        self.minion_2 = Rage_Minion  (self, 650, 570, "Cat Minion 2")

        # Akutelle Inventarinstanz, die im gesamten Spiel verwendet wird. 
        self.current_inventory = Inventory(self)

        # ----------------------------------------------------------------------
        # GROUPS & TURN ORDER
        # Heldenkatzen sind gemischt, damit die Zugreihenfolge in jedem Durchlauf unterschiedlich ist.
        # Nach dem Mischen wird die Liste auf ihre ursprüngliche Reihenfolge zurückgesetzt,
        # was für die korrekte Cursor-Auswahl später erforderlich ist.
        # ----------------------------------------------------------------------
        self.cat_heroes = [self.warrior_cat, self.healer_cat, self.casting_cat]
        random.shuffle(self.cat_heroes)  # Mischt die Reihenfolge der Heldenkatzen 
        self.enemies = [self.minion_1, self.minion_2, self.boss]
        self.fighting_order = [
            self.cat_heroes[0], self.minion_1,
            self.cat_heroes[1], self.minion_2,
            self.cat_heroes[2], self.boss
        ]
        #Reset auf feste Reihenfolge nach dem Mischen — erforderlich für die korrekte Cursor-Logik.
        self.cat_heroes = [self.warrior_cat, self.healer_cat, self.casting_cat]
        self.dead_enemies = []
        self.target_group = [] # Momentan ausgewählte Zielgruppe, wird genutzt für die Cursor-Erstellung und Fähigkeitensequenzen.

        # ----------------------------------------------------------------------
        # UI BOXES / BUTTONS
        # ----------------------------------------------------------------------
        self.cat_box     = Cat_Box(self, self.warrior_cat, self.healer_cat, self.casting_cat)   # Heldenkatzenamen, HP & MP
        self.action_box  = Action_Box(self, self.cat_box)                                       # Action menü (Angriff, Items, etc.)
        self.enemy_box   = Enemy_Box(self, self.boss, self.minion_1, self.minion_2, self.action_box)  # Gegnernamen
        self.item_box    = Item_Box(self, self.action_box)                                      # Verfügbare Gegenstände anzeigen
        self.ability_box = Ability_Box(self, self.action_box)                                   # Verfügbare Fähigkeiten anzeigen
        self.tooltip_box = Tooltip_Box(self)                                                    # Beschreibt Fähigkeiten und Feindangriffe
        self.help_box    = Help_Box(self, self.cat_box.rect)                                    # Steuerungshilfe Overlay
        self.start_box   = Start_Box(self)                                                      # Startbildschirm mit Spieltitel und Startanweisungen                                   
        self.end_box     = End_Box(self)                                                        # Endbildschirm mit Sieg- oder Niederlage-Nachricht und Anweisungen zum Beenden des Spiels
        self.tooltip_message = ""                                                               # Text momentan sichtbar in der Tooltip-Box.

        # ----------------------------------------------------------------------
        # TURN SYSTEM
        # ----------------------------------------------------------------------
        self.turn_timer     = 0                                      # Zählt / indiziert die aktuelle Position in der Zugreihenfolge.
        self.current_player = self.fighting_order[self.turn_timer]   # Beginnt mit dem ersten Teilnehmer in der Zugreihenfolge.
        self.next_turn      = False                                   # Wird auf True gesetzt, wenn die Bedingungen für einen neuen Zug erfüllt sind.

        self.current_target = 0     # Index des aktuell ausgewählten Ziels.
        self.enemy_target   = None  # Das spezifische Feindziel, das in diesem Zug gewählt wurde.
        self.enemy_action   = None  # Die Aktion, die der aktuelle Feind gewählt hat.

        # ----------------------------------------------------------------------
        # CURSORS
        # player_cursor  — Marker wird über dem aktiven Kämpfer angezeigt.
        # single_cursor  — Auswahlcursor für ein einzelnes Ziel.
        # all_cursor     — Auswahlcursor für eine ganze Gruppe.
        # ----------------------------------------------------------------------
        self.player_cursor = Cursor(self, self.current_player.rect.centerx - 10, self.current_player.rect.y - 30)
        self.single_cursor = Cursor(self, 0, 0)
        self.all_cursor    = Cursor(self, 0, 0)

        # ----------------------------------------------------------------------
        # BATTLE SEQUENCER & ACTION STATE
        # ----------------------------------------------------------------------
        self.battle_sequencer = Action(self)  # Behandelt die vollständige Kampfsequenz: Angriffe, Schaden, Animationen.
        self.current_action   = None          # Speichert die aktuell ausgeführte Kampfaktion.

        # ----------------------------------------------------------------------
        # STATUS EFFECTS
        # ----------------------------------------------------------------------
        self.show_status  = False  # True, während ein Statuseffekt angezeigt wird.
        self.status_i     = None   # Iteriert über die aktiven Statuseffekte.
        self.status_done  = False  # True, sobald alle Statuseffekte für diesen Zug verarbeitet wurden.

        self.fight_active = False
        self.fight_won = False
        self.game_over = False


    # ==========================================================================
    # MAIN GAME LOOP
    # ==========================================================================

    def run_game(self):
        """Hauptfunktion — läuft bis die While-Schleife beendet wird."""
        while True:
            if self.fight_active == False:
                self._check_events()
                self._update_screen()   # Zeichnet den Bildschirm mit allen aktualisierten Werten und Positionen neu.
                self.clock.tick(60)     # Aktualisiert die Uhr und stellt die Bildrate ein.
            elif self.fight_active == True:
                self._check_events()        # Überprüft Spieler-Eingaben in diesem Frame.
                self._check_start_turn()    # Überprüft, ob gerade ein neuer Zug begonnen hat.
                self.check_status_effect()  # Behandelt eventuelle aktive Statuseffekte.
                self.check_enemy_turn()
                self._check_for_action()    # Überprüft, ob eine Aktion gerade ausgeführt wird.
                self._check_if_alive()      # Überprüft, ob alle Kämpfer noch am Leben sind.
                self.check_for_fight_end()
                self._check_next_turn()     # Überprüft, ob die Bedingungen für einen neuen Zug erfüllt sind.
                self._update_screen()
                self.clock.tick(60)

    # ==========================================================================
    # RENDERING
    # ==========================================================================

    def _update_screen(self):
        """Zeichnet den Bildschirm mit allen Spielelementen neu."""
        if self.fight_active == False and not self.game_over and not self.fight_won:
            self.screen.blit(self.background, (0, 0))
            self.start_box.draw_start_box()
            pygame.display.flip()
        elif self.fight_active == False and (self.game_over or self.fight_won):
            self.screen.blit(self.background, (0, 0))
            self.end_box.draw_end_box(self.game_over)
            self._draw_game_fields()  # Zeichnet die UI-Panels.
            self._draw_charakters()   # Zeichnet die Charaktere.
            pygame.display.flip()
        elif self.fight_active == True:
            self.screen.blit(self.background, (0, 0))
            self._draw_game_fields()  # Zeichnet die UI-Panels.
            self._draw_charakters()   # Zeichnet die Charaktere.
            self._draw_cursor()       # Zeichnet die Cursor.
            self._draw_effects()      # Zeichnet alle aktiven Effekte.
            pygame.display.flip()     # Aktualisiert die Anzeige, um den neuen Frame anzuzeigen.

    def _draw_charakters(self):
        """Zeichnet alle Charaktere (Helden und Feinde)."""
        if self.warrior_cat.is_alive:
            self.screen.blit(self.warrior_cat.image, (self.warrior_cat.x_position, self.warrior_cat.y_position))
        if self.casting_cat.is_alive:
            self.screen.blit(self.casting_cat.image, (self.casting_cat.x_position, self.casting_cat.y_position))

        if self.minion_1.is_alive:
            self.screen.blit(self.minion_1.image, (self.minion_1.x_position, self.minion_1.y_position))
        if self.minion_2.is_alive:
            minion2_image = getattr(self.minion_2, "image", None)
            if minion2_image is not None:
                self.screen.blit(minion2_image, (self.minion_2.x_position, self.minion_2.y_position))
            else:
                pygame.draw.rect(self.screen, "purple", self.minion_2.rect)
        if self.boss.is_alive:
            self.screen.blit(self.boss.image, (self.boss.x_position, self.boss.y_position))

        # Die Heiler-Katze wird nur in ihrer Standard-/Ruhepause gezeichnet, wenn keine Aktionsanimation läuft.
        # (Muss generalisiert werden, sobald alle Charaktergrafiken vorhanden sind.)
        if not self.battle_sequencer.cat_animation_active:
            self.screen.blit(self.healer_cat.image, (self.healer_cat.x_position, self.healer_cat.y_position))

    def _draw_game_fields(self):
        """Zeichnet die UI-Panels des Kampfbildschirms."""
        self.cat_box.draw_cat_box(self.current_player)      # Panel mit Katzennamen, HP & MP.
        self.enemy_box.draw_enemy_box()                      # Panel mit Gegnernamen.

        # Das Action-Fenster wird nur gezeichnet, wenn der aktuelle Kämpfer vom Spieler gesteuert wird.
        if self.current_player in self.cat_heroes:
            self.action_box.draw_action_box(self.current_player)

        if self.item_box.active:
            self.item_box.draw_item_box(self.current_inventory, self.single_cursor.active)
        if self.ability_box.active:
            self.ability_box.draw_ability_box(self.current_player, self.single_cursor.active, self.all_cursor.active)

        # Liest die Tooltip-Nachricht (falls vorhanden) und zeichnet das Tooltip-Fenster (falls aktiv).
        self.get_tooltip()
        self.tooltip_box.draw_tooltip_box(self.tooltip_message)
        self.help_box.draw_help_box()

    def get_tooltip(self):
        """Liest die Nachricht zum Anzeigen in der Tooltip-Box."""
        if self.item_box.active:
            # Die Tooltip-Nachricht wird aus dem Inventarwörterbuch gelesen.
            self.tooltip_message = self.item_box.current_items[self.item_box.current_position]["tooltip"]
        elif self.ability_box.active:
            # Die Tooltip-Nachricht wird aus dem Fähigkeitswörterbuch gelesen.
            self.tooltip_message = self.current_player.learned_abilities[self.ability_box.current_position]["tooltip"]
        elif self.show_status:
            # Während ein Statuseffekt verarbeitet wird, wird eine entsprechende Nachricht angezeigt.
            self.tooltip_message = self.battle_sequencer.message
        else:
            # Kein Element mit einem Tooltip ist ausgewählt — Nachricht löschen.
            self.tooltip_message = ""

    def _draw_cursor(self):
        """Zeichnet die Cursor und Marker auf dem Schlachtfeld."""
        # Spieler-Runden-Marker: über dem aktiven Kämpfer zentriert positioniert.
        self.player_cursor.rect.x = (
            self.current_player.rect.centerx
            - (self.player_cursor.cursor_frame_width // 2 - 20)
        )
        self.player_cursor.rect.y = (
            self.current_player.rect.y
            - self.player_cursor.cursor_frame_height - 8  # 8-Pixel-Lücke über dem Charakter.
        )
        self.player_cursor.draw_animated_cursor(
            self.player_cursor.current_player_sheet,
            self.player_cursor.rect.x,
            self.player_cursor.rect.y,
            self.player_cursor.cursor_sprites_short
        )

        # Der Single-Target-Auswahlcursor wird nur gezeichnet, wenn er aktiv ist.
        if self.single_cursor.active:
            if self.target_group == self.enemies:
                # Koordinaten, wenn das Ziel zur Feindgruppe gehört.
                offset_x = 30 # Offset wird für die Minions angepasst, damit der Cursor nicht zu weit rechts erscheint.
                if "Minion" in self.enemies[self.current_target].name:
                    offset_x = 40 
                self.single_cursor.rect.x = self.enemies[self.current_target].rect.right + offset_x
                self.single_cursor.rect.y = (
                    self.enemies[self.current_target].rect.centery
                    - (self.single_cursor.cursor_frame_height // 2) + 30
                )
                self.single_cursor.draw_animated_cursor(
                    self.single_cursor.attack_sheet,
                    self.single_cursor.rect.x,
                    self.single_cursor.rect.y,
                    self.single_cursor.attack_sprites
                )
            elif self.target_group == self.cat_heroes:
                # Koordinaten, wenn das Ziel zur Heldengruppe gehört.
                self.single_cursor.rect.x = (
                    self.cat_heroes[self.current_target].rect.left
                    - self.single_cursor.cursor_frame_width - 4
                )
                self.single_cursor.rect.y = (
                    self.cat_heroes[self.current_target].rect.centery
                    - (self.single_cursor.cursor_frame_height // 2) + 30
                )
                self.single_cursor.draw_animated_cursor(
                    self.single_cursor.heal_sheet,
                    self.single_cursor.rect.x,
                    self.single_cursor.rect.y,
                    self.single_cursor.heal_sprites
                )

        # Der Mehrfach-Zielcursor wird über jedem Mitglied der ausgewählten Gruppe gezeichnet.
        if self.all_cursor.active:
            if self.target_group == self.enemies:
                for enemy in self.enemies:
                    offset_x = 4 # Standard-Offset für Feinde
                    if "Minion" in enemy.name:
                        offset_x = 14 # Angepasster Offset für Minions (+10)
                    self.all_cursor.rect.x = enemy.rect.right + offset_x
                    self.all_cursor.rect.y = enemy.rect.centery - (self.all_cursor.cursor_frame_height // 2 - 50) + 30
                    self.all_cursor.draw_animated_cursor(
                        self.all_cursor.attack_sheet,
                        self.all_cursor.rect.x,
                        self.all_cursor.rect.y,
                        self.all_cursor.attack_sprites
                    )
            elif self.target_group == self.cat_heroes:
                for cat in self.cat_heroes:
                    self.all_cursor.rect.x = cat.rect.left - self.all_cursor.cursor_frame_width - 4 
                    self.all_cursor.rect.y = cat.rect.centery - (self.all_cursor.cursor_frame_height // 2) + 30
                    self.all_cursor.draw_animated_cursor(
                        self.all_cursor.heal_sheet,
                        self.all_cursor.rect.x,
                        self.all_cursor.rect.y,
                        self.all_cursor.heal_sprites
                    )

    def _draw_effects(self):
        """Zeichnet alle aktiven Effekte, wenn ihre Bedingungen erfüllt sind."""
        # Sprite-Animationen für alle Charaktere (Helden und Feinde).
        if not self.battle_sequencer.cat_animation_active:
            for enemy in self.enemies:
                enemy.update(is_selected=(enemy is self.current_player))
            for cat in self.cat_heroes:
                cat.update(is_selected=(cat is self.current_player))

        if not self.show_status:
            self.battle_sequencer.draw_damage_numbers()  # Schadensszahlen nach einem Angriff zeichnen.
        else:
            self.battle_sequencer.draw_damage_numbers(self.battle_sequencer.font_color)  # Statuseffekt-Schadensszahlen zeichnen.

        self.battle_sequencer.draw_cat_action_animation(self.current_player)  # Zeichne die Katzen-Kampfanimation (falls aktiv).
        self.battle_sequencer.draw_simple_effect()                             # Zeichne Kampfeffekte (falls aktiv).

    # ==========================================================================
    # INPUT HANDLING
    # ==========================================================================

    def _check_events(self):
        """Überprüft Spieler-Eingabeereignisse in jedem Frame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)
            if event.type == pygame.MOUSEMOTION:        # NEU: Maus-Bewegung
                self.check_mouse_motion(event)
            if event.type == pygame.MOUSEBUTTONDOWN:    # NEU: Mausklick
                self.check_mouse_click(event)

    def check_mouse_motion(self, event):
        """Bewegt den Menücursor, wenn die Maus über ein Menüelement oder einen Charakter schwebt."""
        if self.current_action or self.show_status or not self.fight_active:
            return
        mx, my = event.pos

        if self.action_box.active:
            for i, pos in enumerate(self.action_box.postitions):
                if pos.collidepoint(mx, my):
                    self.action_box.current_position = i

        elif self.item_box.active and not self.single_cursor.active:
            for i, pos in enumerate(self.item_box.postitions):
                if pos.collidepoint(mx, my):
                    self.item_box.current_position = i

        elif self.ability_box.active and not (self.single_cursor.active or self.all_cursor.active):
            for i, pos in enumerate(self.ability_box.postitions):
                if pos.collidepoint(mx, my):
                    self.ability_box.current_position = i

        elif self.single_cursor.active and self.target_group:
            # Das Überfahren mit der Maus über einem Charaktersprite wählt ihn als Ziel aus.
            for i, entity in enumerate(self.target_group):
                if entity.rect.collidepoint(mx, my):
                    self.current_target = i

    def check_mouse_click(self, event):
        """
        Überprüft Mausklicks.
        Linksklick  — bestätigt die aktuelle Auswahl (wie Enter).
        Rechtsklick — bricht ab / geht zurück (wie Escape).
        """
        if event.button == 1:   # Linksklick = Bestätigung
            fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode='\r')
            self.check_keydown_events(fake_event)
        elif event.button == 3: # Rechtsklick = Abbruch
            fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode='')
            self.check_keydown_events(fake_event)

    def check_keydown_events(self, event):
        """Überprüft einzelne Tastendruckereignisse."""
        # Q — Spiel beenden.
        if event.key == pygame.K_q:
            sys.exit()

        # LEERTASTE — überspringt den aktuellen Zug (temporäre Debug-Verknüpfung). // INAKTIV //
        """if event.key == pygame.K_SPACE:
            if not self.current_action and not self.show_status and self.fight_active:
                self.current_player.action = False
                if self.single_cursor.active or self.all_cursor.active:
                    self._create_or_delete_cursor(None)
                self.ability_box.active = False
                self.item_box.active = False""" 

        # Die folgenden Eingaben werden nur verarbeitet, wenn keine Aktionssequenz läuft.

        # PFEIL UNTEN — bewegt den Cursor / die Auswahl nach unten.
        if event.key == pygame.K_DOWN and not self.current_action and not self.show_status and self.fight_active:
            if self.action_box.active:
                if self.action_box.current_position < len(self.action_box.postitions) - 1:
                    self.action_box.current_position += 1
            elif self.item_box.active and not self.single_cursor.active:
                if self.item_box.current_position < len(self.item_box.postitions) - 1:
                    self.item_box.current_position += 1
            elif self.ability_box.active and not (self.single_cursor.active or self.all_cursor.active):
                if self.ability_box.current_position < len(self.ability_box.postitions) - 1:
                    self.ability_box.current_position += 1
            # Bewegt den Single-Target-Cursor nach unten; wird am Anfang zurückgesetzt, wenn das Ende erreicht ist.
            elif self.single_cursor.active:
                self.current_target += 1
                if self.current_target > len(self.target_group) - 1:
                    self.current_target = 0

        # PFEIL OBEN — bewegt den Cursor / die Auswahl nach oben.
        if event.key == pygame.K_UP and not self.current_action and not self.show_status and self.fight_active:
            if self.action_box.active:
                if self.action_box.current_position > 0:
                    self.action_box.current_position -= 1
            elif self.item_box.active and not self.single_cursor.active:
                if self.item_box.current_position > 0:
                    self.item_box.current_position -= 1
            elif self.ability_box.active and not (self.single_cursor.active or self.all_cursor.active):
                if self.ability_box.current_position > 0:
                    self.ability_box.current_position -= 1
            # Bewegt den Single-Target-Cursor nach oben; wird am Ende zurückgesetzt, wenn der Anfang überschritten wird.
            elif self.single_cursor.active:
                self.current_target -= 1
                if self.current_target < 0:
                    self.current_target = len(self.target_group) - 1

        # ENTER — bestätigt / führt Aktionen aus.
        if event.key == pygame.K_RETURN and not self.current_action and not self.show_status:
            if self.current_player in self.cat_heroes and self.action_box.active and self.fight_active:
                if self.action_box.current_position == 0:
                    # Position 0 (Angriff): aktiviert den auf Feinde gerichteten Zielcursor.
                    self._create_or_delete_cursor(self.enemies)
                    self.action_box.active = False
                if self.action_box.current_position == 1:
                    # Position 1 (Gegenstände): öffnet das Gegenstände-Fenster.
                    self.item_box.active    = True
                    self.tooltip_box.active = True
                    self.action_box.active  = False
                if self.action_box.current_position == 2:
                    # Position 2 (Fähigkeiten): öffnet das Fähigkeiten-Fenster.
                    self.ability_box.active = True
                    self.tooltip_box.active = True
                    self.action_box.active  = False

            elif self.item_box.active and not self.single_cursor.active and self.fight_active:
                # Gegenstände-Fenster ist offen — aktiviert den auf Katzen gerichteten Zielcursor (nur Heilgegenstände vorerst).
                self._create_or_delete_cursor(self.cat_heroes)

            elif self.ability_box.active and not self.single_cursor.active and not self.all_cursor.active and self.fight_active:
                # Eine Fähigkeit kann nur ausgewählt werden, wenn die Katze genug Mana hat.
                if self.current_player.current_mp >= self.current_player.learned_abilities[self.ability_box.current_position]["mp_cost"]:
                    # Liest den Zieltyp der Fähigkeit aus dem Wörterbuch und zeigt den entsprechenden Cursor an.
                    if self.current_player.learned_abilities[self.ability_box.current_position]["target"] == "enemy":
                        self._create_or_delete_cursor(self.enemies)
                    elif self.current_player.learned_abilities[self.ability_box.current_position]["target"] == "cat":
                        self._create_or_delete_cursor(self.cat_heroes)
                else:
                    print("Play Error Sound!")  # Platzhalter für einen zukünftigen Fehlertoneffekt.

            elif (self.single_cursor.active or self.all_cursor.active) and self.current_action is None and self.fight_active:
                # Ein Zielcursor ist aktiv — bestätigt die ausgewählte Aktion.
                if self.action_box.current_position == 0:
                    # Action-Fenster Position 0: führt den Standardangriff aus.
                    self.current_action = self.battle_sequencer.default_attack
                    # Deaktiviert den Cursor, behält aber target_group bei (erforderlich für die Aktion).
                    self._create_or_delete_cursor(self.target_group)
                    self.battle_sequencer.action_sequence_active = True

                if self.action_box.current_position == 1:
                    # Action-Fenster Position 1: verwendet einen Gegenstand.
                    self.current_action = self.battle_sequencer.use
                    self._create_or_delete_cursor(self.target_group)
                    self.battle_sequencer.action_sequence_active = True
                    self.item_box.active    = False
                    self.tooltip_box.active = False

                if self.action_box.current_position == 2:
                    # Action-Fenster Position 2 (Magie / Gebet / Fähigkeiten):
                    # Stimmt den Methodennamen der ausgewählten Fähigkeit mit allen verfügbaren Methoden ab
                    # und weist die übereinstimmende Methode als aktuelle Aktion zu.
                    for method in self.battle_sequencer.all_abilities:
                        if method.__name__ == self.current_player.learned_abilities[self.ability_box.current_position]["method"]:
                            self.current_action = method
                            break
                    # Zieht die MP-Kosten der Fähigkeit vom aktuellen Mana der Katze ab.
                    self.current_player.current_mp -= self.current_player.learned_abilities[self.ability_box.current_position]["mp_cost"]
                    self._create_or_delete_cursor(self.target_group)
                    self.battle_sequencer.action_sequence_active = True
                    self.ability_box.active = False
                    self.tooltip_box.active = False

            elif not self.fight_active and not self.fight_won and not self.game_over:
                # Startet den Kampf, wenn auf dem Startbildschirm ENTER gedrückt wird.
                if self.start_box.start_phase == 0:
                    # 1. Enter: zeigt den Prolog und verbirgt das Logo.
                    self.start_box.start_phase = 1
                    if self.arcade_click_sound is not None: # Spielt den Klick-Sound ab, wenn er geladen wurde.
                        try:
                            self.arcade_click_sound.play()
                        except Exception:
                            pass
                    pygame.time.delay(1000) # Fügt eine kurze Verzögerung hinzu, damit der Soundeffekt hörbar ist, bevor der Bildschirm wechselt.
                else:
                    # 2. Enter: startet den Kampf.
                    if self.arcade_click_sound is not None:
                        try:
                            self.arcade_click_sound.play()
                        except Exception:
                            pass
                    pygame.time.delay(1000)
                    # Musik wechseln
                    try:
                        pygame.mixer.music.stop()
                        battle_path = os.path.join("audio", "background", "Battle_soundtrack.mp3")
                        pygame.mixer.music.load(battle_path)
                        pygame.mixer.music.play(-1) # Spielt das Lied in einer unendlichen Schleife.
                        pygame.mixer.music.set_volume(0.5)
                    except Exception as e:
                        print("Warning: Battle soundtrack konnte nicht geladen werden:", e)
                    self.fight_active = True
                    self.background = pygame.transform.scale(
                        pygame.image.load("images/background.png").convert_alpha(), (self.screen_rect.width, self.screen_rect.height)
                    )

            elif not self.fight_active and self.fight_won or self.game_over:
                sys.exit()
            


        # ESCAPE — bricht die aktuelle Aktion oder Auswahl ab.
        if event.key == pygame.K_ESCAPE and not self.current_action and not self.show_status and self.fight_active:
            if self.single_cursor.active or self.all_cursor.active:
                # Bricht die aktuelle Zielauswahl ab und öffnet das relevante Fenster erneut.
                self._create_or_delete_cursor(None)
                if self.action_box.current_position == 0:
                    self.action_box.active = True
                elif self.action_box.current_position == 1:
                    self.item_box.active = True
                elif self.action_box.current_position == 2:
                    self.ability_box.active = True
            elif self.item_box.active:
                # Bricht die Gegenstandauswahl ab und kehrt zum Action-Fenster zurück.
                self.item_box.active          = False
                self.action_box.active        = True
                self.item_box.current_position = 0
                self.tooltip_box.active       = False
            elif self.ability_box.active:
                # Bricht die Fähigkeitsauswahl ab und kehrt zum Action-Fenster zurück.
                self.ability_box.active          = False
                self.action_box.active           = True
                self.ability_box.current_position = 0
                self.tooltip_box.active          = False

        # H — aktiviert/deaktiviert die Hilfe-Box.
        if event.key == pygame.K_h:
            self.help_box.active = not self.help_box.active

    # ==========================================================================
    # CURSOR MANAGEMENT
    # ==========================================================================

    def _create_or_delete_cursor(self, group):
        """Erstellt oder entfernt den Zielauswahlcursor"""
        self.target_group = group

        # Bestimmen Sie aus dem Wörterbucheintrag der aktuellen Fähigkeit, ob gezeichnet werden soll
        # ein Single-Target-Cursor oder ein Mehrfach-Zielcursor.
        if self.ability_box.active and self.current_player.learned_abilities[self.ability_box.current_position]["t_number"] == "all":
            cursor = self.all_cursor
        else:
            cursor = self.single_cursor

        # Cursor umschalten: deaktivieren, wenn er bereits aktiv ist, sonst aktivieren.
        cursor.active = not cursor.active

    # ==========================================================================
    # TURN LOGIC
    # ==========================================================================

    def _check_start_turn(self):
        """
        Überprüft, ob die Bedingungen für den Start eines neuen Zuges erfüllt sind.
        Falls ja, wählt den nächsten aktiven Spieler. Tote Kämpfer werden übersprungen
        automatisch durch Erhöhung des Runden-Zählers, bis ein lebender gefunden wird.
        """
        if self.next_turn:
            self.item_box.active    = False
            self.ability_box.active = False
            self.tooltip_box.active = False

            while self.next_turn:
                self.current_player = self.fighting_order[self.turn_timer]

                if not self.current_player.is_alive:
                    # Überspringt tote Kämpfer durch Erhöhung des Timers.
                    self.turn_timer += 1
                    if self.turn_timer > len(self.fighting_order) - 1:
                        self.turn_timer = 0
                        for player in self.fighting_order:
                            player.action = True  # Stellt Aktionen für alle Kämpfer am Anfang einer neuen Runde wieder her.
                else:
                    # Lebenden Kämpfer gefunden — beende die Schleife.
                    self.next_turn = False

    def check_status_effect(self):
        """
        Überprüft aktive Statuseffekte und wendet deren Auswirkungen an.
        Läuft einmal pro Runde für den aktuellen Spieler, wenn er Statuseffekte hat
        die in diesem Zug noch nicht verarbeitet wurden.
        """
        if self.current_player.status_effects and not self.status_done:
            if not self.show_status:
                self.status_i  = len(self.current_player.status_effects) - 1
                self.show_status = True

            if not self.status_i < 0 and not self.battle_sequencer.damage_sequence_active:
                self.battle_sequencer.status_effect_calculator(
                    self.current_player,
                    self.current_player.status_effects[self.status_i]
                )
                self.status_i -= 1
                if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
                    self.battle_sequencer.damage_sequence_active = True
                    self.tooltip_box.active = True

            elif self.status_i < 0 and not self.battle_sequencer.damage_sequence_active:
                # Alle Statuseffekte wurden verarbeitet — aufräumen.
                self.status_done     = True
                self.show_status     = False
                self.tooltip_box.active = False
                self.status_i        = None

                if self.current_player.current_hp <= 0:
                    self.current_player.is_alive = False
                    self.current_player.status_effects.clear()
                    self.current_player.action = False

                if "stun" in self.current_player.status_effects:
                    self.battle_sequencer.action_sequence_active = False
                    self.current_player.action = False

                self.check_status_timer()

    def check_status_timer(self):
        """Reduziert und entfernt Statuseffekte, deren Timer abgelaufen sind."""
        if "burn"    in self.current_player.status_effects and self.current_player.burn_timer    == 0:
            self.current_player.status_effects.remove("burn")
        if "stun"    in self.current_player.status_effects and self.current_player.stun_timer    == 0:
            self.current_player.status_effects.remove("stun")
        if "protect" in self.current_player.status_effects and self.current_player.protect_timer == 0:
            self.current_player.status_effects.remove("protect")
            self.current_player.defence -= 20  # Entfernt den von Protect gewährten Verteidigungsbonus.

    def check_enemy_turn(self):
        """Löst spezielle Feindbehaviors am Anfang ihres Zuges aus."""
        if self.current_player in self.enemies:
            if self.current_player.revive_minions:
                self.battle_sequencer.revive_minions(
                    self.current_player, self.enemies, self.dead_enemies, self.enemy_action
                )
            if self.current_player.rage_modus:
                self.battle_sequencer.rage_modus(self.current_player)
            self.enemy_turn()

    def enemy_turn(self):
        """
        Führt den Zug des Feindes aus.
        Wählt eine zufällige Fähigkeit aus den verfügbaren Fähigkeiten des Feindes, löst auf
        abgestimmte Methode, bestimmt Ziele und startet eine 3-Sekunden-Vorangriffsver zauberung.
        """
        if not self.enemy_action:
            # Wählt eine zufällige Fähigkeit aus der Liste der verfügbaren Fähigkeiten des Feindes.
            self.enemy_action = choice(self.current_player.available_skills)

            # Findet die Methode, deren Name dem Eintrag 'method' der ausgewählten Fähigkeit entspricht.
            for method in self.battle_sequencer.enemy_abilities:
                if method.__name__ == self.enemy_action["method"]:
                    self.current_action = method
                    break

            if self.enemy_action["target"] == "cat":
                # Nur lebende Katzen sind gültige Ziele.
                for cat in self.cat_heroes:
                    if cat.is_alive:
                        self.target_group.append(cat)
                if self.enemy_action["t_number"] == "single":
                    # Single-Target: wählt eine zufällige lebende Katze.
                    self.enemy_target = choice(self.target_group)

            elif self.enemy_action["target"] == "enemy":
                if self.enemy_action["t_number"] == "all":
                    self.target_group = self.enemies
                elif self.enemy_action["t_number"] == "single":
                    self.enemy_target = choice(self.enemies)

            # Startet einen 3-Sekunden-Countdown, bevor der Angriff ausgeführt wird.
            self.battle_sequencer.enemy_attack_timer = pygame.time.get_ticks()
            self.battle_sequencer.enemy_attack_ready = False
            self.battle_sequencer.action_sequence_active = True

    # ==========================================================================
    # ACTION EXECUTION
    # ==========================================================================

    def _check_for_action(self):
        """
        Überprüft, ob eine Aktion ausgeführt wird, und treibt sie zum Abschluss.
        Für Helden: führt die ausgewählte Aktion mit den korrekten Zielparametern aus.
        Für Feinde: wartet auf die Vorangriffsver zauberung, dann führt die Aktion aus.
        Sobald sowohl die Aktionssequenz als auch die Schadensanzeige beendet sind,
        wird die aktuelle Aktion gelöscht und der Zug des Spielers endet.
        """
        if self.current_action:
            if self.battle_sequencer.action_sequence_active and self.current_player in self.cat_heroes:
                if self.current_action == self.battle_sequencer.use:
                    self.current_action == self.current_action(
                        self.target_group[self.current_target],
                        self.item_box.current_items[self.item_box.current_position]
                    )
                # Wenn die ausgewählte Fähigkeit alle Mitglieder einer Gruppe anvisiert, übergibt die ganze Gruppe.
                elif (self.action_box.current_position == 2 and
                      self.current_player.learned_abilities[self.ability_box.current_position]["t_number"] == "all"):
                    self.current_action(self.current_player, self.target_group)
                else:
                    self.current_action(self.current_player, self.target_group[self.current_target])

                # Nachdem die Aktionssequenz endet, startet oder überspringt den Phase der Schadensanzeige.
                if not self.battle_sequencer.action_sequence_active:
                    if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
                        self.battle_sequencer.damage_sequence_active = True
                    else:
                        self.battle_sequencer.damage_sequence_active = False

            elif self.battle_sequencer.action_sequence_active and self.current_player in self.enemies:
                # Wartet, bis die 3-Sekunden-Vorangriffsver zauberung verstreicht.
                if not self.battle_sequencer.enemy_attack_ready:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.battle_sequencer.enemy_attack_timer >= self.battle_sequencer.enemy_attack_delay:
                        self.battle_sequencer.enemy_attack_ready = True

                # Führt den Angriff des Feindes aus, sobald die Verzögerung abgelaufen ist.
                if self.battle_sequencer.enemy_attack_ready and not self.show_status:
                    if self.enemy_action["t_number"] == "all":
                        self.current_action(self.current_player, self.target_group)
                    elif self.enemy_action["t_number"] == "single":
                        self.current_action(self.current_player, self.enemy_target)
                    if not self.battle_sequencer.action_sequence_active:
                        if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
                            self.battle_sequencer.damage_sequence_active = True

            # Sobald beide Sequenzen abgeschlossen sind, setzt den Aktionsstatus zurück und beendet den Zug.
            if not self.battle_sequencer.action_sequence_active and not self.battle_sequencer.damage_sequence_active:
                self.current_action  = None
                self.enemy_action    = None
                self.current_player.action = False

    # ==========================================================================
    # LIFE / DEATH CHECKS
    # ==========================================================================

    def _check_if_alive(self):
        """
        Überprüft, ob ein Kämpfer gestorben ist.
        Die Überprüfung läuft nur, nachdem die Schadensszahlen angezeigt wurden.
        Tote Feinde werden aus der aktiven Feindeliste entfernt und zu dead_enemies hinzugefügt.
        """
        if not self.battle_sequencer.damage_sequence_active:
            for player in self.fighting_order:
                if player.current_hp <= 0:
                    player.is_alive = False
                    player.status_effects.clear()

            for enemy in self.enemies:
                if not enemy.is_alive:
                    enemy.status_effects.clear()
                    self.dead_enemies.append(enemy)
                    self.enemies.remove(enemy)

    def _check_next_turn(self):
        """
        Überprüft, ob der aktuelle Zug beendet werden soll.
        Der Zug endet, wenn der aktive Spieler keine Aktionen mehr hat.
        Setzt alle UI-Auswahlen zurück und erhöht (oder setzt) den Runden-Zähler.
        Am Ende einer vollständigen Runde werden die Aktionen aller Kämpfer wiederhergestellt.
        """
        if not self.current_player.action and self.fight_active:
            self.turn_timer += 1

            # Setzt den Runden-Zähler und stellt Aktionen für eine neue Runde wieder her.
            if self.turn_timer > len(self.fighting_order) - 1:
                self.turn_timer = 0
                for player in self.fighting_order:
                    player.action = True

            # Wendet Minion-Schutz für jeden Feind an, der ihn hat.
            for enemy in self.enemies:
                if enemy.minion_protection:
                    self.battle_sequencer.minion_protection(enemy, self.enemies)
                    

            # Setzt alle UI-Cursor-Positionen auf ihre Standardwerte zurück.
            self.action_box.current_position  = 0  # Standard: Angriff
            self.item_box.current_position    = 0  # Standard: erster Gegenstand in der Liste
            self.ability_box.current_position = 0  # Standard: erste Fähigkeit in der Liste
            self.current_target               = 0  # Standard: erster Feind in der Gruppe
            self.target_group                 = []

            # Setzt die Statuseffekt-Verfolgung für den neuen Zug zurück.
            self.show_status      = False
            self.tooltip_box.active = False
            self.status_done      = False

            self.next_turn        = True   # Signalisiert, dass der nächste Zug beginnen sollte.
            self.action_box.active = True  # Das Action-Fenster ist standardmäßig zu Beginn jeden Zuges offen.
            self.current_player.was_selected = False

            # Setzt das Sprite der Heiler-Katze auf ihre Standard-Ruhepause zurück.
            self.healer_cat.image = self.healer_cat.default_sprite#

    def check_for_fight_end(self):
        if not self.enemies:
            self.fight_won = True
            self.fight_active = False
        elif all(cat.is_alive == False for cat in self.cat_heroes):
            self.game_over = True
            self.fight_active = False
            




# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # Erstellt eine Spielinstanz und startet das Spiel.
    cf = Cat_Fight()
    cf.run_game()


# ==============================================================================
# INACTIVE / ARCHIVED CODE
# ==============================================================================
#
#   def check_status_effect(self):
#       if self.current_player.status_effect != None and not self.status_done:
#           if not self.show_status:
#               self.battle_sequencer.status_effects(self.current_player)
#               if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
#                   self.show_status = True
#                   self.battle_sequencer.damage_sequence_active = True
#                   self.tooltip_box.active = True
#               else:
#                   self.status_done = True
#           if not self.battle_sequencer.damage_sequence_active and not self.status_done:
#               self.show_status = False
#               self.status_done = True
#               self.tooltip_box.active = False
