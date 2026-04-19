import pygame
import pygame.freetype
from cursor import Cursor


class Box():
    """Die Hauptklasse für die Kampfbilschirmoberflächen"""
    def __init__(self,cf_game):
        self.screen = cf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.font_freetype = pygame.freetype.SysFont(None,30) # Erschafft eine Font-Klasse mit einer bestimmten Schriftart und Schriftgröße
        self.cursor = Cursor(self,0,0) # Der Cursor für die Box 



class Cat_Box(Box):
    """Klasse für die Oberfläche mit den Lebens- und Manaleisten der Katze"""
    def __init__(self,cf_game,cat1,cat2,cat3): # Nimmt als Parameter die drei Katzen
        super().__init__(cf_game)
        self.rect = pygame.Rect(self.screen_rect.bottom ,self.screen_rect.bottom -310,800,300) # Erschafft das Rechteck der Schaltfläche
        self.cats = [cat1,cat2,cat3] # Liste mit den drei Katzen

        
    def draw_cat_box(self, current_cat):
        """Zeichnet die Oberfläche der Box und schreibt den Text hinein"""
        i = 100  # Initiator für das Zeichnen der Elemente in der For-Schleife
        color = "black" # Standardfarbe des Textes
        pygame.draw.rect(self.screen,"white",self.rect,border_radius=10) # Zeichnet das Rechteck der Oberfläche

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

            # Schreibt Namen der Katze und falls es die aktuell aktive Katze ist, wird auch der Cursor an dem entsprechenden Namen gezeichnet
            name_box = self.font_freetype.render_to(self.screen,(self.rect.x +550, self.rect.y + i),f"{str(cat.name)}",color)

            if cat == current_cat:
                self.cursor.rect.x = name_box.x -50
                self.cursor.rect.y = name_box.y
                pygame.draw.rect(self.screen,"black",self.cursor)

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

class Enemy_Box(Box):
    """Klasse für die Oberfläche mit den Feindnamen"""
    def __init__(self,cf_game,enemy1,enemy2,enemy3):
        super().__init__(cf_game)
        self.rect = pygame.Rect(self.screen_rect.left+10, self.screen_rect.bottom -310,650,300)
        self.enemies = [enemy1,enemy2,enemy3]
    
    # Schreibt die Gegnernamen
    def draw_enemy_box(self):
        i = 100
        pygame.draw.rect(self.screen,"white",self.rect,border_radius=10)
        hp_line = self.font_freetype.render_to(self.screen,(self.rect.x +500, self.rect.y + 50),"HP","black",None,pygame.freetype.STYLE_UNDERLINE) # Zeichnet die Überschrift "HP" und speichert sie als Variable, damit sich anderer Text daran ausrichten können (wichtig für Textzentrierung)
        for enemy in self.enemies:
            if enemy.is_alive == True: # Schreibt den Gegnernamen und HP nur, wenn der Gegner noch nicht getötet wurde
                self.font_freetype.render_to(self.screen,(self.rect.x +50, self.rect.y +i),f"{enemy.name}","Black")
                # HP hier als Überschrift, damit sich die HP-Werte daran ausrichten können
                hp_line_spacing = self.font_freetype.get_rect(f"{enemy.current_hp} ").width
                self.font_freetype.render_to(self.screen,(hp_line.centerx, self.rect.y +i),f"/ {str(enemy.max_hp)}","black")
                if enemy.current_hp <= enemy.max_hp * 0.25: # Wenn die HP bei 25% stehen, wird die Schriftfarbe rot. Danach werden die entsprechenden Werte geschrieben.
                    color = "red"
                else:
                    color = "black"
                self.font_freetype.render_to(self.screen,(hp_line.centerx - hp_line_spacing, self.rect.y +i),f"{str(enemy.current_hp)}",color)
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
        self.current_position = 0 # Die aktuelle 
    
    def draw_action_box(self, cat):
        """Zeichnet die Action Box"""
        # Zeichnet die Aktions-Box und schreibt die einzelnen Aktionsmöglichkeiten (individuell nach Katze)
        pygame.draw.rect(self.screen,"white",self.rect,border_radius=10)
        self.font_freetype.render_to(self.screen,self.pos1,cat.actions[0],"Black")
        self.font_freetype.render_to(self.screen,self.pos2,cat.actions[1],"Black")
        self.font_freetype.render_to(self.screen,self.pos3,cat.actions[2],"Black")

        # Zeichnet den Cursor an die erste Position der Aktionsbox
        self.cursor.rect.x = self.postitions[self.current_position].x - 50
        self.cursor.rect.y = self.postitions[self.current_position].y
        pygame.draw.rect(self.screen,"black",self.cursor)


        


    





