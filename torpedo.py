import pygame
from pygame.sprite import Sprite

class Torpedo(Sprite):

    def __init__(self, ai_game):
        super().__init__()
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        #Load torpedo image
        self.image = pygame.image.load('images/torpedo.png')
        self.rect = self.image.get_rect()
        self.rect.midtop = ai_game.ship.rect.midtop

        self.y = float(self.rect.y)

    def update(self):
        """Move the torpedo up the screen"""
        # Update the decimal position of the bullet.
        self.y -= (self.settings.bullet_speed * 1.2)
        # Update the rect position
        self.rect.y = self.y


    def blitme(self):
        """Draw the torpedo at its current location."""
        self.screen.blit(self.image, self.rect)
