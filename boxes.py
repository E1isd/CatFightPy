import pygame
import pygame.freetype
from cursor import Cursor
from inventory import Inventory


class Box():
    """Die Hauptklasse für die Kampfbilschirmoberflächen"""
    def __init__(self,cf_game):
        self.screen = cf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.font_freetype = pygame.freetype.SysFont(None,30) # Erschafft eine Font-Klasse mit einer bestimmten Schriftart und Schriftgröße
        self.cursor = Cursor(self,0,0) # Der Cursor für die Box 
        self.box_color = (255,182,193)
        self.border_color = (139,10,80)
        

        # Symbole für Statusveränderungen
        self.poison_symbol = pygame.transform.smoothscale(pygame.image.load("images/poison-symbol.png").convert_alpha(), (24,24))
        self.fire_symbol = pygame.transform.smoothscale(pygame.image.load("images/fire-symbol.png").convert_alpha(), (24,24))
        self.stun_symbol = pygame.transform.smoothscale(pygame.image.load("images/stun-symbol.png").convert_alpha(), (24,24))



class Cat_Box(Box):
    """Klasse für die Oberfläche mit den Lebens- und Manaleisten der Katze"""
    def __init__(self,cf_game,cat1,cat2,cat3): # Nimmt als Parameter die drei Katzen
        super().__init__(cf_game)
        self.rect = pygame.Rect(self.screen_rect.right-810 ,self.screen_rect.bottom -310,800,300) # Erschafft das Rechteck der Schaltfläche
        self.small_rect = None
        self.cats = [cat1,cat2,cat3] # Liste mit den drei Katzen

        
    def draw_cat_box(self, current_cat):
        """Zeichnet die Oberfläche der Box und schreibt den Text hinein"""
        i = 100  # Initiator für das Zeichnen der Elemente in der For-Schleife
        color = "black" # Standardfarbe des Textes
        pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10) # Zeichnet das Rechteck der Oberfläche
        pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10) # Zeichnet den Rand der Box

        # Schreibt die beiden Überschriften "HP" und "MP". Sie fungieren gleichzeit als Rechteck-Variablen, damit sich anderer Text daran
        # ausrichten können (wichtig für Textzentrierung)
        hp_line = self.font_freetype.render_to(self.screen,(self.rect.x +150, self.rect.y + 50),"HP",color,None,pygame.freetype.STYLE_UNDERLINE)
        mp_line = self.font_freetype.render_to(self.screen,(self.rect.x +350, self.rect.y + 50),"MP",color,None,pygame.freetype.STYLE_UNDERLINE)

        # For-Schleife, die die (aktuellen/maximalen) HP & MP der Katzen schreibt
        for cat in self.cats:
            # Ermittelt die Zeilengröße der Variable "current_hp". Wichtig für die korrekte Positionierung und Zentrierung, welche sich auch
            # automatisch anpasst, wenn die Zahl zwei oder ein-stellig wird.
            hp_line_spacing = self.font_freetype.get_rect(f"{cat.current_hp} ").width
            mp_line_spacing = self.font_freetype.get_rect(f"{cat.current_mp} ").width

            # Zeichnet das Statuseffekt-Symbol neben dem Namen
            x = 150
            if cat.status_effects:
                for effect in cat.status_effects:
                    if effect == "poison":
                        self.screen.blit(self.poison_symbol,(self.rect.right - x, self.rect.y + i ))
                        x -= 30
                    elif effect == "burn":
                        self.screen.blit(self.fire_symbol,(self.rect.right - x, self.rect.y + i ))
                        x -= 30
                    elif effect == "stun":
                        self.screen.blit(self.stun_symbol,(self.rect.right - x, self.rect.y + i ))
                        x -= 30                      

            if cat == current_cat:
                # Zeichnet ein kleines Rechteck um den Namen der aktuell ausgewählten Katze und ändert die Schriftfarbe des Namens
                color = (139,10,80)                             
                name_box = self.font_freetype.render_to(self.screen,(self.rect.x +500, self.rect.y + i),f"{str(cat.name)}",color)
                color = "black"
                self.small_rect = pygame.Rect(name_box.x -10,name_box.y-10, name_box.width + 20, name_box.height +20)
                pygame.draw.rect(self.screen,"white",self.small_rect,width=2,border_radius=10)

            else: 
                name_box = self.font_freetype.render_to(self.screen,(self.rect.x +500, self.rect.y + i),f"{str(cat.name)}",color)


            # Zeichnet Maximale HP & MP der Katze
            self.font_freetype.render_to(self.screen,(hp_line.centerx, self.rect.y +i),f"/ {str(cat.max_hp)}",color)
            self.font_freetype.render_to(self.screen,(mp_line.centerx, self.rect.y +i),f"/ {str(cat.max_mp)}",color)


            # Wenn HP und MP bei 25% stehen, wird die Schriftfarbe rot. Danach werden die entsprechenden Werte geschrieben.
            if cat.current_hp <= cat.max_hp * 0.25:
                color = "red"
            else:
                color = "black"
            self.font_freetype.render_to(self.screen,(hp_line.centerx - hp_line_spacing, self.rect.y +i),f"{str(cat.current_hp)}",color)

            if cat.current_mp <= cat.max_mp * 0.25:
                color = "red"
            else:
                color = "black"
            self.font_freetype.render_to(self.screen,(mp_line.centerx - mp_line_spacing, self.rect.y +i),f"{str(cat.current_mp)}",color)
    
            i +=50
            color = "black"

