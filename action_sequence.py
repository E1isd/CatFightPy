import pygame
import pygame.freetype
from effects import Effects

class Action():
    """Klasse, die die Kampfsequenzen und Methoden zu den Abilitys verwaltet, sowie Damage kalkuliert und Animationen abspielt"""
    def __init__(self,cf_game):
        self.screen = cf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.action_sequence_active = False # Bool Variable für die aktuelle Aktions-Sequenz
        self.enemy_attack_delay = 1500 # 1.5 Sekunden Wartezeit für Gegner-Angriffe
        self.enemy_attack_timer = 0 # Timer für Gegner-Angriffe
        self.enemy_attack_ready = False # Flag, ob der Gegner-Angriff bereit ist
        self.damage_sequence_active = False # Bool Variable für die aktuelle Schadens-Sequenz
        self.font_freetype = pygame.freetype.SysFont(None,30) # Variable für die Schrift
        self.font_color = None
        self.damage_group = pygame.sprite.Group() # Gruppe für alle Kampfteilnehmer, die Schaden erlitten haben
        self.healed_group = pygame.sprite.Group() # Gruppe für alle Kampfteilnehmer, die geheilt wurden
        self.animation_group = pygame.sprite.Group() # !!! Aktuell noch inaktiv !!!
        self.x_pos = 0 # Variable für die x-Bewegung bei Animationen
        self.y_pos = 0 # Variable für die y-Bewegung bei Animationen
        self.frame = 0 # Variable für die Frames (Wichtig, um Zeit vergehen zu lassen bei Animationen)
        
        self.effects = Effects()

        self.i_effect = 0

        self.effect_timer = 0
        self.effect_delay = 200
        self.effect_frame = 1
        self.effect_animation_active = False
        self.effect_animation_complete = False
        self.current_effect_dict = {}
        self.effect_x = 0
        self.effect_y = 0
        self.effect_image = ""

        self.cat_animation_active = False
        self.cat_animation_complete = False
        self.cat_timer = 0
        self.cat_delay = 200
        self.cat_frame = 1
        self.current_cat_dict = {}
        self.i_cat = 0

        self.message = ""



        # Liste mit den Methoden für alle Abilitys im Spiel:
        self.all_abilities = [self.berserker_claw, self.prayer_of_lesser_healing , self.prayer_of_ressurection, self.fireball, self.whirlwind]

        self.enemy_abilities = [self.default_attack,self.poison_claw]

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


    def draw_damage_numbers(self, font_color = None):
        """Funktion, die den Schaden oder Heilung als Zahlen auf alle betroffenen Ziele zeichnet"""
        if self.damage_sequence_active == True: 
                for player in self.damage_group:
                    # Ermittelt Höhe und Länge des Schriftzuges, um es möglichst zentral zu zeichnen
                    string_lenght = self.font_freetype.get_rect(f"{player.got_damage} ").width
                    string_height = self.font_freetype.get_rect(f"{player.got_damage} ").height 
                    # Zeichnet den aktuellen Schadenwert möglichst zentral auf das Ziel
                    self.font_freetype.render_to(self.screen,(player.rect.centerx - (string_lenght / 2),player.rect.centery - (string_height / 2)),\
                                                 f"{player.got_damage}",font_color, size=30+self.x_pos) 
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
                    for player in self.healed_group:
                        player.got_heal = 0
                    self.damage_group.empty()
                    self.healed_group.empty()
        
    def status_effects(self, player):
        """Methode für die Abhandlung aller Statuseffekte"""
        if player.status_effect == "poison":
            player.got_damage = 15
            self.calculate_damage_or_heal(player,self.damage_group)
            self.font_color = "purple"
            self.message = f"{player.name} is poisoned."
        if player.status_effect == "burn":
            player.got_damage = 30
            self.calculate_damage_or_heal(player,self.damage_group)
            self.font_color = "red"
            self.message = f"{player.name} is burning."

    
    def draw_simple_effect(self):
        if self.effect_animation_active == True:
            self.screen.blit(self.effect_image,(self.effect_x,self.effect_y),(0 + self.i_effect,0,self.current_effect_dict["size"] * self.current_effect_dict["scale"] ,self.current_effect_dict["size"] * self.current_effect_dict["scale"]))
            current_time = pygame.time.get_ticks()
            if (current_time - self.effect_timer) >= self.effect_delay:
                self.effect_timer = current_time
                self.i_effect += self.current_effect_dict["size"] * self.current_effect_dict["scale"]
                self.effect_frame += 1
                if self.effect_frame > self.current_effect_dict["frames"]:
                    self.i_effect = 0
                    self.effect_frame = 0
                    self.effect_animation_active = False
                    self.effect_animation_complete = True
    
    def draw_cat_action_animation(self,cat):
        if self.cat_animation_active == True:
            self.screen.blit(cat.image,(cat.x_position,cat.y_position),(0 + self.i_cat,0,self.current_cat_dict["size"] * self.current_cat_dict["scale"] ,self.current_cat_dict["size"] * self.current_cat_dict["scale"]))
            current_time = pygame.time.get_ticks()
            if (current_time - self.cat_timer) >= self.cat_delay:
                self.cat_timer = current_time
                self.i_cat += self.current_cat_dict["size"] * self.current_cat_dict["scale"]
                self.cat_frame += 1
                if self.cat_frame >= self.current_cat_dict["frames"]:
                    if self.current_cat_dict["wait"] == True:
                        if not self.effect_animation_complete:
                            self.i_cat = (self.current_cat_dict["size"] * self.current_cat_dict["scale"]) * (self.current_cat_dict["frames"] - 1)
                        else:
                            self.cat_animation_complete = True
                    else:
                        self.cat_animation_complete = True
            if self.cat_animation_complete == True:
                    self.i_cat = 0
                    self.cat_frame = 0
                    cat.image = cat.image_default
                    self.cat_animation_active = False









        


            



        
    ##### Standard Aktionen #####
    def default_attack(self,attacker,target):
        """Funktion für den Standardangriff - !Noch fehlt die Animation!"""
        target.got_damage = attacker.attack - target.defence # Ermittelt den Schaden
        self.calculate_damage_or_heal(target,self.damage_group)
        self.enemy_attack_ready = False # Reset des Flags nach dem Angriff
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
        if not self.cat_animation_active and not self.effect_animation_active and not self.cat_animation_complete and not self.effect_animation_complete:
            self.cat_animation_active = True
            self.current_effect_dict = self.effects.dict_p_of_res
            self.effect_image = pygame.transform.scale_by(pygame.image.load(self.current_effect_dict["image"]).convert_alpha(),self.current_effect_dict["scale"])
            self.effect_x = target.rect.x -50
            self.effect_y = target.rect.y -110
            self.current_cat_dict = self.effects.dict_cleric_pray
            healer.image = pygame.transform.scale_by(pygame.image.load(self.current_cat_dict["image"]).convert_alpha(),self.current_cat_dict["scale"])
        if self.cat_animation_active == True and not self.effect_animation_active and self.cat_frame == self.current_cat_dict["effect_start"]:
            print(self.cat_frame)
            self.effect_animation_active = True
        if self.cat_animation_complete == True and self.effect_animation_complete == True: 
            if target.is_alive == False:
                target.is_alive = True
                target.got_heal = int(30 + healer.magic/2)
                self.calculate_damage_or_heal(target,self.healed_group)
            self.effect_animation_complete = False
            self.cat_animation_complete = False
            self.action_sequence_active = False # Die Aktions-Sequenz wird beendet
            


    ### Magier-Aktionen###
    def fireball(self, attacker, target):
        """Methode für Feuerball"""
        target.got_damage = 50 + attacker.magic - target.magic_defence # Ermittelt den Schaden
        self.calculate_damage_or_heal(target,self.damage_group)
        self.action_sequence_active = False # Die Aktions-Sequenz wird beendet
        if target.status_effect != "burn":
            target.status_effect = "burn"
    
    def whirlwind(self, attacker, target_group):
        """Methode für einen Wirbelwind-Zauber gegen alle Gegner"""
        for target in target_group:
            target.got_damage = 20 + attacker.magic - target.magic_defence
            self.calculate_damage_or_heal(target,self.damage_group)
        self.action_sequence_active = False



    ### Gegner-Aktionen ###
    def poison_claw(self,attacker,target):
        """Methode für Vergiftungskrale"""
        target.got_damage = target.got_damage = attacker.attack -20 - target.defence
        self.calculate_damage_or_heal(target,self.damage_group)
        if target.status_effect != "poison":
            target.status_effect = "poison"
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

