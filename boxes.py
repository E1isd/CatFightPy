import pygame
import pygame.freetype
from cursor import Cursor
from inventory import Inventory


class Box():
    """Die Hauptklasse für die Kampfbilschirmoberflächen"""
    def __init__(self,cf_game):
        self.screen = cf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.font_freetype = pygame.freetype.SysFont(None,30)
        self.cursor = Cursor(self,0,0)
        self.box_color = (255,182,193)
        self.border_color = (139,10,80)

        # Symbole für Statusveränderungen
        self.poison_symbol = pygame.transform.smoothscale(pygame.image.load("images/Symbols/Poison/poison-symbol.png").convert_alpha(), (25,25))
        self.fire_symbol = pygame.transform.smoothscale(pygame.image.load("images/Symbols/Fire/fire1-symbol.png").convert_alpha(), (25,25))
        self.stun_symbol = pygame.transform.smoothscale(pygame.image.load("images/Symbols/Stun/stun-symbol.png").convert_alpha(), (25,25))
        self.protect_symbol = pygame.transform.smoothscale(pygame.image.load("images/Symbols/Protect/protect-symbol.png").convert_alpha(), (25,25))


class Start_Box(Box):
    """Klasse für die Start Box Oberfläche"""
    def __init__(self,cf_game):
        super().__init__(cf_game)
        self.rect = pygame.Rect(self.screen_rect.centerx -500,250,1000,600)
        self.small_rect = pygame.Rect(self.screen_rect.centerx -300,self.rect.bottom + 20,600,100)
        self.font_freetype_headline = pygame.freetype.SysFont(None,120)

    def draw_start_box(self):
        pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)
        pygame.draw.rect(self.screen,self.box_color,self.small_rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.small_rect, width=3, border_radius=10)

        headline_width = self.font_freetype_headline.get_rect("Cat Fight").width
        small_text_length = self.font_freetype.get_rect("Press Return To Start").width
        small_text_height = self.font_freetype.get_rect("Press Return To Start").height

        self.font_freetype_headline.render_to(self.screen,(self.screen_rect.centerx -headline_width/2,100),"Cat Fight","black",None)
        self.font_freetype.render_to(self.screen,(self.small_rect.centerx - small_text_length/2 , self.small_rect.centery - small_text_height/2),"Press Enter To Start!","black",None)


class Cat_Box(Box):
    """Klasse für die Oberfläche mit den Lebens- und Manaleisten der Katze"""
    def __init__(self,cf_game,cat1,cat2,cat3):
        super().__init__(cf_game)
        self.rect = pygame.Rect(self.screen_rect.right-810 ,self.screen_rect.bottom -310,800,300)
        self.small_rect = None
        self.cats = [cat1,cat2,cat3]

    def draw_cat_box(self, current_cat):
        """Zeichnet die Oberfläche der Box und schreibt den Text hinein"""
        i = 100
        color = "black"
        pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)

        hp_line = self.font_freetype.render_to(self.screen,(self.rect.x +150, self.rect.y + 50),"HP",color,None,pygame.freetype.STYLE_UNDERLINE)
        mp_line = self.font_freetype.render_to(self.screen,(self.rect.x +350, self.rect.y + 50),"MP",color,None,pygame.freetype.STYLE_UNDERLINE)

        for cat in self.cats:
            hp_line_spacing = self.font_freetype.get_rect(f"{cat.current_hp} ").width
            mp_line_spacing = self.font_freetype.get_rect(f"{cat.current_mp} ").width

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
                    elif effect == "protect":
                        self.screen.blit(self.protect_symbol,(self.rect.right - x, self.rect.y + i ))
                        x -= 30

            if cat == current_cat:
                color = (139,10,80)
                name_box = self.font_freetype.render_to(self.screen,(self.rect.x +500, self.rect.y + i),f"{str(cat.name)}",color)
                color = "black"
                self.small_rect = pygame.Rect(name_box.x -10,name_box.y-10, name_box.width + 20, name_box.height +20)
                pygame.draw.rect(self.screen,"white",self.small_rect,width=2,border_radius=10)
            else:
                name_box = self.font_freetype.render_to(self.screen,(self.rect.x +500, self.rect.y + i),f"{str(cat.name)}",color)

            self.font_freetype.render_to(self.screen,(hp_line.centerx, self.rect.y +i),f"/ {str(cat.max_hp)}",color)
            self.font_freetype.render_to(self.screen,(mp_line.centerx, self.rect.y +i),f"/ {str(cat.max_mp)}",color)

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

    def draw_enemy_box(self):
        """Schreibt die Gegnernamen und HP"""
        i = 100
        color = "black"
        pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)
        for enemy in self.enemies:
            if enemy.is_alive == True:
                name_box = self.font_freetype.render_to(self.screen,(self.rect.x +50, self.rect.y +i),f"{enemy.name}","Black")
                hp_line = self.font_freetype.render_to(self.screen,(self.rect.right -150, self.rect.y + 50),"HP",color,None,pygame.freetype.STYLE_UNDERLINE)

                hp_line_spacing = self.font_freetype.get_rect(f"{enemy.current_hp} ").width
                self.font_freetype.render_to(self.screen,(hp_line.centerx, self.rect.y +i),f"/ {str(enemy.max_hp)}","black")
                if enemy.current_hp <= enemy.max_hp * 0.25:
                    color = "red"
                else:
                    color = "black"
                self.font_freetype.render_to(self.screen,(hp_line.centerx - hp_line_spacing, self.rect.y +i),f"{str(enemy.current_hp)}",color)

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
                color = "black"


