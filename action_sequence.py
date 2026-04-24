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
        self.animation_group = pygame.sprite.Group()
        self.x_pos = 0 # Variable für die x-Bewegung bei Animationen
        self.y_pos = 0 # Variable für die y-Bewegung bei Animationen
        self.frame = 0 # Variable für die Frames (Wichtig, um Zeit vergehen zu lassen bei Animationen)


    def default_attack(self,attacker,target):
        """Funktion für den Standardangriff - !Noch fehlt die Animation!"""
        target.got_damage = attacker.attack - target.defence # Ermittelt den Schaden
        self.calculate_damage_or_heal(target,self.damage_group)
        self.action_sequence_active = False # Die Aktions-Sequenz wird beendet
 
    def use(self, target, item):
        """Funktion für das Benutzen von Items"""
        if item["action"] == "heal":
            target.got_heal = item["value"]
            self.calculate_damage_or_heal(target,self.healed_group)
            item["in_stock"] -= 1
        elif item["action"] == "cure":
            if target.status_effect == "poison":
                target.status_effect = None
            item["in_stock"] -=1
        elif item["action"] == "revive":
            if target.is_alive == False:
                target.is_alive = True
                target.got_heal = item["value"]
                self.calculate_damage_or_heal(target,self.healed_group)
                item["in_stock"] -=1
        self.action_sequence_active = False

    def calculate_damage_or_heal(self,target,group):
        """Funktion, die den Schaden ermittelt"""
        if group == self.damage_group:
            if target.got_damage < 0: # Wenn der Schaden kleiner als 0 ist, wird er auf 0 zurückgesetzt
                target.got_damage = 0
            target.current_hp -= target.got_damage # Der Schaden wird von den aktuellen Lebenspunkten abgezogen
            self.damage_group.add(target) # Das Ziel, welches Schaden genommen hat, wird zur Schadensgruppe zugefügt
        if group == self.healed_group:
            if target.is_alive:
                target.current_hp += target.got_heal
                if target.current_hp > target.max_hp:
                    target.current_hp = target.max_hp
                self.healed_group.add(target)


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

    def show_damage(self,group):
        """Animation, die den Schaden anzeigt"""
        if self.damage_sequence_active == True and not self.damage_group:
            for player in group:
                if player.got_damage > 0:
                    self.damage_group.add(player)
                    print(f"{player} added")
        self.x_pos +=1
        self.frame +=1
        for player in group:
            if player.rect.y >= player.rect.bottom:
                self.damage_sequence_active = False
                break