class Enemy_Box(Box):
    """Klasse für die Oberfläche mit den Feindnamen"""
    def __init__(self,cf_game,enemy1,enemy2,enemy3,box):
        super().__init__(cf_game)
        self.rect = pygame.Rect(self.screen_rect.left+10, self.screen_rect.bottom -310,(self.screen_rect.left+10) + (box.rect.x -30),300)
        self.enemies = [enemy1,enemy2,enemy3]
    
    # Schreibt die Gegnernamen
    def draw_enemy_box(self):
        """Schreibt die Gegnernamen und HP"""
        i = 100
        color = "black"
        pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)
        for enemy in self.enemies:
            if enemy.is_alive == True: # Schreibt den Gegnernamen und HP nur, wenn der Gegner noch nicht getötet wurde
                name_box = self.font_freetype.render_to(self.screen,(self.rect.x +50, self.rect.y +i),f"{enemy.name}","Black")
                hp_line = self.font_freetype.render_to(self.screen,(self.rect.right -150, self.rect.y + 50),"HP",color,None,pygame.freetype.STYLE_UNDERLINE)

                # HP hier als Überschrift, damit sich die HP-Werte daran ausrichten können
                hp_line_spacing = self.font_freetype.get_rect(f"{enemy.current_hp} ").width
                self.font_freetype.render_to(self.screen,(hp_line.centerx, self.rect.y +i),f"/ {str(enemy.max_hp)}","black")
                if enemy.current_hp <= enemy.max_hp * 0.25: # Wenn die HP bei 25% stehen, wird die Schriftfarbe rot. Danach werden die entsprechenden Werte geschrieben.
                    color = "red"
                else:
                    color = "black"
                self.font_freetype.render_to(self.screen,(hp_line.centerx - hp_line_spacing, self.rect.y +i),f"{str(enemy.current_hp)}",color)

                # Zeichnet ein Statuseffekt-Symbol neben dem Namen wenn nötig
                x = 20
                if enemy.status_effects:
                    for effect in enemy.status_effects:
                        if effect == "burn":
                            self.screen.blit(self.fire_symbol,(name_box.right +x,self.rect.y +i ))
                            x += 30
                        elif effect == "poison":
                            self.screen.blit(self.poison_symbol,(name_box.right +x,self.rect.y +i ))
                            x += 30
                        elif effect == "stun":
                            self.screen.blit(self.stun_symbol,(name_box.right +x,self.rect.y +i ))
                            x += 30

                i +=50

class Action_Box(Box):
    """Klasse für die Menüoberfläche mit den Aktionsmöglichkeiten des Spielers"""
    def __init__(self,cf_game,box):
        super().__init__(cf_game)
        self.active = True # Überprüft, ob die die Schaltfläche gerade aktiv ist
        self.width = 400 # Die Breite der Box
        self.rect = pygame.Rect(box.rect.x - (self.width +10), self.screen_rect.bottom -310, self.width,300) # Erschafft die Box als Gesamtheit
        # Erschafft die einzelnen Positionen als Rechtecke und speichert sie in einer Liste, so dass man sie mit dem Cursor leichter auswählen kann
        self.pos1 = pygame.Rect(self.rect.x +70, self.rect.y + 50, self.width-70,30)
        self.pos2 = pygame.Rect(self.rect.x +70, self.rect.y + 100, self.width-70,30)
        self.pos3 = pygame.Rect(self.rect.x +70, self.rect.y + 150, self.width-70,30)
        self.postitions = [self.pos1,self.pos2,self.pos3]
        self.current_position = 0 # Die aktuelle Potition
    
    def draw_action_box(self, cat):
        """Zeichnet die Action Box"""
        # Zeichnet die Aktions-Box und schreibt die einzelnen Aktionsmöglichkeiten (individuell nach Katze)
        pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)
        self.font_freetype.render_to(self.screen,self.pos1,cat.actions[0],"Black")
        self.font_freetype.render_to(self.screen,self.pos2,cat.actions[1],"Black")
        self.font_freetype.render_to(self.screen,self.pos3,cat.actions[2],"Black")

        # Zeichnet den Cursor an die erste Position der Aktionsbox
        self.cursor.rect.x = self.postitions[self.current_position].x - 50
        self.cursor.rect.y = self.postitions[self.current_position].y - 6
        if self.active == True:
            self.cursor.draw_animated_cursor(self.cursor.box_cursor_sheet,self.cursor.rect.x,self.cursor.rect.y)
        else:
            self.screen.blit(self.cursor.cursor_inactive_image, (self.cursor.rect.x,self.cursor.rect.y))
            self.cursor.current_sprite = 0
        
    
