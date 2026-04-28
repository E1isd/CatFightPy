import pygame
from pygame.sprite import Sprite
from ability import Ability

class Enemy(Sprite):
    """Überklasse für die Gegner"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__()
        self.screen = ct_game.screen
        self.x_position = start_x
        self.y_position = start_y
        self.name = name
        self.action = 1
        self.got_damage = 0
        self.is_alive = True
        self.abilities = Ability()


class Necromancer(Enemy):
    """Klasse für den Hauptboss"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.rect = pygame.Rect(self.x_position, self.y_position, 200,200)
        self.max_hp = 1500
        self.current_hp = 1500
        self.mp = 3000
        self.defence = 50
        self.attack = 200
        self.magic = 300
        self.magic_defence = 50

        self.available_skills = [self.abilities.simple_attack]

class Poison_Minion(Enemy):
    """Klasse für Minion 1"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.max_hp = 500
        self.current_hp = 500
        self.mp = 500
        self.defence = 40
        self.attack = 100
        self.magic = 300
        self.magic_defence = 50
        self.available_skills = [self.abilities.simple_attack]

class Rage_Minion(Enemy):
    """Klasse für Minion 2"""
    def __init__(self,ct_game,start_x,start_y,name):
        super().__init__(ct_game,start_x,start_y,name)
        self.rect = pygame.Rect(self.x_position, self.y_position, 100,100)
        self.max_hp = 500
        self.current_hp = 500
        self.mp = 500
        self.defence = 40
        self.attack = 300
        self.magic = 100
        self.magic_defence = 50
        self.available_skills = [self.abilities.simple_attack]
