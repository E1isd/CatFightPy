import pygame
import ctypes
import sys
import random
from random import choice
from cats import *
from enemys import *
from boxes import *
from cursor import Cursor
from action_sequence import Action

class Cat_Fight:
    """Das Hauptspiel als Klasse"""
    def __init__(self):

        # Diese Codezeile sorgt dafür, dass Windows die Bildschirmskalierung nicht in das Spiel übernimmt. Dadurch konnte es vorher trotz einer
        # Auflösung von 1920 x 1080, in der das Spiel programmiert ist, zu verwaschenen Grafiken und Schriften kommen.
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except AttributeError:
            pass 

        pygame.init()
        self.screen = pygame.display.set_mode((1920,1080),pygame.SCALED | pygame.FULLSCREEN)# Initialisiert den Bildschirm auf dem das Spiel stattfindet (in Vollbild)
        self.screen_rect = self.screen.get_rect()
        self.bg_color = (200, 205, 220) # Variable für Hintergrundfarbe des Blockes in RGB-Werten
        self.background = pygame.transform.scale(pygame.image.load("images/background.png").convert_alpha(),(1920,1080))
        pygame.display.set_caption("Katzen RPG")# Text für die Fensterzeile

        self.clock = pygame.time.Clock() #Clock misst die Zeit und ist für die Framerate wichtig

        # Heldenkatzen:
        self.warrior_cat = Warrior(self,1100,370,"Warrior")
        self.healer_cat = Cleric (self,1150,470, "Cleric")
        self.casting_cat = Mage(self,1200,620, "Mage")

        # Gegner:
        self.boss = Necromancer(self,350,350,"Evil Necromancer Cat")
        self.minion_1 = Poison_Minion(self,650,370, "Cat-Minion 1")
        self.minion_2 = Rage_Minion (self,650,620, "Cat-Minion 2")

        self.current_inventory = Inventory(self) # Klasse für das aktuelle Inventar

        # Gruppen
        # Alle Kampfteilnehmer für den Kampf
        self.cat_heroes = [self.warrior_cat,self.healer_cat,self.casting_cat] # Gruppe für die Heldenkatzen
        random.shuffle(self.cat_heroes) # Die Reihenfolge der Heldenkatzen wird zufällig gemischt, damit die Reihenfolge der Helden in jedem Durchlauf anders ist
        self.enemies = [self.minion_1,self.minion_2,self.boss] # Gruppe für die Gegner
        self.fighting_order = [self.cat_heroes[0], self.minion_1, self.cat_heroes[1], self.minion_2, self.cat_heroes[2], self.boss]
        self.cat_heroes = [self.warrior_cat,self.healer_cat,self.casting_cat] # Nach dem zufälligen Mischen, wird die Reihenfolge wieder normal gesetzt. Wichtig für die korrekte Cursor Auswahl
        self.target_group = [] # Die aktuelle angewählte Gruppe, wichtig für die Erschaffung des Auswähl-Cursors und für Fähigkeitssequenzen


        # Schaltflächen:
        self.cat_box = Cat_Box(self,self.warrior_cat,self.healer_cat,self.casting_cat) # Katzennamen, HP & MP
        self.action_box = Action_Box(self,self.cat_box) # Box mit den Aktionsmöglichkeiten (Angriff etc.)
        self.enemy_box = Enemy_Box(self,self.boss,self.minion_1,self.minion_2,self.action_box) # Gegnernamen
        self.item_box = Item_Box(self,self.action_box) # Box, die die verfügbaren Items anzeigt
        self.ability_box = Ability_Box(self,self.action_box) # Box, die die verfügbaren Abilitys anzeigt
        self.tooltip_box = Tooltip_Box(self) # Box, die Abilitys und Gegnerangriffe beschreibt 
        self.help_box = Help_Box(self,self.cat_box.rect) # Box, die Hilfe für die Steuerung anzeigt

        self.tooltip_message = "" # Die Variable für den angezeigten Text der Tooltip-Box

        # Für das Rundensystem
        self.turn_timer = 0 # Variable, die die Runden zählt
        self.current_player = self.fighting_order[self.turn_timer] # Setzt den aktuellen Spieler auf die 1. Position der Fighting-Order
        self.next_turn = False # Die Bool-Variable, die überprüft, ob die Bedingungen für eine nächste Runde gegeben ist
        
        
        self.current_target = 0 # Die int-Variable für die Auswahl des aktuellen Ziels
        self.enemy_target = None # Variable für das aktuelle Gegner-Ziel
        self.enemy_action = None # Variable für die aktuelle Gegner-Aktion

        # Cursor:
        self.player_cursor = Cursor(self,self.current_player.rect.centerx - 10,self.current_player.rect.y -30) # Cursor über aktuellem Kampfteilnehmer
        self.single_cursor = Cursor (self, 0,0) # Auswahl  für das aktuelle Ziel
        self.all_cursor = Cursor(self,0,0)# Auswahl für alle Ziele einer aktuell anvisierten Gruppe


        self.battle_sequencer = Action(self) # Klasse, die die gesamte Kampfabfolge (Angriffe, Schaden, Animationen) abhandelt
        self.current_action = None # In dieser Variable wird die aktuelle Kampfaktion gespeichert

        self.show_status = False # Bool-Variable für das Anzeigen eines Statuseffekt
        self.status_i = None
        self.status_done = False # Bool-Variable, die angibt, dass die Statuseffekt-Anzeige fertig ist
        


    def run_game(self): # Hauptfunktion (Ereignisse checken, Bildschirm/Sprites aktualisieren)
        """Die Hauptfunktion: Sie läuft so lange, bis die while-Schleife beendet ist"""
        while True:
            self._check_events() # Überprüft, ob in diesem Frame Tasteneingaben stattfinden
            self._check_start_turn() # Überprüft, ob gerade eine neue Runde gestartet ist
            self.check_status_effect() # Überprüft, ob Statusveränderungen vorliegen und handelt ihre Effekte ab
            self._check_for_action() # Überprüft, ob eine Aktion ausgeführt wird
            self._check_if_alive() # Überprüft, ob alle Kampfteilnehmer noch am Leben sind
            self._check_next_turn() # Überprüft, ob die Bedingungen für eine neue Runde gegeben sind
            self._update_screen() # Aktualisiert den Bildschirm mit allen aktualisierten Werten, Positionen etc.
            self.clock.tick(60) # Aktualisiert die Uhr und legt so die Framerate fest
 
    def _update_screen(self):
        """Zeichnet der Bildschirm mit allen Spielelementen neu"""
        self.screen.blit(self.background, (0,0))
        self._draw_game_fields() # Zeichnet die Schaltflächen 
        self._draw_charakters() # Zeichnet die Spielfiguren
        self._draw_cursor() # Zeichnet die Cursor
        self._draw_effects() # Zeichnet alle aktiven Effekte
        pygame.display.flip() # Zeichnet den Bildschirm neu
        
    
    def _draw_charakters(self):
        """Zeichnet die Spielfiguren"""
        pygame.draw.rect(self.screen,"red",self.warrior_cat)
        pygame.draw.rect(self.screen,"blue",self.casting_cat)
        
        if self.minion_1.is_alive == True:
            pygame.draw.rect(self.screen,"green",self.minion_1)
        if self.minion_2.is_alive == True:
            pygame.draw.rect(self.screen,"purple",self.minion_2.rect)
        if self.boss.is_alive == True:
            self.screen.blit(self.boss.image, (self.boss.x_position,self.boss.y_position))
            # Zeichnet die Katze nur in ihrer Standard/Idle Pose wenn gerade keine Aktion-Animation vorliegt !Muss später noch abgeändert werden,
            # wenn alle Katzen als Grafik vorliegen.
        if not self.battle_sequencer.cat_animation_active: 
            self.screen.blit(self.healer_cat.image, (self.healer_cat.x_position,self.healer_cat.y_position))

        

    def _draw_game_fields(self):
        """Zeichnet die Schaltflächen des Kampfbildschirms"""
        self.cat_box.draw_cat_box(self.current_player) # Schaltfläche mit den Namen der Katzen, sowie HP & MP
        self.enemy_box.draw_enemy_box() # Schaltflächen mit den Namen der Gegner
        if self.current_player in self.cat_heroes: # Wenn der aktuelle Kampfteilnehmer spielbar ist, wird die Action-Box gezeichnet
            self.action_box.draw_action_box(self.current_player)
        if self.item_box.active == True: # Wenn die Item-Box aktiv ist, wird sie gezeichnet
            self.item_box.draw_item_box(self.current_inventory,self.single_cursor.active)
        if self.ability_box.active == True: # Wenn die Ability-Box aktiv ist, wird sie gezeichnet
            self.ability_box.draw_ability_box(self.current_player,self.single_cursor.active,self.all_cursor.active)
        # Liest die Tooltip-Nachricht aus (wenn vorhanden) und zeichnet die Tooltip-Box(wenn aktiv):
        self.get_tooltip()
        self.tooltip_box.draw_tooltip_box(self.tooltip_message)
        self.help_box.draw_help_box()

    def get_tooltip(self):
        """Funktion, um die Nachricht für die Tooltip-Box auszulesen"""
        if self.item_box.active == True:  # Die Tooltip-Message wird aus dem Inventory-Dictonary gelesen
            self.tooltip_message = self.item_box.current_items[self.item_box.current_position]["tooltip"]
        elif self.ability_box.active == True: # Die Tooltip-Message wird aus dem Ability-Dictonary gelesen
            self.tooltip_message = self.current_player.learned_abilities[self.ability_box.current_position]["tooltip"]
        elif self.show_status == True: # Wenn ein Status-Effekt abgehandelt wird, wird eine entsprechende Nachricht abgespielt
            self.tooltip_message = self.battle_sequencer.message
        else: # Wenn kein Element mit Tooltip angewählt ist, bleibt die Message leer
            self.tooltip_message = ""     
        
    def _draw_cursor(self):
        """Zeichnet die Cursor und Marker auf das Spielfeld"""
        # Zeichnet den Marker für die aktuelle Spielfigur, dafür werden die Koordinaten des Cursors beim aktuellen Kampfteilnehmer gesetzt:
        self.player_cursor.rect.x = self.current_player.rect.centerx - 16
        self.player_cursor.rect.y = self.current_player.rect.y -40
        self.single_cursor.draw_animated_cursor(self.player_cursor.current_player_sheet,self.player_cursor.rect.x,self.player_cursor.rect.y)
        
        # Der Cursor für das Auswählen eines Ziels wird nur gezeichnet, wenn er auch aktiv ist:
        if self.single_cursor.active == True:
            if self.target_group == self.enemies: # Koordinaten, wenn das Ziel zu den Gegnern gehört
                self.single_cursor.rect.x = self.enemies[self.current_target].rect.right +10
                self.single_cursor.rect.y = self.enemies[self.current_target].rect.centery -16
                self.single_cursor.draw_animated_cursor(self.single_cursor.attack_sheet,self.single_cursor.rect.x,self.single_cursor.rect.y)
            elif self.target_group == self.cat_heroes: # Koordinaten, wenn das Ziel zu den Katzen gehört
                self.single_cursor.rect.x = self.cat_heroes[self.current_target].rect.left -40
                self.single_cursor.rect.y = self.cat_heroes[self.current_target].rect.centery -16
                self.single_cursor.draw_animated_cursor(self.single_cursor.heal_sheet,self.single_cursor.rect.x,self.single_cursor.rect.y)
        # Der Cursor für das Auswählen aller Ziele einer Gruppe
        if self.all_cursor.active == True:
            if self.target_group == self.enemies:
                for enemy in self.enemies:
                    self.all_cursor.rect.x = enemy.rect.right +10
                    self.all_cursor.rect.y = enemy.rect.centery -10
                    self.all_cursor.draw_animated_cursor(self.all_cursor.attack_sheet,self.all_cursor.rect.x,self.all_cursor.rect.y)
            elif self.target_group == self.cat_heroes:
                for cat in self.cat_heroes:
                    self.all_cursor.rect.x = cat.rect.left -40
                    self.all_cursor.rect.y = cat.rect.centery -16
                    self.all_cursor.draw_animated_cursor(self.all_cursor.heal_sheet,self.all_cursor.rect.x,self.all_cursor.rect.y)


    def _draw_effects(self):
        """Zeichnet alle aktiven Effekte (Wenn die entsprechenden Bedingungen gegeben sind)"""
        # Sprite-Animation für alle Charaktere (Helden und Gegner), die gerade an der Reihe sind
        if self.current_player and not self.battle_sequencer.cat_animation_active:
            self.current_player.update(is_selected=True) # Die Funktion für die Sprite-Animation

        if self.show_status == False:
            self.battle_sequencer.draw_damage_numbers() # Zeichnet die Schadenzahlen an den Kampfteilnehmern nach einem Angriff
        elif self.show_status == True:
            self.battle_sequencer.draw_damage_numbers(self.battle_sequencer.font_color) # Zeichnet die Statuseffekt-Schadenszahlen

        self.battle_sequencer.draw_cat_action_animation(self.current_player) # Zeichnet die Katzen-Kampf-Animation (wenn aktiv)      
        self.battle_sequencer.draw_simple_effect() # Zeichnet die Kampfeffekte (wenn aktiv)




    def _check_events(self):
        """Wartet auf Tasteneingaben vom Spieler"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Schließt das Spiel
                sys.exit()
            if event.type == pygame.KEYDOWN: # Wenn eine Taste gedrückt wird, wird überprüft, welches Event ausgelöst wird
                self.check_keydown_events(event)

    def check_keydown_events(self,event):
        """Wenn eine Taste gedrückt wird, wird auf verschiedene Events geprüft"""
        if event.key == pygame.K_q: # Event für Beenden des Spieles (Taste Q)
            sys.exit()
        if event.key == pygame.K_SPACE: # !TEMPORÄR um die Runden schnell zu skippen!!!
            if not self.current_action and not self.show_status:
                self.current_player.action = False
                if self.single_cursor.active == True or self.all_cursor.active:
                    self._create_or_delete_cursor(None)
                self.ability_box.active = False
                self.item_box.active = False
        # Alle der folgenden Tasteneingaben sind nur möglich, wenn gerade keine Aktionssequenz abgespielt wird!
        if event.key == pygame.K_DOWN and not self.current_action and not self.show_status: # Bewegung des Cursors nach unten
            if  self.action_box.active == True: # In der Action-Box
                if self.action_box.current_position < len(self.action_box.postitions)-1:
                    self.action_box.current_position +=1
            elif self.item_box.active == True and not self.single_cursor.active: # In der Item-Box
                if self.item_box.current_position < len(self.item_box.postitions)-1:
                    self.item_box.current_position +=1
            elif self.ability_box.active == True and not (self.single_cursor.active or self.all_cursor.active): # In der Ability-Box
                if self.ability_box.current_position < len(self.ability_box.postitions)-1:
                    self.ability_box.current_position +=1
            # Bewegung des Auswahlcursors für Einzelziele nach unten (die Reihenfolge beginnt wieder von vorne, 
            # wenn die Anzahl der möglichen Ziele überschritten wurde.):
            elif self.single_cursor.active == True:
                self.current_target +=1
                if self.current_target > len(self.target_group) -1:
                    self.current_target = 0
        if event.key == pygame.K_UP and not self.current_action and not self.show_status: # Bewegung des Cursors nach oben
            if self.action_box.active == True: # In der Action-Box
                if self.action_box.current_position > 0:
                    self.action_box.current_position -=1
            elif self.item_box.active == True and not self.single_cursor.active: # In der Item-Box
                if self.item_box.current_position > 0:
                    self.item_box.current_position -=1
            elif self.ability_box.active == True and not (self.single_cursor.active or self.all_cursor.active): # In der Ability-Box
                if self.ability_box.current_position >0:
                    self.ability_box.current_position -=1
            # Bewegung des Auswahlcursors nach oben (die Reihenfolge beginnt wieder von hinten, 
            # wenn die Anzahl der möglichen Ziele überschritten wurde.):
            elif self.single_cursor.active == True:
                self.current_target -= 1
                if self.current_target < 0:
                    self.current_target = len(self.target_group) -1
        if event.key == pygame.K_RETURN and not self.current_action and not self.show_status: # Die Taste mit der Aktionen ausgeführt werden 
                if self.current_player in self.cat_heroes and self.action_box.active == True:
                    if self.action_box.current_position == 0: # Aktiviert den Cursor für die Stadtardattacke
                        self._create_or_delete_cursor(self.enemies)
                        self.action_box.active = False
                    if self.action_box.current_position == 1: # Aktiviert die Item-Box
                        self.item_box.active = True
                        self.tooltip_box.active = True
                        self.action_box.active = False
                    if self.action_box.current_position == 2: # Aktiviert die Ability-Box
                        self.ability_box.active = True
                        self.tooltip_box.active = True
                        self.action_box.active = False
                elif self.item_box.active == True and not self.single_cursor.active: # Wenn die Item-Box aktiv ist, wird der Cursor aktiviert
                    self._create_or_delete_cursor(self.cat_heroes) # Der Cursor hat als Ziel die Katzen (gibt momentan nur Heilitems)
                elif self.ability_box.active == True and not self.single_cursor.active and not self.all_cursor.active:
                    # Die aktuell ausgewählte Fähigkeit kann nur ausgewählt werden, wenn die Katze die erforderlichen MP hat:
                    if self.current_player.current_mp >= self.current_player.learned_abilities[self.ability_box.current_position]["mp_cost"]:
                        # Aus dem Dictonary wird gelesen, ob die Fähigkeit Gegner angreift oder Katzen heilt. Entsprechend werden die Cursor
                        # gezeichnet:
                        if self.current_player.learned_abilities[self.ability_box.current_position]["target"] == "enemy":
                            self._create_or_delete_cursor(self.enemies)
                        elif self.current_player.learned_abilities[self.ability_box.current_position]["target"] == "cat":
                            self._create_or_delete_cursor(self.cat_heroes)
                    else:
                        print("Play Error Sound!") # Platzhalter für späteren Soundeffekt
                elif (self.single_cursor.active == True or self.all_cursor.active == True) and self.current_action == None: # Aktionen, wenn der Cursor aktiv ist
                    if self.action_box.current_position == 0: # Wenn der Action-Box Cursor auf "Attack" steht...
                        self.current_action = self.battle_sequencer.default_attack # ... wird die Standard-Attacke als aktuelle Aktion festgelegt
                        # Der Attack-cursor wird wieder deaktiviert, dabei bleibt die aktuell ausgewählte Gruppe als target_group 
                        # (wichtig für die aktuelle Aktion) aktiv:
                        self._create_or_delete_cursor(self.target_group) 
                        self.battle_sequencer.action_sequence_active = True # Mit dieser Boolvariable beginnt die Einleitung der Kampfsequenz
                    if self.action_box.current_position == 1: # Wenn der Action-Box Cursor auf "Items" steht...
                        self.current_action = self.battle_sequencer.use #... wird "Use" als aktuelle Aktion festgelegt
                        self._create_or_delete_cursor(self.target_group) 
                        self.battle_sequencer.action_sequence_active = True 
                        self.item_box.active = False
                        self.tooltip_box.active = False
                    if self.action_box.current_position == 2: # Wenn der Action-Box Cursor auf Magic, Prayer oder Skills steht...
                        # ... werden die Namen aller verfügbaren Methoden mit dem entsprechenden Eintrag der aktuell ausgewählten Ability 
                        # verglichen. Sobald es ein "Match" gibt, wird diese Methode als aktuelle Aktion festgelegt und die For-Schleife
                        # bricht ab (break).
                        for method in self.battle_sequencer.all_abilities:
                            if method.__name__ == self.current_player.learned_abilities[self.ability_box.current_position]["method"]:
                                self.current_action = method
                                break
                        # Die Magiekosten der Ability werden von den aktuellen Manapunkten der Katze abgezogen
                        self.current_player.current_mp -= self.current_player.learned_abilities[self.ability_box.current_position]["mp_cost"]
                        self._create_or_delete_cursor(self.target_group) 
                        self.battle_sequencer.action_sequence_active = True 
                        self.ability_box.active = False
                        self.tooltip_box.active = False

        if event.key == pygame.K_ESCAPE and not self.current_action and not self.show_status: # Abbruch von Aktionen und Auswahlpunkten
            if self.single_cursor.active == True or self.all_cursor.active == True: # Bricht die aktuelle Cursor-Auswahl ab
                self._create_or_delete_cursor(None)
                if self.action_box.current_position == 0:
                    self.action_box.active = True
                elif self.action_box.current_position == 1:
                    self.item_box.active = True
                elif self.action_box.current_position == 2:
                    self.ability_box.active = True
            elif self.item_box.active == True: # Bricht die aktuelle Item-Auswahl ab
                self.item_box.active = False
                self.action_box.active = True
                self.item_box.current_position = 0
                self.tooltip_box.active = False
            elif self.ability_box.active == True: # Bricht die aktuelle Ability-Auswahl ab
                self.ability_box.active = False
                self.action_box.active = True
                self.ability_box.current_position = 0
                self.tooltip_box.active = False
        if event.key == pygame.K_h: # Taste, um die Hilfe Box zu aktivieren oder deaktivieren
            if self.help_box.active == True:
                self.help_box.active = False
            else:
                self.help_box.active = True

    def _create_or_delete_cursor(self,group): # Als Parameter die Gruppe, deren Charakter(e) anwählbar sein sollen
        """Erschafft oder Löscht den Angriffscursor"""
        self.target_group = group
        # Aufgrund des Dictonary-Eintrags der aktuell ausgewählten Fähigkeit wird ermittelt, ob Cursor für ein Einzelziel oder
        # für alle Ziele der entsprechenden Gruppe gezeichnet werden sollen:
        if self.ability_box.active == True and self.current_player.learned_abilities[self.ability_box.current_position]["t_number"] == "all":
            cursor = self.all_cursor
        else:
            cursor = self.single_cursor
        if cursor.active == True: # Falls bereits ein Auswahlcursor aktiv ist, wird er durch diesen Befehl wieder deaktivert
            cursor.active = False
        else:
            cursor.active = True

            
    def _check_start_turn(self):
            """Überprüft, ob die Bedingung für den Start der Runde gegeben ist"""
            # Falls ja, wird ein neuer aktiver Spieler ausgewählt
            if self.next_turn == True:
                # Schließt die Item-Box und Ability-Box, falls sie noch geöffnet sein sollten
                self.item_box.active = False
                self.ability_box.active = False
                self.tooltip_box.active = False
                while self.next_turn == True: 
                    self.current_player = self.fighting_order[self.turn_timer] # Der nächste Spieler wird anhand der Kampfreihenfolge festgelegt
                    # Wenn der Spieler zur Gegnergruppe gehört, wird die while-Schleife beendet und die Methode für die Gegnerrunde ausgeführt:
                    if self.current_player in self.enemies: 
                        self.next_turn = False
                        print(f"{self.current_player.name} ist dran") # !!Temporär!! Print-Befehl wenn ein Gegner dran ist
                        self.enemy_turn() 
                    # Falls der aktuelle Spieler eine tote Katze ist, wird der Rundentimer eins erhöht (d.h. die Runde wird übersprungen)
                    # und die while-Schleife beginnt von vorne. So wird sichergestellt, dass tote Spieler übersprungen werden:
                    elif self.current_player in self.cat_heroes and self.current_player.is_alive == False:
                        self.turn_timer +=1
                    else: # Bei einer lebendingen Katze als aktuellen Spieler wird die Schleife aufgelöst
                        self.next_turn = False
        
    def check_status_effect(self):
        """Überprüft, ob Status-Effekte vorliegen und führt die entsprechenden Effekte aus"""
        # Die Methode wird ausgeführt, wenn der aktuelle Spieler einen Status-Effekt hat und der Status-Effekt in seiner Runde noch nicht
        # abgehandelt wurde.
        if self.current_player.status_effects and not self.status_done:
            if not self.show_status:
                self.status_i = len(self.current_player.status_effects) - 1
                self.show_status = True
            if not self.status_i < 0 and not self.battle_sequencer.damage_sequence_active:
                self.battle_sequencer.status_effect_calculator(self.current_player, self.current_player.status_effects[self.status_i])
                self.status_i -=1
                if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
                     self.battle_sequencer.damage_sequence_active = True
                     self.tooltip_box.active = True
            elif self.status_i < 0 and not self.battle_sequencer.damage_sequence_active:
                self.status_done = True
                self.show_status = False
                self.tooltip_box.active = False
                self.status_i = None
                if "stun" in self.current_player.status_effects:
                    self.battle_sequencer.action_sequence_active = False
                    self.current_player.action = False
                self.check_status_timer()
        
    
    def check_status_timer(self):
        """Methode, die die Timer für die Statuseffekte überprüft"""
        if "burn" in self.current_player.status_effects and self.current_player.burn_timer == 0:
            self.current_player.status_effects.remove("burn")
        if "stun" in self.current_player.status_effects and self.current_player.stun_timer == 0:
            self.current_player.status_effects.remove("stun")
                


                    

    def enemy_turn(self):
        """Führt den Gegnerzug aus"""
        # Als aktuelle Fähigkeit wird eine Fähigkeit aus der Liste der möglichen Angriffe gewählt:
        self.enemy_action = choice(self.current_player.available_skills) 
        # Anhand des Dictonary-Eintrags wird die passende Methode zu der Fähigkeit ermittelt und als aktuelle Aktion festgelegt:
        for method in self.battle_sequencer.enemy_abilities:
            if method.__name__ == self.enemy_action["method"]:
                self.current_action = method
                break 
        if self.enemy_action["target"] == "cat": # Wenn das Ziel der Aktion die Katzen sind
            for cat in self.cat_heroes:
                if cat.is_alive == True: # Als mögliche Ziele kommen nur lebendige Katzen in Frage
                    self.target_group.append(cat)
            if self.enemy_action["t_number"] == "single": # Bei Aktionen gegen ein Einzelziel wird das Ziel zufällig aus der Gruppe ermittelt
                self.enemy_target = choice(self.target_group)
        elif self.enemy_action["target"] == "enemy":
            if self.enemy_action["t_number"] == "all":
                self.target_group = self.enemies
            elif self.enemy_action["t_number"] == "single":
                self.enemy_target = choice(self.enemies)
        # Timer starten für 3 Sekunden Wartezeit vor dem Angriff
        self.battle_sequencer.enemy_attack_timer = pygame.time.get_ticks()
        self.battle_sequencer.enemy_attack_ready = False
        self.battle_sequencer.action_sequence_active = True

    
    def _check_for_action(self):
        """Überprüft ob eine Aktion stattfindet"""
        if self.current_action : # Diese Funktion wird erst ausgeführt, wenn eine aktuelle Aktion festgelegt ist
            # Solange die Variable für den action-sequencer wahr ist, wird die festgelegete Aktion ausgeführt
            if self.battle_sequencer.action_sequence_active == True and self.current_player in self.cat_heroes: 
                if self.current_action == self.battle_sequencer.use:
                    self.current_action == self.current_action(self.target_group[self.current_target], self.item_box.current_items[self.item_box.current_position])
            # Aufgrund des Dictonary-Eintrags der aktuell ausgewählten Fähigkeit wird ermittelt, die Parameter in der aktuellen Ability-Methode
            # für Einzelziele oder eine ganze Gruppe zu verwenden:
                elif self.action_box.current_position == 2 and self.current_player.learned_abilities[self.ability_box.current_position]["t_number"] == "all":
                    self.current_action(self.current_player, self.target_group)
                else:
                    self.current_action(self.current_player, self.target_group[self.current_target]) 
            # Wenn die Aktion beendet ist, wird Sequenz für das Anzeigen der Schadenswerte angezeigt
                if self.battle_sequencer.action_sequence_active == False:
                    if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
                        self.battle_sequencer.damage_sequence_active = True
            elif self.battle_sequencer.action_sequence_active == True and self.current_player in self.enemies:
                # Prüfen ob 3 Sekunden vergangen sind seit dem Start des Gegnerzugs
                if self.battle_sequencer.enemy_attack_ready == False:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.battle_sequencer.enemy_attack_timer >= self.battle_sequencer.enemy_attack_delay:
                        self.battle_sequencer.enemy_attack_ready = True
                # Wenn die Wartezeit vorbei ist, wird der Angriff ausgeführt
                if self.battle_sequencer.enemy_attack_ready and not self.show_status:
                    if self.enemy_action["t_number"] == "all":
                        self.current_action(self.current_player, self.target_group)
                    elif self.enemy_action["t_number"] == "single":
                        self.current_action(self.current_player, self.enemy_target)
                    if self.battle_sequencer.action_sequence_active == False:
                        if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
                            self.battle_sequencer.damage_sequence_active = True
            # Zum Schluss wird der Wert für die aktuelle Aktion zurückgesetzt und der Wert für die Aktionsmöglichkeiten des aktuellen
            # Spielers auf False gesetzt. Dies führt zur Beendigung der Runde:
            if self.battle_sequencer.action_sequence_active == False and self.battle_sequencer.damage_sequence_active == False:
                self.current_action = None
                self.current_player.action = False

    def _check_if_alive(self):
        """Überprüft, ob ein Kampfteilnehmer gestorben ist"""
        if self.battle_sequencer.damage_sequence_active == False: # Der Check findet erst statt, wenn der damage auf dem Bildschirm angezeigt wurde
            for player in self.fighting_order:
                if player.current_hp <= 0: # Wenn die aktuelle HP kleiner gleich 0 ist, wird die Lebens-Variable auf False gesetzt
                    player.is_alive = False
                    player.status_effect = None
        # Falls ein Gegner tot ist, wird er sowohl aus der Gruppe der Kampfteilnehmer, als auch aus der Gegnergrupe gelöscht
        for enemy in self.enemies:
            if enemy.is_alive == False:
                self.enemies.remove(enemy)
                self.fighting_order.remove(enemy)

    def _check_next_turn(self):
        """Überprüft, ob die Bedingung für den Abschluss der Runde gegeben ist"""
        # Die Runde endet, wenn der aktive Spieler keine Aktion mehr übrig hat
        if self.current_player.action == False:
            self.turn_timer +=1 # Der Rundenzähler wird um eins erhöht
            # Wenn der Rundenzähler größer ist als die aktuelle Anzahl Kampfteilnehmer, wird der 
            # Zähler wieder zurückgesetzt und die Kampfreihenfolge beginnt von vorne
            if self.turn_timer > len(self.fighting_order) -1:
                self.turn_timer = 0
                for player in self.fighting_order: # Jeder der Kampfteilnehmer erhält wieder eine Aktion
                    player.action = True
            self.action_box.current_position = 0 # Zurücksetzen der Cursor-Position für die Action-Box (Standartpos.: Attack)
            self.item_box.current_position = 0 # Zurücksetzen der Cursor-Postition für Item-Box Auswahl
            self.ability_box.current_position = 0 # Zurücksetzen der Cursor-Postition für die Ability-Box Auswahl
            self.current_target = 0 # Zurücksetzen des Angriffscursors (Standartpos.: Erster Gegner der Gruppe)
            self.target_group = [] # Die angewählte Gruppe wird wieder zurückgesetzt
            self.show_status = False
            self.tooltip_box.active = False
            self.status_done = False # Die Bool-Variable für die Statusabhandlung wird wieder zurückgesetzt
            self.next_turn = True # Die Variable für die nächste Runde wird auf True gesetzt
            self.action_box.active = True # Die Aktionsbox wird standardmäßig wieder auf aktiv gesetzt




if __name__ == "__main__":
    #Erstellt eine Spielinstanz und führt das Spiel aus.
    cf = Cat_Fight()
    cf.run_game()




# Inaktiver Code
    #def check_status_effect(self):
        #"""Überprüft, ob Status-Effekte vorliegen und führt die entsprechenden Effekte aus"""
        # Die Methode wird ausgeführt, wenn der aktuelle Spieler einen Status-Effekt hat und der Status-Effekt in seiner Runde noch nicht
        # abgehandelt wurde.
        #if self.current_player.status_effect !=None and not self.status_done: 
            #if not self.show_status:
                 #self.battle_sequencer.status_effects(self.current_player) # Führt die Methode zur einmaligen Abhandlung des Statuseffekts aus
                 # Wenn der Statuseffekt Schaden verursacht, wird damage_sequence und show_status aktiviert, woraufhin der Schaden abgehandelt wird.
                 # Außerdem wird ein Tooltip eingeblendet, der anzeigt, warum der Spieler Schaden nimmt.
                 #if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
                     #self.show_status = True
                     #self.battle_sequencer.damage_sequence_active = True
                     #self.tooltip_box.active = True
                # else: # Wenn der status_effect ohne Schaden auskommt, wird diese Methode sofort beendet
                     #self.status_done = True
            #if self.battle_sequencer.damage_sequence_active == False and not self.status_done: # Nach Schadensanzeige wird Methode beendet
                #self.show_status = False
                #self.status_done = True
                #self.tooltip_box.active = False
