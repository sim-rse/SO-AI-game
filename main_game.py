#coole sprites ma geen stap animatie: https://diegosanches.com/science-kombat (scroll naar beneden)
import pygame
from loops import *
from objects import *
from entities import *
pygame.init()

class Game():
    def __init__(self,screen):
        self.screen = screen
        self.dt = 1
        self.window_scale = 1
        self.fps = 60

        self.running = True

        self.scene = "default"
        self.scene_running = False
        self.gravity = 1

        self.debugging = False

        self.objects = []
        self.UI = []
        self.background = pygame.images.load('images/projectimage1.png')

    def add(self,obj):
        if type(obj) == list:
            for i in obj:
                self.objects.append(i)
        else:
            self.objects.append(obj)

    def remove(self,obj):
        if type(obj) == list:
            for i in obj:
                self.objects.remove(i)
        else:
            print(f"removing {obj}")
            self.objects.remove(obj)

    def empty(self, keepUI = False):
        self.objects = []
        if not keepUI:
            self.UI = []

    def add_UI(self,obj):
        if type(obj) == list:
            for i in obj:
                self.UI.append(i)
        else:
            self.UI.append(obj)
    
    def remove_UI(self,obj):
        if type(obj) == list:
            for i in obj:
                self.UI.remove(i)
        else:
            self.UI.remove(obj)
    
    @property
    def entities(self):
        return [ent for ent in self.objects if isinstance(ent, Entity)]
    
    @property
    def players(self):
        return [obj for obj in self.objects if isinstance(obj, Player)]
    
    @property
    def colliders(self):
        return [obj for obj in self.objects if obj.collider]
    
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
        case "test_scene":
            test_menu(game)
pygame.quit()