class Action_Box(Box):
    """Klasse für die Menüoberfläche mit den Aktionsmöglichkeiten des Spielers"""
    def __init__(self,cf_game,box):
        super().__init__(cf_game)
        self.active = True
        self.width = 400
        self.rect = pygame.Rect(box.rect.x - (self.width +10), self.screen_rect.bottom -310, self.width,300)
        self.pos1 = pygame.Rect(self.rect.x +70, self.rect.y + 50, self.width-70,30)
        self.pos2 = pygame.Rect(self.rect.x +70, self.rect.y + 100, self.width-70,30)
        self.pos3 = pygame.Rect(self.rect.x +70, self.rect.y + 150, self.width-70,30)
        self.postitions = [self.pos1,self.pos2,self.pos3]
        self.current_position = 0

    def draw_action_box(self, cat):
        """Zeichnet die Action Box"""
        pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)
        self.font_freetype.render_to(self.screen,self.pos1,cat.actions[0],"Black")
        self.font_freetype.render_to(self.screen,self.pos2,cat.actions[1],"Black")
        self.font_freetype.render_to(self.screen,self.pos3,cat.actions[2],"Black")

        self.cursor.rect.x = self.postitions[self.current_position].x - 50
        self.cursor.rect.y = self.postitions[self.current_position].y - 6
        if self.active == True:
            self.cursor.draw_animated_cursor(self.cursor.box_cursor_sheet,self.cursor.rect.x,self.cursor.rect.y, self.cursor.cursor_sprites)
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
        for item, value in inventory.item_dict.items():
            if value["in_stock"] > 0:
                self.current_items.append(value)
        if not self.current_items:
            self.font_freetype.render_to(self.screen,(self.rect.x +50, self.rect.y +50),"Out Of Items","Black")
        else:
            for postion in self.current_items:
                pos=self.font_freetype.render_to(self.screen,(self.rect.x +100, self.rect.y +i),f"{postion['name']}","Black")
                self.postitions.append(pos)
                self.font_freetype.render_to(self.screen,(self.rect.x +300, self.rect.y +i),f"x {postion['in_stock']}","Black")
                i+=50
            self.cursor.rect.x = self.postitions[self.current_position].x - 50
            self.cursor.rect.y = self.postitions[self.current_position].y - 5
            if cursor_active == False:
                self.cursor.draw_animated_cursor(self.cursor.box_cursor_sheet,self.cursor.rect.x,self.cursor.rect.y, self.cursor.cursor_sprites)
            else:
                self.screen.blit(self.cursor.cursor_inactive_image, (self.cursor.rect.x,self.cursor.rect.y))
                self.cursor.current_sprite = 0