class Item_Box(Box):
    """Klasse für die Menüoberfläche der Items"""
    def __init__(self,cf_game,box):
        super().__init__(cf_game)
        self.active = False
        self.rect = pygame.Rect(self.screen_rect.left+10, self.screen_rect.bottom -310,(self.screen_rect.left+10) + (box.rect.x -30),300)
        self.current_items = []
        self.postitions = []
        self.current_position = 0
    
    def draw_item_box(self, inventory, cursor_active):
        """Zeichnet die Item-Box"""
        i = 50
        self.current_items.clear()
        self.postitions.clear()
        pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)
        for item, value in inventory.item_dict.items(): # Es wird ermittelt, welches Item im aktuellen Inventar vorhanden ist("in_stock")
            if value["in_stock"] > 0:
                self.current_items.append(value) # Items, bei denen mindestens eine Einheit vorhanden ist, landen in der current_items Liste
        if not self.current_items: # Wenn die current_items Liste leer ist, wird eine entsprechende Nachricht angezeigt
            self.font_freetype.render_to(self.screen,(self.rect.x +50, self.rect.y +50),"Out Of Items","Black")
        else: 
            for postion in self.current_items: # Schreibt alle Items aus current_items mit Name und Anzahl in die Item-Box
                pos=self.font_freetype.render_to(self.screen,(self.rect.x +100, self.rect.y +i),f"{postion['name']}","Black")
                self.postitions.append(pos) # Fügt das Rechteck des geschriebenen Items zur Positions-Liste hinzu (für dei Position des Cursors)
                self.font_freetype.render_to(self.screen,(self.rect.x +300, self.rect.y +i),f"x {postion['in_stock']}","Black")
                i+=50
            # Setzt den Cursor der Item-Box an die aktuelle Stelle und zeichnet ihn
            self.cursor.rect.x = self.postitions[self.current_position].x - 50 
            self.cursor.rect.y = self.postitions[self.current_position].y - 5
            if cursor_active == False:
                self.cursor.draw_animated_cursor(self.cursor.box_cursor_sheet,self.cursor.rect.x,self.cursor.rect.y)
            else:
                self.screen.blit(self.cursor.cursor_inactive_image, (self.cursor.rect.x,self.cursor.rect.y))
                self.cursor.current_sprite = 0
                
            

class Ability_Box(Box):
    """Klasse für die Menüoberfläche der Items"""
    def __init__(self,cf_game,box):
        super().__init__(cf_game)
        self.active = False
        self.rect = pygame.Rect(self.screen_rect.left+10, self.screen_rect.bottom -310,(self.screen_rect.left+10) + (box.rect.x -30),300)
        self.postitions = []
        self.current_position = 0

    
    def draw_ability_box(self,cat,cursor_active1,cursor_active2):
        """Zeichnet die Item-Box"""
        i = 100
        self.postitions.clear()
        color = "black"
        pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10) 
        mp_line = self.font_freetype.render_to(self.screen,(self.rect.right - 200, self.rect.y +50),f"MP Needed",color)    
        
        for ability in cat.learned_abilities: # Zeichnet alle aktuell gelernten Abilitys der Katze mitsamt den Manakosten
            # Wenn die Manakosten der Fähigkeit größer sind, als die aktuellen Manakosten der Katze, werden die MP grau dargestellt
            if ability["mp_cost"] > cat.current_mp: 
                color = "grey"
            pos=self.font_freetype.render_to(self.screen,(self.rect.x +100, self.rect.y +i),f"{ability['name']}",color)
            self.postitions.append(pos)
            text_spacing = self.font_freetype.get_rect(f"{ability['mp_cost']} ").width
            self.font_freetype.render_to(self.screen,(mp_line.centerx - (text_spacing/2), self.rect.y +i),f"{ability['mp_cost']}",color)
            i += 50
            # Setzt den Cursor der Ability-Box an die aktuelle Stelle und zeichnet ihn
        self.cursor.rect.x = self.postitions[self.current_position].x - 50 
        self.cursor.rect.y = self.postitions[self.current_position].y - 5
        if cursor_active1 == True or cursor_active2 == True:
            self.screen.blit(self.cursor.cursor_inactive_image, (self.cursor.rect.x,self.cursor.rect.y))
            self.cursor.current_sprite = 0
        else:
            self.cursor.draw_animated_cursor(self.cursor.box_cursor_sheet,self.cursor.rect.x,self.cursor.rect.y)
            
        



