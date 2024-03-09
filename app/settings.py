from pathlib import Path
import sys

import pygame

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # assets are in same directory as the executable
    # when running as bundled pyinstaller app
    DIR = Path(sys.executable).parent
else:
    # assets are relative to this files directory (parent)
    # when running from source code
    DIR = Path(__file__).parent.parent


# -- SETTINGS
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Waves
# 1/2, 3/4, 5/6, 7/8, 9/10
# 11/12, 13/14, 15/16, 17/18, 19/20
# -- COLORS
BACKGROUND = [
    'Black', 'Black', 'Black', 'Black', 'Blue',
    'cyan4', 'Magenta3', 'Yellow', 'gray93', 'Red'
]

CITY_GROUND = [
    'Yellow', 'Yellow', 'Blue', 'Red', 'Yellow',
    'Yellow', 'Green4', 'Green', 'Red', 'Yellow'
]

CITY_COLOR = [
    'Cyan', 'Cyan', 'Yellow', 'Yellow', 'Magenta',
    'Black', 'Black', 'White', 'Yellow', 'Green'
]

PLAYER_COLOR = [
    'Blue', 'Blue', 'Green', 'Blue', 'Black',
    'Blue', 'Yellow', 'Red', 'Green4', 'Blue'
]

ENEMY_COLOR = [
    'Red', 'Green', 'Red', 'Yellow', 'Red',
    'Red', 'Black', 'Black', 'Magenta3', 'Black'
]

EXPLOSION_COLORS = [
    'white', 'cadetblue1', 'darkorange', 'deeppink1',
    'firebrick1', 'gold', 'green', 'yellow'
]

MISSILE_SPEEDS = [
    20.8, 37.14, 57.78, 86.67, 94.55,
    104.0, 130.0, 148.57, 167.74, 173.33
]

# multi is max starting at 11/12
WAVE_MULTIPLERS = [1,2,3,4,5,6,6,6,6,6]


#
