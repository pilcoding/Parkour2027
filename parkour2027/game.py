import pygame 


class Game:
    '''A class to represent the game.'''

    def __init__(self, width=800, height=600,ticks=60):
        pygame.init()

        self.width = width
        self.height = height
        self.ticks = ticks

        self.screen = pygame.display.set_mode((self.width, self.height))

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
        pygame.display.flip()

    def handle_event(self):
        '''Handle the exit event.'''
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False
                