class Ability_Box(Box):
    """Klasse für die Menüoberfläche der Abilitys"""
    def __init__(self,cf_game,box):
        super().__init__(cf_game)
        self.active = False
        self.rect = pygame.Rect(self.screen_rect.left+10, self.screen_rect.bottom -310,(self.screen_rect.left+10) + (box.rect.x -30),300)
        self.postitions = []
        self.current_position = 0

    def draw_ability_box(self,cat,cursor_active1,cursor_active2):
        """Zeichnet die Ability-Box"""
        i = 100
        self.postitions.clear()
        color = "black"
        pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)
        mp_line = self.font_freetype.render_to(self.screen,(self.rect.right - 200, self.rect.y +50),f"MP Needed",color)

        for ability in cat.learned_abilities:
            if ability["mp_cost"] > cat.current_mp:
                color = "grey"
            pos=self.font_freetype.render_to(self.screen,(self.rect.x +100, self.rect.y +i),f"{ability['name']}",color)
            self.postitions.append(pos)
            text_spacing = self.font_freetype.get_rect(f"{ability['mp_cost']} ").width
            self.font_freetype.render_to(self.screen,(mp_line.centerx - (text_spacing/2), self.rect.y +i),f"{ability['mp_cost']}",color)
            i += 50
        self.cursor.rect.x = self.postitions[self.current_position].x - 50
        self.cursor.rect.y = self.postitions[self.current_position].y - 5
        if cursor_active1 == True or cursor_active2 == True:
            self.screen.blit(self.cursor.cursor_inactive_image, (self.cursor.rect.x,self.cursor.rect.y))
            self.cursor.current_sprite = 0
        else:
            self.cursor.draw_animated_cursor(self.cursor.box_cursor_sheet,self.cursor.rect.x,self.cursor.rect.y, self.cursor.cursor_sprites)


class Tooltip_Box(Box):
    """Klasse für die Tooltip-Box"""
    def __init__(self,cf_game):
        super().__init__(cf_game)
        self.active = False
        self.rect = pygame.Rect(self.screen_rect.left+10, self.screen_rect.top+5,self.screen_rect.width -20, 70)

    def draw_tooltip_box(self,message):
        "Zeichnet die Tooltip-Box, wenn benötigt"
        if self.active == True:
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
        self.height = 340  # Increased from 275 to fit the new mouse control lines
        self.font_freetype_small = pygame.freetype.SysFont(None,20)
        self.rect = pygame.Rect(box.right -350, self.screen_rect.centery - self.height , 350, self.height )
        self.small_rect = pygame.Rect(self.rect.right - 55, self.rect.y -55, 50,50)

    def draw_help_box(self):
        """Zeichnet die Hilfe-Box"""
        pygame.draw.rect(self.screen,self.box_color,self.small_rect,border_radius=10)
        pygame.draw.rect(self.screen,self.border_color,self.small_rect,width=3,border_radius=10)
        self.font_freetype.render_to(self.screen,(self.small_rect.centerx -9, self.small_rect.centery -10),"H","Black")
        help_length = self.font_freetype_small.get_rect("Press To Show Help").width + 5

        if self.active == True:
            self.font_freetype_small.render_to(self.screen,(self.small_rect.x - help_length, self.small_rect.bottom - 25),"Press To Hide Help","White")
            char_length = self.font_freetype_small.get_rect("UP/DOWN").width
            pygame.draw.rect(self.screen,self.box_color,self.rect,border_radius=10)
            pygame.draw.rect(self.screen,self.border_color,self.rect, width=3, border_radius=10)
            # Keyboard controls
            self.font_freetype_small.render_to(self.screen,(self.rect.x + 40, self.rect.y + 50),"UP/DOWN:","Black")
            self.font_freetype_small.render_to(self.screen,((self.rect.x + 40) + (char_length + 30), self.rect.y + 50),"Move Cursor","Black")
            self.font_freetype_small.render_to(self.screen,(self.rect.x + 40, self.rect.y + 100),"ENTER:","Black")
            self.font_freetype_small.render_to(self.screen,((self.rect.x + 40) + (char_length + 30), self.rect.y + 100),"Choose/Action","Black")
            self.font_freetype_small.render_to(self.screen,(self.rect.x + 40, self.rect.y + 150),"ESC:","Black")
            self.font_freetype_small.render_to(self.screen,((self.rect.x + 40) + (char_length + 30), self.rect.y + 150),"Go Back","Black")
            self.font_freetype_small.render_to(self.screen,(self.rect.x + 40, self.rect.y + 200),"Q:","Black")
            self.font_freetype_small.render_to(self.screen,((self.rect.x + 40) + (char_length + 30), self.rect.y + 200),"Quit Game","Black")
            # NEW: Mouse controls
            self.font_freetype_small.render_to(self.screen,(self.rect.x + 40, self.rect.y + 250),"L-CLICK:","Black")
            self.font_freetype_small.render_to(self.screen,((self.rect.x + 40) + (char_length + 30), self.rect.y + 250),"Choose/Action","Black")
            self.font_freetype_small.render_to(self.screen,(self.rect.x + 40, self.rect.y + 300),"R-CLICK:","Black")
            self.font_freetype_small.render_to(self.screen,((self.rect.x + 40) + (char_length + 30), self.rect.y + 300),"Go Back","Black")
        else:
            self.font_freetype_small.render_to(self.screen,(self.small_rect.x - help_length, self.small_rect.bottom - 25),"Press To Show Help","White")
