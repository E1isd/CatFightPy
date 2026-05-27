import os
import ctypes
import sys
import random
from random import choice

# ==============================================================================
# MODULE-LEVEL COMMENTS
# ==============================================================================
# Remove a forced dummy audio driver setting if it was set externally.
# Prevents SDL from using a silent dummy driver when a real one is available.

if os.getenv("SDL_AUDIODRIVER", "").lower() == "dummy":
    del os.environ["SDL_AUDIODRIVER"]
    
import pygame
from cats import *  # noqa: F403
from enemys import *
from boxes import *
from cursor import Cursor
from action_sequence import Action


# ==============================================================================
# CLASS: Cat_Fight
# ==============================================================================
# The main game class. Handles initialization, the game loop, rendering,
# input events, turn management, and battle logic.
# ==============================================================================

class Cat_Fight:

    def __init__(self):
        # ----------------------------------------------------------------------
        # DPI / DISPLAY SETUP
        # This line prevents Windows from applying display scaling to the game.
        # Without it, the 1920x1080 resolution could result in blurry graphics
        # and fonts due to OS-level DPI scaling.
        # ----------------------------------------------------------------------
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except AttributeError:
            pass 

        # Pre-initialize the mixer with low buffer values to reduce audio latency,
        # which is important for synchronizing sounds with animations.
        pygame.mixer.pre_init(44100, -16, 2, 512)
        # Initialize all pygame modules so they can be used in the game.
        pygame.init()

        # The icon shown in the title bar and task manager.
        icon = pygame.image.load("images/Icon/Icon.ico")
        pygame.display.set_icon(icon)
        
        # ----------------------------------------------------------------------
        # AUDIO SETUP
        # If audio cannot be loaded, a warning is printed and the game starts
        # without sound instead of crashing.
        # ----------------------------------------------------------------------
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            music_path = os.path.join("audio", "background", "BackgroundMusic.mp3")
            if not os.path.isfile(music_path):
                raise FileNotFoundError(f"Music file not found: {music_path}")
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # Play the track on an infinite loop.
            pygame.mixer.music.set_volume(0.5)  # 50% volume.
        except Exception as e:
            print("Warning: Audio could not be started. Game will run without sound.")
            print("Audio error:", e)

        # ----------------------------------------------------------------------
        # SCREEN SETUP
        # First attempts fullscreen so the game looks correct on different
        # screen sizes. Falls back to a regular window if fullscreen fails.
        # ----------------------------------------------------------------------
        try:
            self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        except pygame.error:
            print("Warning: Fullscreen not available. Starting in windowed mode instead.")
            self.screen = pygame.display.set_mode((1920, 1080))

        self.screen_rect = self.screen.get_rect()
        self.bg_color = (200, 205, 220)  # Background block color in RGB.
        self.background = pygame.transform.scale(
            pygame.image.load("images/background_start.png").convert_alpha(), (1920, 1080)
        )
        pygame.display.set_caption("Katzen RPG")  # Text shown in the title bar.

        # The clock measures time and controls the frame rate.
        self.clock = pygame.time.Clock()

        # ----------------------------------------------------------------------
        # HERO CATS
        # ----------------------------------------------------------------------
        self.warrior_cat = Warrior(self, 1100, 350, "Warrior")
        self.healer_cat   = Cleric (self, 1150, 460, "Cleric")
        self.casting_cat  = Mage   (self, 1200, 590, "Mage")

        # ----------------------------------------------------------------------
        # ENEMIES
        # ----------------------------------------------------------------------
        self.boss     = Necromancer (self, 350, 350, "Evil Necromancer Cat")
        self.minion_1 = Poison_Minion(self, 650, 370, "Cat-Minion 1")
        self.minion_2 = Rage_Minion  (self, 650, 570, "Cat-Minion 2")

        # The current inventory instance.
        self.current_inventory = Inventory(self)

        # ----------------------------------------------------------------------
        # GROUPS & TURN ORDER
        # cat_heroes is shuffled so the heroes' turn order differs each run.
        # After shuffling, the list is reset to its original order, which is
        # required for correct cursor selection later.
        # ----------------------------------------------------------------------
        self.cat_heroes = [self.warrior_cat, self.healer_cat, self.casting_cat]
        random.shuffle(self.cat_heroes)  # Randomize hero order each run.
        self.enemies = [self.minion_1, self.minion_2, self.boss]
        self.fighting_order = [
            self.cat_heroes[0], self.minion_1,
            self.cat_heroes[1], self.minion_2,
            self.cat_heroes[2], self.boss
        ]
        # Reset to fixed order after shuffling — needed for correct cursor logic.
        self.cat_heroes = [self.warrior_cat, self.healer_cat, self.casting_cat]
        self.dead_enemies = []
        self.target_group = []  # Currently selected target group; used for cursor creation and ability sequences.

        # ----------------------------------------------------------------------
        # UI BOXES / BUTTONS
        # ----------------------------------------------------------------------
        self.cat_box     = Cat_Box(self, self.warrior_cat, self.healer_cat, self.casting_cat)  # Cat names, HP & MP.
        self.action_box  = Action_Box(self, self.cat_box)                                       # Action menu (Attack, Items, etc.).
        self.enemy_box   = Enemy_Box(self, self.boss, self.minion_1, self.minion_2, self.action_box)  # Enemy names.
        self.item_box    = Item_Box(self, self.action_box)                                      # Available items display.
        self.ability_box = Ability_Box(self, self.action_box)                                   # Available abilities display.
        self.tooltip_box = Tooltip_Box(self)                                                    # Describes abilities and enemy attacks.
        self.help_box    = Help_Box(self, self.cat_box.rect)                                    # Control help overlay.
        self.start_box   = Start_Box(self)

        self.tooltip_message = ""  # Text currently shown in the tooltip box.

        # ----------------------------------------------------------------------
        # TURN SYSTEM
        # ----------------------------------------------------------------------
        self.turn_timer     = 0                                      # Counts / indexes the current position in the turn order.
        self.current_player = self.fighting_order[self.turn_timer]   # Start with the first participant in the turn order.
        self.next_turn      = False                                   # Set to True when conditions for a new turn are met.

        self.current_target = 0     # Index of the currently selected target.
        self.enemy_target   = None  # The specific enemy target chosen this turn.
        self.enemy_action   = None  # The action the current enemy has selected.

        # ----------------------------------------------------------------------
        # CURSORS
        # player_cursor  — marker shown above the active combatant.
        # single_cursor  — selection cursor for a single target.
        # all_cursor     — selection cursor for an entire group.
        # ----------------------------------------------------------------------
        self.player_cursor = Cursor(self, self.current_player.rect.centerx - 10, self.current_player.rect.y - 30)
        self.single_cursor = Cursor(self, 0, 0)
        self.all_cursor    = Cursor(self, 0, 0)

        # ----------------------------------------------------------------------
        # BATTLE SEQUENCER & ACTION STATE
        # ----------------------------------------------------------------------
        self.battle_sequencer = Action(self)  # Handles the full battle sequence: attacks, damage, animations.
        self.current_action   = None          # Stores the currently executing battle action.

        # ----------------------------------------------------------------------
        # STATUS EFFECTS
        # ----------------------------------------------------------------------
        self.show_status  = False  # True while a status effect is being displayed.
        self.status_i     = None   # Iterates over the active status effects.
        self.status_done  = False  # True once all status effects for this turn have been processed.

        self.fight_active = False


    # ==========================================================================
    # MAIN GAME LOOP
    # ==========================================================================

    def run_game(self):
        """Main function — runs until the while loop is exited."""
        while True:
            if self.fight_active == False:
                self._check_events()
                self._update_screen()   # Redraws the screen with all updated values and positions.
                self.clock.tick(60)     # Updates the clock and sets the frame rate.
            elif self.fight_active == True:
                self._check_events()        # Check for player input this frame.
                self._check_start_turn()    # Check whether a new turn has just started.
                self.check_status_effect()  # Handle any active status effects.
                self.check_enemy_turn()
                self._check_for_action()    # Check whether an action is being executed.
                self._check_if_alive()      # Check whether all combatants are still alive.
                self._check_next_turn()     # Check whether conditions for a new turn are met.
                self._update_screen()
                self.clock.tick(60)

    # ==========================================================================
    # RENDERING
    # ==========================================================================

    def _update_screen(self):
        """Redraws the screen with all game elements."""
        if self.fight_active == False:
            self.screen.blit(self.background, (0, 0))
            self.start_box.draw_start_box()
            pygame.display.flip()
        elif self.fight_active == True:
            self.screen.blit(self.background, (0, 0))
            self._draw_game_fields()  # Draw the UI panels.
            self._draw_charakters()   # Draw the characters.
            self._draw_cursor()       # Draw the cursors.
            self._draw_effects()      # Draw all active effects.
            pygame.display.flip()     # Flip the display to show the new frame.

    def _draw_charakters(self):
        """Draws all characters (heroes and enemies)."""
        if self.warrior_cat.is_alive:
            self.screen.blit(self.warrior_cat.image, (self.warrior_cat.x_position, self.warrior_cat.y_position))
        if self.casting_cat.is_alive:
            self.screen.blit(self.casting_cat.image, (self.casting_cat.x_position, self.casting_cat.y_position))

        if self.minion_1.is_alive:
            self.screen.blit(self.minion_1.image, (self.minion_1.x_position, self.minion_1.y_position))
        if self.minion_2.is_alive:
            minion2_image = getattr(self.minion_2, "image", None)
            if minion2_image is not None:
                self.screen.blit(minion2_image, (self.minion_2.x_position, self.minion_2.y_position))
            else:
                pygame.draw.rect(self.screen, "purple", self.minion_2.rect)
        if self.boss.is_alive:
            self.screen.blit(self.boss.image, (self.boss.x_position, self.boss.y_position))

        # The healer cat is only drawn in its default/idle pose when no action
        # animation is playing. (Must be generalized once all character graphics exist.)
        if not self.battle_sequencer.cat_animation_active:
            self.screen.blit(self.healer_cat.image, (self.healer_cat.x_position, self.healer_cat.y_position))

    def _draw_game_fields(self):
        """Draws the UI panels of the battle screen."""
        self.cat_box.draw_cat_box(self.current_player)      # Panel with cat names, HP & MP.
        self.enemy_box.draw_enemy_box()                      # Panel with enemy names.

        # The action box is only drawn when the current combatant is player-controlled.
        if self.current_player in self.cat_heroes:
            self.action_box.draw_action_box(self.current_player)

        if self.item_box.active:
            self.item_box.draw_item_box(self.current_inventory, self.single_cursor.active)
        if self.ability_box.active:
            self.ability_box.draw_ability_box(self.current_player, self.single_cursor.active, self.all_cursor.active)

        # Read the tooltip message (if any) and draw the tooltip box (if active).
        self.get_tooltip()
        self.tooltip_box.draw_tooltip_box(self.tooltip_message)
        self.help_box.draw_help_box()

    def get_tooltip(self):
        """Reads the message to display in the tooltip box."""
        if self.item_box.active:
            # Tooltip message is read from the inventory dictionary.
            self.tooltip_message = self.item_box.current_items[self.item_box.current_position]["tooltip"]
        elif self.ability_box.active:
            # Tooltip message is read from the ability dictionary.
            self.tooltip_message = self.current_player.learned_abilities[self.ability_box.current_position]["tooltip"]
        elif self.show_status:
            # While a status effect is being processed, show an appropriate message.
            self.tooltip_message = self.battle_sequencer.message
        else:
            # No element with a tooltip is selected — clear the message.
            self.tooltip_message = ""

    def _draw_cursor(self):
        """Draws the cursors and markers on the battlefield."""
        # Player-turn marker: positioned centered above the active combatant.
        self.player_cursor.rect.x = (
            self.current_player.rect.centerx
            - (self.player_cursor.cursor_frame_width // 2 - 20)
        )
        self.player_cursor.rect.y = (
            self.current_player.rect.y
            - self.player_cursor.cursor_frame_height - 8  # 8-pixel gap above the character.
        )
        self.player_cursor.draw_animated_cursor(
            self.player_cursor.current_player_sheet,
            self.player_cursor.rect.x,
            self.player_cursor.rect.y,
            self.player_cursor.cursor_sprites_short
        )

        # The single-target selection cursor is only drawn when active.
        if self.single_cursor.active:
            if self.target_group == self.enemies:
                # Coordinates when the target belongs to the enemy group.
                self.single_cursor.rect.x = self.enemies[self.current_target].rect.right + 30
                self.single_cursor.rect.y = (
                    self.enemies[self.current_target].rect.centery
                    - (self.single_cursor.cursor_frame_height // 2)
                )
                self.single_cursor.draw_animated_cursor(
                    self.single_cursor.attack_sheet,
                    self.single_cursor.rect.x,
                    self.single_cursor.rect.y,
                    self.single_cursor.attack_sprites
                )
            elif self.target_group == self.cat_heroes:
                # Coordinates when the target belongs to the hero group.
                self.single_cursor.rect.x = (
                    self.cat_heroes[self.current_target].rect.left
                    - self.single_cursor.cursor_frame_width - 4
                )
                self.single_cursor.rect.y = (
                    self.cat_heroes[self.current_target].rect.centery
                    - (self.single_cursor.cursor_frame_height // 2)
                )
                self.single_cursor.draw_animated_cursor(
                    self.single_cursor.heal_sheet,
                    self.single_cursor.rect.x,
                    self.single_cursor.rect.y,
                    self.single_cursor.heal_sprites
                )

        # The all-targets cursor is drawn over every member of the selected group.
        if self.all_cursor.active:
            if self.target_group == self.enemies:
                for enemy in self.enemies:
                    self.all_cursor.rect.x = enemy.rect.right + 4
                    self.all_cursor.rect.y = enemy.rect.centery - (self.all_cursor.cursor_frame_height // 2 - 50)
                    self.all_cursor.draw_animated_cursor(
                        self.all_cursor.attack_sheet,
                        self.all_cursor.rect.x,
                        self.all_cursor.rect.y,
                        self.all_cursor.attack_sprites
                    )
            elif self.target_group == self.cat_heroes:
                for cat in self.cat_heroes:
                    self.all_cursor.rect.x = cat.rect.left - self.all_cursor.cursor_frame_width - 4
                    self.all_cursor.rect.y = cat.rect.centery - (self.all_cursor.cursor_frame_height // 2)
                    self.all_cursor.draw_animated_cursor(
                        self.all_cursor.heal_sheet,
                        self.all_cursor.rect.x,
                        self.all_cursor.rect.y,
                        self.all_cursor.heal_sprites
                    )

    def _draw_effects(self):
        """Draws all active effects when their conditions are met."""
        # Sprite animations for all characters (heroes and enemies).
        if not self.battle_sequencer.cat_animation_active:
            for enemy in self.enemies:
                enemy.update(is_selected=(enemy is self.current_player))
            for cat in self.cat_heroes:
                cat.update(is_selected=(cat is self.current_player))

        if not self.show_status:
            self.battle_sequencer.draw_damage_numbers()  # Draw damage numbers after an attack.
        else:
            self.battle_sequencer.draw_damage_numbers(self.battle_sequencer.font_color)  # Draw status-effect damage numbers.

        self.battle_sequencer.draw_cat_action_animation(self.current_player)  # Draw the cat combat animation (if active).
        self.battle_sequencer.draw_simple_effect()                             # Draw combat effects (if active).

    # ==========================================================================
    # INPUT HANDLING
    # ==========================================================================

    def _check_events(self):
        """Listens for player input events each frame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)
            if event.type == pygame.MOUSEMOTION:        # NEW: mouse hover
                self.check_mouse_motion(event)
            if event.type == pygame.MOUSEBUTTONDOWN:    # NEW: mouse click
                self.check_mouse_click(event)

    def check_mouse_motion(self, event):
        """Moves the menu cursor when the mouse hovers over a menu item or character."""
        if self.current_action or self.show_status or not self.fight_active:
            return
        mx, my = event.pos

        if self.action_box.active:
            for i, pos in enumerate(self.action_box.postitions):
                if pos.collidepoint(mx, my):
                    self.action_box.current_position = i

        elif self.item_box.active and not self.single_cursor.active:
            for i, pos in enumerate(self.item_box.postitions):
                if pos.collidepoint(mx, my):
                    self.item_box.current_position = i

        elif self.ability_box.active and not (self.single_cursor.active or self.all_cursor.active):
            for i, pos in enumerate(self.ability_box.postitions):
                if pos.collidepoint(mx, my):
                    self.ability_box.current_position = i

        elif self.single_cursor.active and self.target_group:
            # Hovering over a character sprite selects them as the target.
            for i, entity in enumerate(self.target_group):
                if entity.rect.collidepoint(mx, my):
                    self.current_target = i

    def check_mouse_click(self, event):
        """Handles mouse button clicks.

        Left click  — confirms the current selection (same as Enter).
        Right click — cancels / goes back (same as Escape).
        """
        if event.button == 1:   # Left click = confirm
            fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode='\r')
            self.check_keydown_events(fake_event)
        elif event.button == 3: # Right click = cancel
            fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode='')
            self.check_keydown_events(fake_event)

    def check_keydown_events(self, event):
        """Handles individual key-press events."""
        # Q — quit the game.
        if event.key == pygame.K_q:
            sys.exit()

        # SPACE — skip the current turn (temporary debug shortcut).
        if event.key == pygame.K_SPACE:
            if not self.current_action and not self.show_status and self.fight_active:
                self.current_player.action = False
                if self.single_cursor.active or self.all_cursor.active:
                    self._create_or_delete_cursor(None)
                self.ability_box.active = False
                self.item_box.active = False

        # The following inputs are only processed when no action sequence is playing.

        # DOWN ARROW — move cursor / selection downward.
        if event.key == pygame.K_DOWN and not self.current_action and not self.show_status and self.fight_active:
            if self.action_box.active:
                if self.action_box.current_position < len(self.action_box.postitions) - 1:
                    self.action_box.current_position += 1
            elif self.item_box.active and not self.single_cursor.active:
                if self.item_box.current_position < len(self.item_box.postitions) - 1:
                    self.item_box.current_position += 1
            elif self.ability_box.active and not (self.single_cursor.active or self.all_cursor.active):
                if self.ability_box.current_position < len(self.ability_box.postitions) - 1:
                    self.ability_box.current_position += 1
            # Move single-target cursor down; wraps back to the start when the end is reached.
            elif self.single_cursor.active:
                self.current_target += 1
                if self.current_target > len(self.target_group) - 1:
                    self.current_target = 0

        # UP ARROW — move cursor / selection upward.
        if event.key == pygame.K_UP and not self.current_action and not self.show_status and self.fight_active:
            if self.action_box.active:
                if self.action_box.current_position > 0:
                    self.action_box.current_position -= 1
            elif self.item_box.active and not self.single_cursor.active:
                if self.item_box.current_position > 0:
                    self.item_box.current_position -= 1
            elif self.ability_box.active and not (self.single_cursor.active or self.all_cursor.active):
                if self.ability_box.current_position > 0:
                    self.ability_box.current_position -= 1
            # Move single-target cursor up; wraps back to the end when the start is passed.
            elif self.single_cursor.active:
                self.current_target -= 1
                if self.current_target < 0:
                    self.current_target = len(self.target_group) - 1

        # ENTER — confirm / execute actions.
        if event.key == pygame.K_RETURN and not self.current_action and not self.show_status:
            if self.current_player in self.cat_heroes and self.action_box.active and self.fight_active:
                if self.action_box.current_position == 0:
                    # Position 0 (Attack): activate the target cursor aimed at enemies.
                    self._create_or_delete_cursor(self.enemies)
                    self.action_box.active = False
                if self.action_box.current_position == 1:
                    # Position 1 (Items): open the item box.
                    self.item_box.active    = True
                    self.tooltip_box.active = True
                    self.action_box.active  = False
                if self.action_box.current_position == 2:
                    # Position 2 (Abilities): open the ability box.
                    self.ability_box.active = True
                    self.tooltip_box.active = True
                    self.action_box.active  = False

            elif self.item_box.active and not self.single_cursor.active and self.fight_active:
                # Item box is open — activate the target cursor aimed at cats (heal items only for now).
                self._create_or_delete_cursor(self.cat_heroes)

            elif self.ability_box.active and not self.single_cursor.active and not self.all_cursor.active and self.fight_active:
                # An ability can only be selected if the cat has enough MP.
                if self.current_player.current_mp >= self.current_player.learned_abilities[self.ability_box.current_position]["mp_cost"]:
                    # Read the ability's target type from the dictionary and show the appropriate cursor.
                    if self.current_player.learned_abilities[self.ability_box.current_position]["target"] == "enemy":
                        self._create_or_delete_cursor(self.enemies)
                    elif self.current_player.learned_abilities[self.ability_box.current_position]["target"] == "cat":
                        self._create_or_delete_cursor(self.cat_heroes)
                else:
                    print("Play Error Sound!")  # Placeholder for a future error sound effect.

            elif (self.single_cursor.active or self.all_cursor.active) and self.current_action is None and self.fight_active:
                # A target cursor is active — confirm the selected action.
                if self.action_box.current_position == 0:
                    # Action Box position 0: execute the standard attack.
                    self.current_action = self.battle_sequencer.default_attack
                    # Deactivate the cursor while keeping target_group set (needed for the action).
                    self._create_or_delete_cursor(self.target_group)
                    self.battle_sequencer.action_sequence_active = True

                if self.action_box.current_position == 1:
                    # Action Box position 1: use an item.
                    self.current_action = self.battle_sequencer.use
                    self._create_or_delete_cursor(self.target_group)
                    self.battle_sequencer.action_sequence_active = True
                    self.item_box.active    = False
                    self.tooltip_box.active = False

                if self.action_box.current_position == 2:
                    # Action Box position 2 (Magic / Prayer / Skills):
                    # Match the selected ability's method name against all available methods
                    # and assign the matching method as the current action.
                    for method in self.battle_sequencer.all_abilities:
                        if method.__name__ == self.current_player.learned_abilities[self.ability_box.current_position]["method"]:
                            self.current_action = method
                            break
                    # Deduct the ability's MP cost from the cat's current mana.
                    self.current_player.current_mp -= self.current_player.learned_abilities[self.ability_box.current_position]["mp_cost"]
                    self._create_or_delete_cursor(self.target_group)
                    self.battle_sequencer.action_sequence_active = True
                    self.ability_box.active = False
                    self.tooltip_box.active = False

            elif not self.fight_active:
                # Start the fight when ENTER is pressed on the start screen.
                self.fight_active = True
                self.background = pygame.transform.scale(
                    pygame.image.load("images/background.png").convert_alpha(), (1920, 1080)
                )

        # ESCAPE — cancel current action or selection.
        if event.key == pygame.K_ESCAPE and not self.current_action and not self.show_status and self.fight_active:
            if self.single_cursor.active or self.all_cursor.active:
                # Cancel the current target selection and reopen the relevant box.
                self._create_or_delete_cursor(None)
                if self.action_box.current_position == 0:
                    self.action_box.active = True
                elif self.action_box.current_position == 1:
                    self.item_box.active = True
                elif self.action_box.current_position == 2:
                    self.ability_box.active = True
            elif self.item_box.active:
                # Cancel item selection and return to the action box.
                self.item_box.active          = False
                self.action_box.active        = True
                self.item_box.current_position = 0
                self.tooltip_box.active       = False
            elif self.ability_box.active:
                # Cancel ability selection and return to the action box.
                self.ability_box.active          = False
                self.action_box.active           = True
                self.ability_box.current_position = 0
                self.tooltip_box.active          = False

        # H — toggle the help overlay.
        if event.key == pygame.K_h:
            self.help_box.active = not self.help_box.active

    # ==========================================================================
    # CURSOR MANAGEMENT
    # ==========================================================================

    def _create_or_delete_cursor(self, group):
        """Creates or removes the target selection cursor.

        Args:
            group: The group whose members should be selectable.
                   Pass None to deactivate without setting a new group.
        """
        self.target_group = group

        # Determine from the current ability's dictionary entry whether to draw
        # a single-target cursor or an all-targets cursor.
        if self.ability_box.active and self.current_player.learned_abilities[self.ability_box.current_position]["t_number"] == "all":
            cursor = self.all_cursor
        else:
            cursor = self.single_cursor

        # Toggle the cursor: deactivate it if it is already active, otherwise activate it.
        cursor.active = not cursor.active

    # ==========================================================================
    # TURN LOGIC
    # ==========================================================================

    def _check_start_turn(self):
        """Checks whether conditions for starting a new turn are met.
        
        If so, selects the next active player. Dead combatants are skipped
        automatically by incrementing the turn timer until a living one is found.
        """
        if self.next_turn:
            self.item_box.active    = False
            self.ability_box.active = False
            self.tooltip_box.active = False

            while self.next_turn:
                self.current_player = self.fighting_order[self.turn_timer]

                if not self.current_player.is_alive:
                    # Skip dead combatants by advancing the timer.
                    self.turn_timer += 1
                    if self.turn_timer > len(self.fighting_order) - 1:
                        self.turn_timer = 0
                        for player in self.fighting_order:
                            player.action = True  # Restore actions for all combatants at the start of a new round.
                else:
                    # Found a living combatant — end the search loop.
                    self.next_turn = False

    def check_status_effect(self):
        """Checks for active status effects and applies their consequences.
        
        Runs once per turn for the current player if they have any status effects
        that have not yet been processed this turn.
        """
        if self.current_player.status_effects and not self.status_done:
            if not self.show_status:
                self.status_i  = len(self.current_player.status_effects) - 1
                self.show_status = True

            if not self.status_i < 0 and not self.battle_sequencer.damage_sequence_active:
                self.battle_sequencer.status_effect_calculator(
                    self.current_player,
                    self.current_player.status_effects[self.status_i]
                )
                self.status_i -= 1
                if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
                    self.battle_sequencer.damage_sequence_active = True
                    self.tooltip_box.active = True

            elif self.status_i < 0 and not self.battle_sequencer.damage_sequence_active:
                # All status effects have been processed — clean up.
                self.status_done     = True
                self.show_status     = False
                self.tooltip_box.active = False
                self.status_i        = None

                if self.current_player.current_hp <= 0:
                    self.current_player.is_alive = False
                    self.current_player.status_effects.clear()
                    self.current_player.action = False

                if "stun" in self.current_player.status_effects:
                    self.battle_sequencer.action_sequence_active = False
                    self.current_player.action = False

                self.check_status_timer()

    def check_status_timer(self):
        """Decrements and removes status effects whose timers have expired."""
        if "burn"    in self.current_player.status_effects and self.current_player.burn_timer    == 0:
            self.current_player.status_effects.remove("burn")
        if "stun"    in self.current_player.status_effects and self.current_player.stun_timer    == 0:
            self.current_player.status_effects.remove("stun")
        if "protect" in self.current_player.status_effects and self.current_player.protect_timer == 0:
            self.current_player.status_effects.remove("protect")
            self.current_player.defence -= 20  # Remove the defence bonus granted by Protect.

    def check_enemy_turn(self):
        """Triggers special enemy behaviors at the start of their turn."""
        if self.current_player in self.enemies:
            if self.current_player.revive_minions:
                self.battle_sequencer.revive_minions(
                    self.current_player, self.enemies, self.dead_enemies, self.enemy_action
                )
            if self.current_player.rage_modus:
                self.battle_sequencer.rage_modus(self.current_player)
            self.enemy_turn()

    def enemy_turn(self):
        """Executes the enemy's turn.
        
        Selects a random skill from the enemy's available skills, resolves the
        matching method, determines targets, and starts a 3-second pre-attack delay.
        """
        if not self.enemy_action:
            # Pick a random skill from the enemy's available skill list.
            self.enemy_action = choice(self.current_player.available_skills)

            # Find the method whose name matches the chosen skill's 'method' entry.
            for method in self.battle_sequencer.enemy_abilities:
                if method.__name__ == self.enemy_action["method"]:
                    self.current_action = method
                    break

            if self.enemy_action["target"] == "cat":
                # Only living cats are valid targets.
                for cat in self.cat_heroes:
                    if cat.is_alive:
                        self.target_group.append(cat)
                if self.enemy_action["t_number"] == "single":
                    # Single-target: pick a random living cat.
                    self.enemy_target = choice(self.target_group)

            elif self.enemy_action["target"] == "enemy":
                if self.enemy_action["t_number"] == "all":
                    self.target_group = self.enemies
                elif self.enemy_action["t_number"] == "single":
                    self.enemy_target = choice(self.enemies)

            # Start a 3-second countdown before the attack is executed.
            self.battle_sequencer.enemy_attack_timer = pygame.time.get_ticks()
            self.battle_sequencer.enemy_attack_ready = False
            self.battle_sequencer.action_sequence_active = True

    # ==========================================================================
    # ACTION EXECUTION
    # ==========================================================================

    def _check_for_action(self):
        """Checks whether an action is in progress and drives it to completion.
        
        For heroes: executes the chosen action with the correct target parameters.
        For enemies: waits for the pre-attack delay, then fires the action.
        Once both the action sequence and the damage display are finished,
        the current action is cleared and the player's turn ends.
        """
        if self.current_action:
            if self.battle_sequencer.action_sequence_active and self.current_player in self.cat_heroes:
                if self.current_action == self.battle_sequencer.use:
                    self.current_action == self.current_action(
                        self.target_group[self.current_target],
                        self.item_box.current_items[self.item_box.current_position]
                    )
                # If the selected ability targets all members of a group, pass the whole group.
                elif (self.action_box.current_position == 2 and
                      self.current_player.learned_abilities[self.ability_box.current_position]["t_number"] == "all"):
                    self.current_action(self.current_player, self.target_group)
                else:
                    self.current_action(self.current_player, self.target_group[self.current_target])

                # After the action sequence ends, start or skip the damage display phase.
                if not self.battle_sequencer.action_sequence_active:
                    if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
                        self.battle_sequencer.damage_sequence_active = True
                    else:
                        self.battle_sequencer.damage_sequence_active = False

            elif self.battle_sequencer.action_sequence_active and self.current_player in self.enemies:
                # Wait for the 3-second pre-attack delay to elapse.
                if not self.battle_sequencer.enemy_attack_ready:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.battle_sequencer.enemy_attack_timer >= self.battle_sequencer.enemy_attack_delay:
                        self.battle_sequencer.enemy_attack_ready = True

                # Execute the enemy's attack once the delay has elapsed.
                if self.battle_sequencer.enemy_attack_ready and not self.show_status:
                    if self.enemy_action["t_number"] == "all":
                        self.current_action(self.current_player, self.target_group)
                    elif self.enemy_action["t_number"] == "single":
                        self.current_action(self.current_player, self.enemy_target)
                    if not self.battle_sequencer.action_sequence_active:
                        if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
                            self.battle_sequencer.damage_sequence_active = True

            # Once both sequences are complete, reset the action state and end the turn.
            if not self.battle_sequencer.action_sequence_active and not self.battle_sequencer.damage_sequence_active:
                self.current_action  = None
                self.enemy_action    = None
                self.current_player.action = False

    # ==========================================================================
    # LIFE / DEATH CHECKS
    # ==========================================================================

    def _check_if_alive(self):
        """Checks whether any combatant has died.
        
        The check only runs after the damage numbers have finished displaying.
        Dead enemies are removed from the active enemy list and added to dead_enemies.
        """
        if not self.battle_sequencer.damage_sequence_active:
            for player in self.fighting_order:
                if player.current_hp <= 0:
                    player.is_alive = False
                    player.status_effects.clear()

            for enemy in self.enemies:
                if not enemy.is_alive:
                    enemy.status_effects.clear()
                    self.dead_enemies.append(enemy)
                    self.enemies.remove(enemy)

    def _check_next_turn(self):
        """Checks whether the current turn should end.
        
        The turn ends when the active player has no actions remaining.
        Resets all UI selections and increments (or wraps) the turn timer.
        At the end of a full round, every combatant's action is restored.
        """
        if not self.current_player.action:
            self.turn_timer += 1

            # Wrap the turn timer and restore actions for a new round.
            if self.turn_timer > len(self.fighting_order) - 1:
                self.turn_timer = 0
                for player in self.fighting_order:
                    player.action = True

            # Apply minion protection for any enemy that has it.
            for enemy in self.enemies:
                if enemy.minion_protection:
                    self.battle_sequencer.minion_protection(enemy, self.enemies)

            # Reset all UI cursor positions to their defaults.
            self.action_box.current_position  = 0  # Default: Attack
            self.item_box.current_position    = 0
            self.ability_box.current_position = 0
            self.current_target               = 0  # Default: first enemy in the group
            self.target_group                 = []

            # Reset status-effect tracking for the new turn.
            self.show_status      = False
            self.tooltip_box.active = False
            self.status_done      = False

            self.next_turn        = True   # Signal that the next turn should start.
            self.action_box.active = True  # The action box defaults to open at the start of each turn.
            self.current_player.was_selected = False

            # Reset the healer cat's sprite to its default idle pose.
            # (Can be generalized once all character graphics are in place.)
            self.healer_cat.image = self.healer_cat.default_sprite


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # Create a game instance and start the game.
    cf = Cat_Fight()
    cf.run_game()


# ==============================================================================
# INACTIVE / ARCHIVED CODE
# ==============================================================================
# The following is an older version of check_status_effect, kept for reference.
#
#   def check_status_effect(self):
#       """Checks for active status effects and applies their consequences."""
#       if self.current_player.status_effect != None and not self.status_done:
#           if not self.show_status:
#               self.battle_sequencer.status_effects(self.current_player)
#               # If the status effect deals damage, activate damage_sequence and
#               # show_status so the damage is processed. Also show a tooltip
#               # explaining why the player is taking damage.
#               if self.battle_sequencer.damage_group or self.battle_sequencer.healed_group:
#                   self.show_status = True
#                   self.battle_sequencer.damage_sequence_active = True
#                   self.tooltip_box.active = True
#               else:
#                   # If the status effect requires no damage, finish immediately.
#                   self.status_done = True
#           if not self.battle_sequencer.damage_sequence_active and not self.status_done:
#               # After the damage display, mark the status handling as complete.
#               self.show_status = False
#               self.status_done = True
#               self.tooltip_box.active = False
