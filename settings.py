class Settings:
    """A class to store all settings for Alien Invasion"""

    def __init__(self):
        """Initialize the game's static settings"""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (0, 0, 0)

        # Bullet settings
        self.bullet_width = 2
        self.bullet_height = 25
        self.bullet_color = (0, 255, 0)
        self.bullets_allowed = 10

        # Alien settings
        self.fleet_drop_speed = 10

        # Ship settings
        self.ship_limit = 3
        self.last_fired_on_right = True

        # How quickly the game speeds up
        self.speedup_scale = 1.7
        self.score_scale = 1.5
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        self.ship_speed = 10
        self.bullet_speed = 30.0
        self.alien_speed = 3.0
        # fleet_direction of 1 is flag for right; -1 flag for left
        self.fleet_direction = 1

        # Scoring
        self.alien_points = 50

    def increase_speed(self):
        """ Increase speed settings and alien point values"""
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
