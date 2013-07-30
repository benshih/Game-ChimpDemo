# These statements 
import os, sys
import pygame
from pygame.locals import *

if not pygame.font: print 'warning, fonts disabled'
if not pygame.mixer: print 'warning, music disabled'

# These functions allow us to load the required images and sounds for the game.
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            color = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
        if not pygame.mixer:
            return NoneSound()
        fullname = os.path.join('data', name)
        try:
            sound = pygame.mixer.Sound(fullname)
        except pygame.error, message:
            print 'Cannot load sound:', wav
            raise SystemExit, message
        return sound

# Classes that represent objects in the game (Fist and Monkey).
class Fist(pygame.sprite.Sprite):
    '''moves a clenched fist on the screen, following the mouse'''
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('fist.bmp', -1)
        self.punching = 0

    def update(self):
        "move the first based on the mouse position"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos
        if self.punching:
            self.rect.move_ip(5, 10)

    def punch(self, target):
        '''returns true if the fist collides with the target'''
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unpunch(self):
        '''called to pull the fist back'''
        self.punching = 0
