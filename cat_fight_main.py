import pygame
import sys
from cats import *
from enemys import *
from boxes import *
from cursor import Cursor
from action_sequence import Action

class Cat_Fight:
    """Das Hauptspiel als Klasse"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)# Initialisiert den Bildschirm auf dem das Spiel stattfindet (in Vollbild)
        self.screen_rect = self.screen.get_rect()
        self.bg_color = "grey" # Variable für Hintergrundfarbe des Blockes
        pygame.display.set_caption("Katzen RPG")# Text für die Fensterzeile

        self.clock = pygame.time.Clock() #Clock misst die Zeit und ist für die Framerate wichtig

        # Heldenkatzen:
        self.warrior_cat = Warrior(self,1100,200,"Warrior")
        self.healer_cat = Cleric (self,1150,400, "Cleric")
        self.casting_cat = Mage(self,1200,600, "Mage")

        # Gegner:
        self.boss = Necromancer(self,350,400,"The Evil Necromancer Cat")
        self.minion_1 = Poison_Minion(self,650,300, "Cat-Minion 1")
        self.minion_2 = Rage_Minion (self,650,600, "Cat-Minion 2")

        # Gruppen
        # Alle Kampfteilnehmer für den Kampf
        self.fighting_order = [self.warrior_cat, self.minion_1, self.healer_cat,self.minion_2, self.casting_cat, self.boss] 
        self.cat_heroes = [self.warrior_cat,self.casting_cat,self.healer_cat] # Gruppe für die Heldenkatzen
        self.enemys = [self.minion_1,self.minion_2,self.boss] # Gruppe für die Gegner

        # Schaltflächen:
        self.cat_box = Cat_Box(self,self.warrior_cat,self.healer_cat,self.casting_cat) # Katzennamen, HP & MP
        self.enemy_box = Enemy_Box(self,self.boss,self.minion_1,self.minion_2) # Gegnernamen
        self.action_box = Action_Box(self,self.cat_box) # Box mit den Aktionsmöglichkeiten (Angriff etc.)
        self.item_box = Item_Box(self,self.action_box)
        self.ability_box = Ability_Box(self,self.action_box)
        self.tooltip_box = Tooltp_Box(self)

        self.tooltip_message = ""

        # Für das Rundensystem
        self.turn_timer = 0
        self.current_player = self.fighting_order[self.turn_timer] # Setzt den aktuellen Spieler auf die 1. Position der Fighting-Order
        self.turn_counter = 1
        self.next_turn = False # Die Bool-Variable, die überprüft, ob die Bedingungen für eine nächste Runde gegeben ist


        self.current_target = 0 # Die int-Variable für die Auswahl des aktuellen Ziels
        # Cursor:
        # Der Cursor, der über der aktuellen Katze erscheint
        self.player_cursor = Cursor(self,self.current_player.rect.centerx - 10,self.current_player.rect.y -30)
        # Der Gegner-Auswahl Cursor, der automatisch auf den ersten Gegner steht
        self.attack_cursor = Cursor (self, self.enemys[self.current_target].rect.right +10, self.enemys[self.current_target].rect.centery -10)

        self.battle_sequencer = Action(self) # Klasse, die die gesamte Kampfabfolge (Angriffe, Schaden, Animationen) abhandelt
        self.current_action = None # In dieser Variable wird die aktuelle Kampfaktion gespeichert

        self.current_effects = pygame.sprite.Group()

        self.test_image = pygame.image.load("images/Cat-Healer.png")
        self.image_rect = self.test_image.get_rect()



    def run_game(self): # Hauptfunktion (Ereignisse checken, Bildschirm/Sprites aktualisieren)
        """Die Hauptfunktion: Sie läuft so lange, bis die while-Schleife beendet ist"""
        while True:
            self._check_events() # Überprüft, ob in diesem Frame Tasteneingaben stattfinden
            self._check_start_turn() # Überprüft, ob gerade eine neue Runde gestartet ist
            self._check_for_action() # Überprüft, ob eine Aktion ausgeführt wird
            self._check_if_alive() # Überprüft, ob alle Kampfteilnehmer noch am Leben sind
            self._check_next_turn() # Überprüft, ob die Bedingungen für eine neue Runde gegeben sind
            self._update_screen() # Aktualisiert den Bildschirm mit allen aktualisierten Werten, Positionen etc.
            self.clock.tick(60) # Aktualisiert die Uhr und legt so die Framerate fest
        
    def _update_screen(self):
        """Zeichnet der Bildschirm mit allen Spielelementen neu"""
        self.screen.fill(self.bg_color) #Füllt den Hintergrund des Spielfensters
        self._draw_game_fields() # Zeichnet die Schaltflächen 
        self._draw_charakters() # Zeichnet die Spielfiguten
        self._draw_cursor() # Zeichnet die Cursor
        self._draw_effects() # Zeichnet alle aktiven Effekte
        pygame.display.flip() # Zeichnet den Bildschirm neu
    
    def _draw_charakters(self):
        """Zeichnet die Spielfiguren"""
        pygame.draw.rect(self.screen,"red",self.warrior_cat)
        pygame.draw.rect(self.screen,"blue",self.casting_cat)
        self.screen.blit(self.healer_cat.image, (self.healer_cat.x_position,self.healer_cat.y_position))
        if self.minion_1.is_alive == True:
            pygame.draw.rect(self.screen,"green",self.minion_1)
        if self.minion_2.is_alive == True:
            pygame.draw.rect(self.screen,"purple",self.minion_2)
        if self.boss.is_alive == True:
            pygame.draw.rect(self.screen,"brown",self.boss)
        if self.current_effects:
            self.current_effects.draw(self.screen)

    def _draw_game_fields(self):
        """Zeichnet die Schaltflächen des Kampfbildschirms"""
        self.cat_box.draw_cat_box(self.current_player) # Schaltfläche mit den Namen der Katzen, sowie HP & MP
        self.enemy_box.draw_enemy_box() # Schaltflächen mit den Namen der Gegner
        if self.current_player in self.cat_heroes: # Wenn der aktuelle Kampfteilnehmer spielbar ist, wird die Action-Box gezeichnet
            self.action_box.draw_action_box(self.current_player)
        if self.item_box.active == True:
            self.item_box.draw_item_box()
        if self.ability_box.active == True:
            self.ability_box.draw_ability_box()
        self.get_tooltip()
        self.tooltip_box.draw_tooltip_box(self.tooltip_message)
        

    def _draw_cursor(self):
        """Zeichnet die Cursor und Marker auf das Spielfeld"""
        # Zeichnet den Marker für die aktuelle Spielfigur, dafür werden die Koordinaten des Cursors beim aktuellen Kampfteilnehmer gesetzt
        self.player_cursor.rect.x = self.current_player.rect.centerx - 10
        self.player_cursor.rect.y = self.current_player.rect.y -30
        pygame.draw.rect(self.screen,"black",self.player_cursor)

        # Der Cursor für das Auswählen eines Angriffsziel wird nur gezeichnet, wenn er auch aktiv ist
        if self.attack_cursor.active == True:
            self.attack_cursor.rect.x = self.enemys[self.current_target].rect.right +10
            self.attack_cursor.rect.y = self.enemys[self.current_target].rect.centery -10
            pygame.draw.rect(self.screen,"red",self.attack_cursor)
        
    def _draw_effects(self):
        """Zeichnet alle aktiven Effekte (Wenn die entsprechenden Bedingungen gegeben sind)"""
        self.battle_sequencer.draw_damage_numbers() # Zeichnet die Schadenzahlen an den Kampfteilnehmern

    def get_tooltip(self):
        """Funktion, um die Nachricht für die Tooltip-Box auszulesen"""
        if self.item_box.active == True:
            self.tooltip_message = self.item_box.current_items[self.item_box.current_position]["tooltip"]
        else:
            self.tooltip_message = ""
        

            
    
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
            if not self.current_action:
                self.current_player.action = False
                if self.attack_cursor.active == True:
                    self._create_attack_cursor()
        # Alle der folgenden Tasteneingaben sind nur möglich, wenn gerade keine Aktionssequenz abgespielt wird!
        if event.key == pygame.K_DOWN and not self.current_action:
            # Bewegung nach unten des Cursors der Action-Box (nur möglich, wenn aktueller Kämpfer spielbar und die action-box aktiv ist) 
            if self.current_player in self.cat_heroes and self.action_box.active == True:
                if self.action_box.current_position < len(self.action_box.postitions)-1:
                    self.action_box.current_position +=1
            elif self.current_player in self.cat_heroes and self.item_box.active == True:
                if self.item_box.current_position < len(self.item_box.postitions)-1:
                    self.item_box.current_position +=1
            
            # Wenn hingegen der Attack-Cursor aktiv ist, wird dieser nach unten bewegt (die Reihenfolge beginnt wieder von vorne, wenn
            # die Anzahl der möglichen Gegner überschritten wurde.)
            elif self.attack_cursor.active == True:
                self.current_target +=1
                if self.current_target > len(self.enemys) -1:
                    self.current_target = 0
        if event.key == pygame.K_UP and not self.current_action:
            # Bewegung nach oben des Cursors der Action-Box (nur möglich, wenn aktueller Kämpfer spielbar und die action-box aktiv ist)
            if self.current_player in self.cat_heroes and self.action_box.active == True:
                if self.action_box.current_position > 0:
                    self.action_box.current_position -=1
            elif self.current_player in self.cat_heroes and self.item_box.active == True:
                if self.item_box.current_position > 0:
                    self.item_box.current_position -=1
            # Wenn hingegen der Attack-Cursor aktiv ist, wird dieser nach oben bewegt (die Reihenfolge beginnt wieder von hinten, wenn
            # 0 erreicht wurde).
            elif self.attack_cursor.active == True:
                self.current_target -= 1
                if self.current_target < 0:
                    self.current_target = len(self.enemys) -1
        if event.key == pygame.K_RETURN and not self.current_action:
                if self.current_player in self.cat_heroes and self.action_box.active == True:
                    if self.action_box.current_position == 0: # Befehl, um den Angriffscursor zu aktivieren
                        self._create_attack_cursor()
                    if self.action_box.current_position == 1:
                        self.item_box.active = True
                        self.tooltip_box.active = True
                        self.action_box.active = False
                    if self.action_box.current_position == 2:
                        self.ability_box.active = True
                        self.action_box.active = False
                    # Wenn der Angriffscursor aktiviert ist und bisher noch keine aktuelle Aktion aktiv ist, wird als aktuelle Aktion
                    # eine Standardattacke festgelegt und auf das aktuelle Ziel angewendet
                elif self.attack_cursor.active == True and self.current_action == None: 
                    self.current_action = self.battle_sequencer.default_attack
                    self._create_attack_cursor() # Der Attack-cursor wird wieder deaktiviert
                    self.battle_sequencer.action_sequence_active = True # Mit dieser Boolvariable beginnt die Einleitung der Kampfsequenz
        if event.key == pygame.K_ESCAPE and not self.current_action: 
            # Falls der Angriffscursor aktiviert ist, wird er durch die Escape-Tatse wieder deaktiviert.
            if self.attack_cursor.active == True:
                self._create_attack_cursor()
                self.current_target = 0
            if self.item_box.active == True:
                self.item_box.active = False
                self.action_box.active = True
                self.item_box.current_position = 0
                self.tooltip_box.active = False
            if self.ability_box.active == True:
                self.ability_box.active = False
                self.action_box.active = True
            

    def _check_start_turn(self):
            """Überprüft, ob die Bedingung für den Start der Runde gegeben ist"""
            # Falls ja, wird ein neuer aktiver Spieler ausgewählt
            if self.next_turn == True:
                self.current_player = self.fighting_order[self.turn_timer]
                self.next_turn = False

    def _check_next_turn(self):
        """Überprüft, ob die Bedingung für den Abschluss der Runde gegeben ist"""
        # Die Runde endet, wenn der aktive Spieler keine Aktion mehr übrig hat
        if self.current_player.action == False:
            self.turn_timer +=1 # Der Rundenzähler wird um eins erhöht
            # Wenn der Rundenzähler größer ist als die aktuelle Anzahl Kampfteilnehmer, wird der 
            # Zähler wieder zurückgesetzt und die Kampfreihenfolge beginnt von vorne
            if self.turn_timer > len(self.fighting_order) -1:
                self.turn_timer = 0
                for player in self.fighting_order:
                    player.action = True
            self.turn_counter +=1
            self.action_box.current_position = 0 # Zurücksetzen der Cursor-Position für die Action-Box (Standartpos.: Attack)
            self.current_target = 0 # Zurücksetzen des Angriffscursors (Standartpos.: Erster Gegner der Gruppe)
            self.next_turn = True # Die Variable für die nächste Runde wird auf True gesetzt
    
    def _create_attack_cursor(self):
        """Erschafft den Angriffscursor"""
        if self.action_box.active == True:
            self.attack_cursor.active = True
            self.action_box.active = False
        # Falls bereits ein Angriffscursor aktiv ist, wird er durch diesen Befehl wieder deaktivert
        elif self.attack_cursor.active == True:
            self.attack_cursor.active = False
            self.action_box.active = True

    def _check_if_alive(self):
        """Überprüft, ob ein Kampfteilnehmer gestorben ist"""
        if self.battle_sequencer.damage_sequence_active == False: # Der Check findet erst statt, wenn der damage auf dem Bildschirm angezeigt wurde
            for player in self.fighting_order:
                if player.current_hp <= 0: # Wenn die aktuelle HP kleiner gleich 0 ist, wird die Lebens-Variable auf False gesetzt
                    player.is_alive = False
        # Falls ein Gegner tot ist, wird er sowohl aus der Gruppe der Kampfteilnehmer, als auch aus der Gegnergrupe gelöscht
        for enemy in self.enemys:
            if enemy.is_alive == False:
                self.enemys.remove(enemy)
                self.fighting_order.remove(enemy)
    
    def _check_for_action(self):
        """Überprüft ob eine Aktion stattfindet"""
        if self.current_action : # Diese Funktion wird erst ausgeführt, wenn eine aktuelle Aktion festgelegt ist
            # Solange die Variable für den action-sequencer wahr ist, wird die festgelegete Aktion ausgeführt
            if self.battle_sequencer.action_sequence_active == True: 
                self.current_action(self.current_player, self.enemys[self.current_target]) 
            # Wenn die Aktion beendet ist, wird Sequenz für das Anzeigen der Schadenswerte angezeigt
                if self.battle_sequencer.action_sequence_active == False:
                    self.battle_sequencer.damage_sequence_active = True
            # Zum Schluss wird der Wert für die aktuelle Aktion zurückgesetzt und der Wert für die Aktionsmöglichkeiten des aktuellen
            # Spielers auf False gesetzt. Dies führt zur Beendigung der Runde
            if self.battle_sequencer.action_sequence_active == False and self.battle_sequencer.damage_sequence_active == False:
                self.current_action = None
                self.current_player.action = False
            



    
    



if __name__ == "__main__":
    #Erstellt eine Spielinstanz und führt das Spiel aus.
    cf = Cat_Fight()
    cf.run_game()






    # Inaktiver Code

    def attack(self,cat,enemy):
        damage = cat.attack - enemy.defence
        enemy.current_hp -= damage
        print(f"{cat.name} hit {enemy.name}. Damage: {damage}.  HP: {enemy.current_hp} / {enemy.max_hp} ")
    


        