class Tooltip_Box(Box):
    """Klasse für die Tooltip-Box"""
    def __init__(self,cf_game):
        super().__init__(cf_game)
        self.active = False
        self.rect = pygame.Rect(self.screen_rect.left+10, self.screen_rect.top+5,self.screen_rect.width -20, 70)

    def draw_tooltip_box(self,message): # Als Parameter wird hier eine message entgegengenommen, die die variable Message der Tooltip-Box anzeigt
        "Zeichnet die Tooltip-Box, wenn benötigt"
        if self.active == True:
            # Ermittelt die Höhe und Breite der Message, damit sie zentriert angezeigt werden kann:
            message_width = self.font_freetype.get_rect(message).width
            message_height = self.font_freetype.get_rect(message).height
            pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
            pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)
            self.font_freetype.render_to(self.screen,(self.rect.centerx - message_width/2 , self.rect.centery - message_height/2),message,"Black")

class Help_Box(Box):
    "Zeichnet die Hilfs-Box, die die Steuerung anzeigt"
    def __init__(self,cf_game,box):
        super().__init__(cf_game)
        self.active = False
        self.height = 275
        self.font_freetype_small = pygame.freetype.SysFont(None,20)
        self.rect = pygame.Rect(box.right -350, self.screen_rect.centery - self.height , 350, self.height )
        self.small_rect = pygame.Rect(self.rect.right - 55, self.rect.y -55, 50,50) # Ein kleines extra Rechteck
    
    def draw_help_box(self):
            """Zeichnet die Hilfe-Box"""
            pygame.draw.rect(self.screen,self.box_color,self.small_rect,border_radius=10)
            pygame.draw.rect(self.screen,self.border_color,self.small_rect,width=3,border_radius=10)
            # Zeichnet das kleine Extra-Dreieck, egal ob die Hilfe-Box aktiv ist oder nicht:
            self.font_freetype.render_to(self.screen,(self.small_rect.centerx -9, self.small_rect.centery -10),"H","Black")
            help_length = self.font_freetype_small.get_rect("Press To Show Help").width + 5

            if self.active == True: # Zeichnet die Hilfs-Box wenn sie aktiviert ist
                self.font_freetype_small.render_to(self.screen,(self.small_rect.x - help_length, self.small_rect.bottom - 25),"Press To Hide Help","White")
                char_length = self.font_freetype_small.get_rect("UP/DOWN").width
                pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
                pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)
                self.font_freetype_small.render_to(self.screen,(self.rect.x + 40, self.rect.y + 50),"UP/DOWN:","Black")
                self.font_freetype_small.render_to(self.screen,((self.rect.x + 40) + (char_length + 30), self.rect.y + 50),"Move Cursor","Black")
                self.font_freetype_small.render_to(self.screen,(self.rect.x + 40, self.rect.y + 100),"ENTER:","Black")
                self.font_freetype_small.render_to(self.screen,((self.rect.x + 40) + (char_length + 30), self.rect.y + 100),"Choose/Action","Black")
                self.font_freetype_small.render_to(self.screen,(self.rect.x + 40, self.rect.y + 150),"ESC:","Black")
                self.font_freetype_small.render_to(self.screen,((self.rect.x + 40) + (char_length + 30), self.rect.y + 150),"Go Back","Black")
                self.font_freetype_small.render_to(self.screen,(self.rect.x + 40, self.rect.y + 200),"Q:","Black")
                self.font_freetype_small.render_to(self.screen,((self.rect.x + 40) + (char_length + 30), self.rect.y + 200),"Quit Game","Black")
            else: # Zeichnet nur einen Text, wenn die Hilfs-Box nicht aktiviert ist
                self.font_freetype_small.render_to(self.screen,(self.small_rect.x - help_length, self.small_rect.bottom - 25),"Press To Show Help","White")



        


    





