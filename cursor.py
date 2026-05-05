import pygame

class Cursor():
    """Die Klasse für den Spielcursor"""
    def __init__(self,cf_game,x,y):
        self.screen = cf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.rect = pygame.Rect(x,y,20,20)
        self.active = False # Bool-Variable ob der Cursor aktiv (also steuerbar) ist

        # Animationssheets für die einzelnen Cursor
        self.current_player_sheet = pygame.image.load("images/Cursor/current-player-cursor-sheet.png").convert_alpha() # Spielerauswahl
        self.box_cursor_sheet = pygame.image.load("images/Cursor/box-active-sheet.png").convert_alpha() # Auswahlcursor in den Boxen
        self.attack_sheet = pygame.image.load("images/Cursor/attack-sheet.png").convert_alpha() # Angriffscursor
        self.heal_sheet = pygame.image.load("images/Cursor/heal-sheet.png").convert_alpha() # Heilcursor

        self.cursor_inactive_image = pygame.image.load("images/Cursor/cursor-inactive.png").convert_alpha() # Bild für inaktiven Cursor
        self.cursor_sprites = [(0,0,32,32),(32,0,32,32),(64,0,32,32),(96,0,32,32)] # Koordinaten für die Teilbereiche der Cursor-Sheets         
        self.current_sprite = 0 # Variable für den aktuellen Sprite des Animations-Sheets
        self.animation_timer = 0 # Timer für die Animation
        self.animation_delay = 275 # Variable für die Zeit bis zum nächsten Animationsframe (in ms)

    def draw_animated_cursor(self,cursor,x,y):
        """Methode, die den animierten Cursor zeichnet"""
        self.screen.blit(cursor,(x,y),self.cursor_sprites[self.current_sprite])
        current_time = pygame.time.get_ticks()
        if (current_time - self.animation_timer) >= self.animation_delay:
            self.animation_timer = current_time
            self.current_sprite += 1
            # Ist die Animation durchgelaufen, wird sie wiederholt:
            if self.current_sprite >= len(self.cursor_sprites):
                self.current_sprite = 0






 # Momentan inaktiv wegen Fehler
    def draw_cursor(self):
        pygame.draw.rect = (self.screen,"red", self.rect)
        
