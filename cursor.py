import pygame

class Cursor():
    """Die Klasse für den Spielcursor"""
    def __init__(self,cf_game,x,y):
        self.screen = cf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.cursor_frame_width = 16
        self.cursor_frame_height = 16
        self.rect = pygame.Rect(x, y, self.cursor_frame_width, self.cursor_frame_height)
        self.active = False # Bool-Variable ob der Cursor aktiv (also steuerbar) ist

        # Animationssheets für die einzelnen Cursor
        self.current_player_sheet = pygame.image.load("images/Cursor/current-player-cursor-sheet.png").convert_alpha() # Spielerauswahl
        self.box_cursor_sheet = pygame.image.load("images/Cursor/box-active-sheet.png").convert_alpha() # Auswahlcursor in den Boxen
        self.attack_sheet = pygame.image.load("images/Cursor/attack-sheet.png").convert_alpha() # Angriffscursor
        self.heal_sheet = pygame.image.load("images/Cursor/heal-sheet.png").convert_alpha() # Heilcursor

        self.cursor_inactive_image = pygame.image.load("images/Cursor/cursor-inactive.png").convert_alpha() # Bild für inaktiven Cursor
        self.cursor_sprites = self.make_cursor_sprites(self.box_cursor_sheet)
        self.cursor_sprites_short = self.make_cursor_sprites(self.current_player_sheet)
        self.attack_sprites = self.make_cursor_sprites(self.attack_sheet)
        self.heal_sprites = self.make_cursor_sprites(self.heal_sheet)
        self.current_sprite = 0 # Variable für den aktuellen Sprite des Animations-Sheet
        self.animation_timer = 0 # Timer für die Animation
        self.animation_delay = 200 # Variable für die Zeit bis zum nächsten Animationsframe (in ms)

    def draw_animated_cursor(self,cursor,x,y,sprite_sheet):
        """Methode, die den animierten Cursor zeichnet"""
        self.screen.blit(cursor,(x,y),sprite_sheet[self.current_sprite])
        current_time = pygame.time.get_ticks()
        if (current_time - self.animation_timer) >= self.animation_delay:
            self.animation_timer = current_time
            self.current_sprite += 1
            # Ist die Animation durchgelaufen, wird sie wiederholt:
            if self.current_sprite >= len(sprite_sheet):
                self.current_sprite = 0

    def make_cursor_sprites(self, sheet):
        """Erzeugt eine Sprite-Liste für ein Cursor-Sheet basierend auf der Bildbreite."""
        frames = []
        frame_count = sheet.get_width() // self.cursor_frame_width
        for i in range(frame_count):
            frames.append((i * self.cursor_frame_width, 0, self.cursor_frame_width, self.cursor_frame_height))
        return frames

    # TODO: 
    # 1. Cursor-Animation hat momentan den Fehler, das der Cursor zwischendurch einfach verschwindet, bevor die Animation von vorne beginnt. 
    # Das liegt wahrscheinlich daran, das die Sprite-Koordinaten nicht korrekt sind. Muss ich nochmal überprüfen. 
    # 2. Die Cursor müssen noch etwas skalliert werden, damit sie besser sichtbar sind. Und ein Stück verschoben werden, da sie momentan etwas off sind.
    # 3. Das der Cursor verschindet, kann daran liegen, das die cursor sheets unterschiedliche Anzahl von Frames haben. Muss ich auch nochmal überprüfen.

    # Momentan inaktiv wegen Fehlern
    def draw_cursor(self):
        pygame.draw.rect = (self.screen,"red", self.rect)
        
