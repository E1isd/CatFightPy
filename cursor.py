import pygame

class Cursor():
    """Die Klasse für den Spielcursor"""
    def __init__(self,cf_game,x,y):
        self.screen = cf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.rect = pygame.Rect(x,y,20,20)
        self.target_group = []
        self.active = False # Bool-Variable ob der Cursor aktiv (also steuerbar) ist


 # Momentan inaktiv wegen Fehler
    def draw_cursor(self):
        pygame.draw.rect = (self.screen,"red", self.rect)
        
