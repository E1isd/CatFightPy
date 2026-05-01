import pygame

class Cursor():
    """Die Klasse für den Spielcursor"""
    def __init__(self,cf_game,x,y):
        self.screen = cf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.rect = pygame.Rect(x,y,20,20)
        self.active = False # Bool-Variable ob der Cursor aktiv (also steuerbar) ist

        self.current_player_image = pygame.image.load("images/Cursor/current-player-cursor.png").convert_alpha()
        self.box_cursor_image = pygame.image.load("images/Cursor/box-active.png").convert_alpha()
        self.cursor_inactive_image = pygame.image.load("images/Cursor/cursor-inactive.png").convert_alpha()
        self.attack_cursor_image = pygame.image.load("images/Cursor/attack-cursor.png").convert_alpha()
        self.heal_cursor_image = pygame.image.load("images/Cursor/heal-cursor.png").convert_alpha()


 # Momentan inaktiv wegen Fehler
    def draw_cursor(self):
        pygame.draw.rect = (self.screen,"red", self.rect)
        
