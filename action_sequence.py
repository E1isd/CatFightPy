import pygame
import pygame.freetype

class Action():
    """Klasse, die die Kampfsequenzen verwaltet, Damage kalkuliert und Animationen abpielt"""
    def __init__(self,cf_game):
        self.screen = cf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.action_sequence_active = False # Bool Variable für die aktuelle Aktions-Sequenz
        self.damage_sequence_active = False # Bool Variable für die aktuelle Schadens-Sequenz
        self.font_freetype = pygame.freetype.SysFont(None,30) # Variable für die Schrift
        self.damage_group = pygame.sprite.Group() # Gruppe für alle Kampfteilnehmer, die Schaden erlitten haben
        self.healed_group = pygame.sprite.Group() # Gruppe für alle Kampfteilnehmer, die geheilt wurden
        self.animation_group = pygame.sprite.Group() # !!! Aktuell noch inaktiv !!!
        self.x_pos = 0 # Variable für die x-Bewegung bei Animationen
        self.y_pos = 0 # Variable für die y-Bewegung bei Animationen
        self.frame = 0 # Variable für die Frames (Wichtig, um Zeit vergehen zu lassen bei Animationen)

        # Liste mit den Methoden für alle Abilitys im Spiel:
        self.all_abilities = [self.berserker_claw, self.prayer_of_lesser_healing , self.prayer_of_ressurection, self.fireball, self.whirlwind]

        self.enemy_abilities = [self.default_attack]

    #### Allgemeine Funktionen ####

    def calculate_damage_or_heal(self,target,group):
        """Funktion, die den Schaden oder den Heilwert ermittelt"""
        if group == self.damage_group:
            if target.got_damage < 0: # Wenn der Schaden kleiner als 0 ist, wird er auf 0 zurückgesetzt
                target.got_damage = 0
            target.current_hp -= target.got_damage # Der Schaden wird von den aktuellen Lebenspunkten abgezogen
            if target.current_hp < 0: # Sind aktuelle HP kleiner als 0, werden sie auf 0 gesetzt (damit keine negativen Zahlen angezeigt werden)
                target.current_hp = 0
            self.damage_group.add(target) # Das Ziel, welches Schaden genommen hat, wird zur Schadensgruppe zugefügt
        if group == self.healed_group:
            if target.is_alive: # Heilung nur, wenn das Ziel auch am Leben ist
                target.current_hp += target.got_heal
                if target.current_hp > target.max_hp: # Wenn nach der Heilung der Wert für die aktuellen HP größer ist als max_hp...
                    target.current_hp = target.max_hp # ... wird der Wert für current_hp auf max_hp gesetzt
                self.healed_group.add(target)  # Das Ziel, welches geheilt wurde, wird zur Heilungsgruppe hinzugefügt


    def draw_damage_numbers(self):
        """Funktion, die den Schaden oder Heilung als Zahlen auf alle betroffenen Ziele zeichnet"""
        if self.damage_sequence_active == True: 
                for player in self.damage_group:
                    # Ermittelt Höhe und Länge des Schriftzuges, um es möglichst zentral zu zeichnen
                    string_lenght = self.font_freetype.get_rect(f"{player.got_damage} ").width
                    string_height = self.font_freetype.get_rect(f"{player.got_damage} ").height 
                    # Zeichnet den aktuellen Schadenwert möglichst zentral auf das Ziel
                    self.font_freetype.render_to(self.screen,(player.rect.centerx - (string_lenght / 2),player.rect.centery - (string_height / 2)),\
                                                 f"{player.got_damage}", size=30+self.x_pos) 
                for player in self.healed_group:
                    # Ermittelt Höhe und Länge des Schriftzuges, um es möglichst zentral zu zeichnen
                    string_lenght = self.font_freetype.get_rect(f"{player.got_heal} ").width
                    string_height = self.font_freetype.get_rect(f"{player.got_heal} ").height 
                    # Zeichnet den aktuellen Heilungswert möglichst zentral auf das Ziel
                    self.font_freetype.render_to(self.screen,(player.rect.centerx - (string_lenght / 2),player.rect.centery - (string_height / 2)),\
                                                 f"{player.got_heal}","green", size=30+self.x_pos) 
                # Animation: Mithilfe der x_pos-Variable, die hier nicht als x-position genommen wird, sondern als Aushilfsvariable, wird die
                # Schriftgröße pro Frame verändert. Zuerst wird sie vergrößert, ab einer bestimmten Anzahl Frames dann wieder verkleinert und
                # zurück. So entsteht der Effekt eines "Aufleuchtens".             
                if self.frame <= 30:
                    self.x_pos +=0.2
                elif self.frame > 30 and self.frame< 60:
                    self.x_pos -= 0.2
                elif self.frame > 60:
                    self.x_pos +=0.2
                self.frame +=1 # Nach jedem Zeichnen, nimmt die Frame-Variable eins zu
                # Bei 100 Frames wird die Sequenz beendet und die Werte wieder auf den Anfang gesetzt, sowie die damage-Gruppe wieder geleert
                if self.frame == 100:
                    self.damage_sequence_active = False
                    self.frame = 0
                    self.x_pos = 0
                    for player in self.damage_group:
                        player.got_damage = 0
                    self.damage_group.empty()
                    self.healed_group.empty()

        
    ##### Standard Aktionen #####
    def default_attack(self,attacker,target):
        """Funktion für den Standardangriff - !Noch fehlt die Animation!"""
        target.got_damage = attacker.attack - target.defence # Ermittelt den Schaden
        self.calculate_damage_or_heal(target,self.damage_group)
        self.action_sequence_active = False # Die Aktions-Sequenz wird beendet
 
    def use(self, target, item):
        """Funktion für das Benutzen von Items"""
        # Wenn das Item zur Kategorie der Heilungsitems gehört, wird das Ziel um dem im Item-Dictonary gespeicherten Wert geheilt
        if item["action"] == "heal":
            target.got_heal = item["value"]
            self.calculate_damage_or_heal(target,self.healed_group)
            item["in_stock"] -= 1
        # Wenn das Item zur Kategorie "Cure" gehört, wird das Ziel von dem Status-effect befreit, der im Item-Dictonary gespeichert ist 
        # - Falls das Ziel diesen Status Effekt überhaupt hat
        elif item["action"] == "cure":
            if target.status_effect == item["status_effect"]:
                target.status_effect = None
            item["in_stock"] -=1
        # Wenn das Item zur Kategorie "Revive" gehört, wird das Ziel wiederbelebt und um den im Item-Dictonayry gespeicherten Wert geheilt -
        # die Heilung findet allerdings nur statt, wenn das Ziel auch wiederbelebt wurde
        elif item["action"] == "revive":
            if target.is_alive == False:
                target.is_alive = True
                target.got_heal = item["value"]
                self.calculate_damage_or_heal(target,self.healed_group)
                item["in_stock"] -=1
        self.action_sequence_active = False


    ### Krieger-Aktionen###
    def berserker_claw(self, attacker,target):
        """Methode für Berserkerklauen Angriff"""
        target.got_damage = 100 + attacker.attack - target.defence
        self.calculate_damage_or_heal(target,self.damage_group)
        self.action_sequence_active = False # Die Aktions-Sequenz wird beendet
    
    
    ### Kleriker-Aktionen###
    def prayer_of_lesser_healing(self,healer,target):
        """Methode für das Gebet zur leichten Heilung"""
        target.got_heal = int(50 + healer.magic/2)
        self.calculate_damage_or_heal(target,self.healed_group)
        self.action_sequence_active = False # Die Aktions-Sequenz wird beendet
    
    def prayer_of_ressurection(self,healer,target):
        """Methode für das Gebet zur Wiederbelebung"""
        if target.is_alive == False:
            target.is_alive = True
            target.got_heal = int(30 + healer.magic/2)
            self.calculate_damage_or_heal(target,self.healed_group)
        self.action_sequence_active = False # Die Aktions-Sequenz wird beendet


    ### Magier-Aktionen###
    def fireball(self, attacker, target):
        """Methode für Feuerball"""
        target.got_damage = 50 + attacker.magic - target.magic_defence # Ermittelt den Schaden
        self.calculate_damage_or_heal(target,self.damage_group)
        self.action_sequence_active = False # Die Aktions-Sequenz wird beendet
    
    def whirlwind(self, attacker, target_group):
        """Methode für einen Wirbelwind-Zauber gegen alle Gegner"""
        for target in target_group:
            target.got_damage = 20 + attacker.magic - target.magic_defence
            self.calculate_damage_or_heal(target,self.damage_group)
        self.action_sequence_active = False
    
    





# Inaktiver Coder
    def inactive(self):
            if self.frame == 0:
                for player in self.damage_group:
                    string_lenght = self.font_freetype.get_rect(f"{player.got_damage} ").width
                    string_height = self.font_freetype.get_rect(f"{player.got_damage} ").height
                    if player.rect.centery - (string_height / 2) + self.x_pos >= player.rect.bottom:
                        self.frame +=1
                        break
                    else:
                        self.font_freetype.render_to(self.screen,(player.rect.centerx - (string_lenght / 2),player.rect.centery - (string_height / 2) + self.x_pos),f"{player.got_damage}",None)
                        self.x_pos +=1
            elif self.frame > 0:
                for player in self.damage_group:
                    string_lenght = self.font_freetype.get_rect(f"{player.got_damage} ").width
                    string_height = self.font_freetype.get_rect(f"{player.got_damage} ").height
                    self.font_freetype.render_to(self.screen,(player.rect.centerx - (string_lenght / 2),player.rect.bottom - (string_height)),f"{player.got_damage}",None)
                    self.frame += 1
            
            if self.frame == 60:
                self.damage_sequence_active = False
                self.x_pos = 0
                self.frame = 0

