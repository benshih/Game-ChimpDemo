# These statements import the necessary libraries for the program.
import os, sys
import pygame
from pygame.locals import *

if not pygame.font: print("warning, fonts disabled")
if not pygame.mixer: print("warning, music disabled")

# These functions allow us to load the required images and sounds for the game.
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            color = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print('Cannot load sound: ', fullname)
        raise SystemExit(message)
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

class Chimp(pygame.sprite.Sprite):
    '''move a monkey across the screen. spins the monkey when punched'''
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call sprite initializer
        self.image, self.rect = load_image('chimp.bmp', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10
        self.move = 9
        self.dizzy = 0

    def update(self):
        '''walk or spin depending on monkey's state'''
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        '''move the monkey across the screen, and turn at the ends'''
        newpos = self.rect.move((self.move, 0))
        if not self.area.contains(newpos):
            if self.rect.left < self.area.left or self.rect.right > self.area.right:
                self.move = -self.move # start moving in the opposite direction if we encounter a boundary
                newpos = self.rect.move((self.move, 0))
                # fancy effect that makes the monkey appear to turn in the direction 
                self.image = pygame.transform.flip(self.image, 1, 0)
            self.rect = newpos
            
    # underscore for function suggests that the methods should only be used by the Chimp class
    def _spin(self):
        '''spin the monkey image'''
        center = self.rect.center
        self.dizzy += 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center = center)

    def punched(self):
        '''causes the monkey to start spinning'''
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image

def main():
    
    # Initialize program components (the reason why nothing was showing up!)
    pygame.init()
    screen = pygame.display.set_mode((468, 60))
    pygame.display.set_caption('monkey fever')
    pygame.mouse.set_visible(0)

    # Create the background for the message text.
    background = pygame.Surface(screen.get_size())
    background = background.convert() # makes sure the background is the same format as the display window, which provides the fastest results
    background.fill((250, 250, 250))

    # Render centered text on the background.
    if pygame.font:
        font = pygame.font.Font(None, 36) # use the default font, size 36
        text = font.render("pummel the chimp and win $$$", 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2)
        background.blit(text, textpos) # paste the text onto the background image

    # display the background while initializing other resources
    screen.blit(background, (0,0))
    pygame.display.flip() # handles single buffered and double buffered surfaces so that they are visible to the user.

    # prepare all the game objects that the game will use.
    ## sound effects
    whiff_sound = load_sound('')
    punch_sound = load_sound('')
    ## create an instance of each sprite class
    chimp = Chimp()
    fist = Fist()
    ## RenderPlain for simple drawings
    ## allsprites list contains all the sprites that belong in the group
    allsprites = pygame.sprite.RenderPlain((fist, chimp))
    ## control thede game's framerate by making sure the main loop doesn't run too quickly
    clock = pygame.time.Clock()

    # main game loop
    while 1:
        ## makes sure the game doesn't run faster than 60 fps
        clock.tick(60)

        ## handle input events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == MOUSEBUTTONDOWN:
                if fist.punch(chimp):
                    punch_sound.play()
                    chimp.punched()
                else:
                     whiff_sound.play()
            elif event.type == MOUSEBUTTONUP:
                fist.unpunch()

        allsprites.update()
        
        ## draw the entire scene
        screen.blit(background, (0,0))
        allsprites.draw(screen)
        pygame.display.flip()

# calls the main function when the python script is executed
if __name__ == '__main__': main()
