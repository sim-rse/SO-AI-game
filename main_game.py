#coole sprites ma geen stap animatie: https://diegosanches.com/science-kombat (scroll naar beneden)
import pygame
from loops import gameLoop
pygame.init()

class Game():
    def __init__(self,screen):
        self.screen = screen
        self.dt = 1
        self.window_scale = 1

        self.running = True

        self.scene = "default"
        self.scene_running = False

        self.debugging = False
    @property
    def screen_width(self):
        return self.screen.get_width()
    @property
    def screen_height(self):
        return self.screen.get_height()

screenInfo = pygame.display.Info()

screen_x = (screenInfo.current_w)*0.9
screen_y = (screenInfo.current_h)*0.9
screen_size = [1536,864] #(width x height)
screen = pygame.display.set_mode(screen_size) #voeg pygame.FULLSCREEN als argument toe voor fullscreen

pygame.display.set_caption("Untitled Fight Game - Nu met animaties!")

game = Game(screen) #We maken ee game class aan die allerlei variabels over de game in het algemeen (zoals screen, lijsten met entities enz, tijd tussen de frames) groepeert zodat we telkens maar een variabel moeten doorgeven en niet duizenden. Zo kan een object makkelijker variabels van andere objecten veranderen (zolang deze zich ergens in de Game object bevinden) 

while game.running:
    match game.scene:
        case "default":
            gameLoop(game)
pygame.quit()