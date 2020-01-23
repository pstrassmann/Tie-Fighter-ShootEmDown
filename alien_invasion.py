import sys
from time import sleep

import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from torpedo import Torpedo
from alien import Alien
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button


class AlienInvasion:
    """Overall class to manage game assets and behavior"""

    def __init__(self):
        """Initialize the game, and create game resources."""

        # Initialize pygame and set screen size and display mode
        pygame.init()
        self.settings = Settings()
        # self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        # self.clock = pygame.time.Clock()

        # Initialize game statistics and scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # Initialize sprites
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.torpedos = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

        # Make the play button
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            # self.dt = self.clock.tick(100)

    def _check_events(self):
        """Respond to keypresses and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks play"""

        # Detect mouse click on play button, start game, and reset stats and settings
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Get rid of any remaining aiens and bullets
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor
            pygame.mouse.set_visible(False)

    def _check_keyup_events(self, event):
        """Respond to key releases"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_keydown_events(self, event):
        """Respond to key presses"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_t:
            self._fire_torpedo()
        elif event.key == pygame.K_q:
            sys.exit()

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _fire_torpedo(self):
        """Create a new bullet and add it to the bullets group"""
        if len(self.torpedos) < self.settings.torpedos_allowed:
            new_torpedo = Torpedo(self)
            self.torpedos.add(new_torpedo)

    def _update_bullets(self):
        """Update bullet positions and test if more bullets are allowed
        """
        self.bullets.update()
        self.torpedos.update()

        # Get rid of bullets that are no longer visible
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        for torpedo in self.torpedos.copy():
            if torpedo.rect.bottom <= 0:
                self.torpedos.remove(torpedo)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """"Detect bullet-alien collisions and remove both if collided"""

        collisions_bullet = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        collisions_torpedo = pygame.sprite.groupcollide(self.torpedos, self.aliens, False, True)


        if collisions_bullet:
            for list_of_hit_aliens in collisions_bullet.values():
                self._update_score(list_of_hit_aliens)

        if collisions_torpedo:
            for list_of_hit_aliens in collisions_torpedo.values():
                self._update_score(list_of_hit_aliens)

        if not self.aliens:  # if all aliens have been destroyed
            # Get rid of existing bullets and generate new fleet
            self.bullets.empty()
            self.torpedos.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level
            self.stats.level += 1
            self.sb.prep_level()

    def _update_score(self, list_of_hit_aliens):
        self.stats.score += self.settings.alien_points * len(list_of_hit_aliens)
        self.sb.prep_score()
        self.sb.check_high_score()

    def _create_alien(self, alien_number, row_number):
        # Create an alien and place it in the row
        alien = Alien(self)
        alien_width, alien.height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = (1.5 * alien.rect.height) + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _create_fleet(self):
        """ Create the fleet of aliens"""
        # Create an alien and fine the number of aliens in a row
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop down and change fleet direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_aliens_bottom(self):
        """Checks if any aliens have reached bottom of screen"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()  # Treat as loss, like ship collision
                break

    def _ship_hit(self):
        """Respond to the ship-alien collisions"""
        if self.stats.ships_left > 0:
            # Decrement ships_left
            self.stats.ships_left -= 1
            self.sb.prep_ships()


            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            # Pause
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _update_aliens(self):
        """Update the positions of all aliens in the fleet"""
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Look for aliens hitting screen bottom
        self._check_aliens_bottom()

    def _update_screen(self):
        """Update images on screen, and flip to the new screen"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        for torpedo in self.torpedos.sprites():
            torpedo.blitme()
        self.aliens.draw(self.screen)

        #Draw scoreboard
        self.sb.show_score()

        # Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()

        # Make the most recently drawn screen visible
        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
