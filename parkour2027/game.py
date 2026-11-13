import pygame 
from physicEngine.elements import Bone,Vector2D

import Utils.UColors as uC


class Game:
    '''A class to represent the game.'''

    def __init__(self, width=800, height=600,ticks=60):
        pygame.init()

        self.width = width
        self.height = height
        self.ticks = ticks

        self.screen = pygame.display.set_mode((self.width, self.height))
        print(type(self.screen))

        pygame.display.set_caption("Parkour 2027")

        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        '''Run the game loop.'''
        while self.running:

            self.handle_event()
            self.draw()

            self.clock.tick(self.ticks)

    def draw(self):
        '''Draw the game screen.'''
        self.screen.fill((0, 0, 0))

        v1 = Vector2D(200,200)
        v2 = Vector2D(300,100)
        b = Bone(v1,v2,50,uC.BLUE)
        b.draw(self.screen)

        pygame.display.flip()

    def handle_event(self):
        '''Handle the exit event.'''
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False