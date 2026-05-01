import pygame

class Cursor():
    """Die Klasse für den Spielcursor"""
    def __init__(self,cf_game,x,y):
        self.screen = cf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.rect = pygame.Rect(x,y,20,20)
        self.active = False # Bool-Variable ob der Cursor aktiv (also steuerbar) ist

        self.current_player_image = pygame.image.load("images/Cursor/current-player-cursor.png").convert_alpha()
        self.cursor_inactive_image = pygame.image.load("images/Cursor/cursor-inactive.png").convert_alpha()
        self.box_cursor_sheet = pygame.image.load("images/Cursor/box-active-sheet.png").convert_alpha()
        self.attack_sheet = pygame.image.load("images/Cursor/attack-sheet.png").convert_alpha()
        self.heal_sheet = pygame.image.load("images/Cursor/heal-sheet.png").convert_alpha()
        self.cursor_sprites = [(0,0,32,32),(32,0,32,32),(64,0,32,32),(96,0,32,32)]
        self.current_sprite = 0
        self.animation_timer = 0
        self.animation_delay = 275

    def draw_animated_cursor(self,cursor,x,y):
        self.screen.blit(cursor,(x,y),self.cursor_sprites[self.current_sprite])
        current_time = pygame.time.get_ticks()
        if (current_time - self.animation_timer) >= self.animation_delay:
            self.animation_timer = current_time
            self.current_sprite += 1
            if self.current_sprite >= len(self.cursor_sprites):
                self.current_sprite = 0






 # Momentan inaktiv wegen Fehler
    def draw_cursor(self):
        pygame.draw.rect = (self.screen,"red", self.rect)
        
