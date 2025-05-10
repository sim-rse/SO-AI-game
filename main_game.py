#coole sprites ma geen stap animatie: https://diegosanches.com/science-kombat (scroll naar beneden)
import pygame
from loops import *
from objects import *
from entities import *
from start_menu import selection_menu
from powerrup import PowerUp
from game_end import game_over

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

        self.debugging = True

        self.objects = []
        self.UI = []
        self.backgrounds = [
        pygame.image.load("images/projectimage1.jpg").convert(),
        pygame.image.load("images/projectimage2.jpg").convert(),
        pygame.image.load("images/projectimage3.jpg").convert()
        ]

        for num, img in enumerate(self.backgrounds):
            self.backgrounds[num] = pygame.transform.scale(img, (screen.get_width(), screen.get_height()))
        self.background_index = 0
    
    @property
    def background(self):
        return self.backgrounds[self.background_index]
    
    @background.setter
    def background(self, value):
        if type(value)==int:
            self.background_index = value
    
    def add(self,obj):
        if type(obj) == list:
            for i in obj:
                self.objects.append(i)
        else:
            self.objects.append(obj)

    def remove(self,obj):
        if type(obj) == list:
            for i in obj:
                if i in self.objects:       #er was ander soms een error bij projectiles waarbij het zich twee keer probeerde te removen (dit was een tijdelijke fix, maar als u dit ziet ben ik het vergeten deftig op te lossen)
                    self.objects.remove(i)
        else:
            #print(f"removing {obj}")
            if obj in self.objects:
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
    
    def pause(self):       #deze scene werkt lichtjes anders: het moet ergens binnen de loop van de andere scenes geroepen worden zodat we dan terug naar de andere 
                                #kheb het ook hiet gezet ipv in loops.py door circulaire imports
        screen: pygame.display = self.screen
        current_scene = self.scene
        keys = []
        color = (30,30,30)
        width = 200
        UI = [SceneButton(self,screen.get_width()/2 - width/2,screen.get_height()*0.4,"Back to game","default",width=width,height=50), SceneButton(self,screen.get_width()/2 - width/2,screen.get_height()*0.5,"Start Menu","start_menu",width=width,height=50)]   #de naam van de scene kan technisch gezien random zijn, want we keren toch terug naar de vorige scene

        pygame.draw.rect(screen, (50,50,50,200), pygame.Rect(screen.get_width()*0.2, screen.get_height()*0.2, screen.get_width()*0.6, screen.get_height()*0.6))
        pygame.draw.rect(screen, (255,0,0,200), pygame.Rect(screen.get_width()*0.22, screen.get_height()*0.22, screen.get_width()*0.56, screen.get_height()*0.56), width=10)
        
        font = pygame.font.SysFont("monospace", 30)
        title = font.render("Game Paused", 1, (255,255,255), (50,50,50))
        screen.blit(title, (screen.get_width()/2 - title.get_width()/2, screen.get_height()*0.21))

        while self.running and self.scene_running:
            clock.tick(self.fps)
            #screen.fill(color)
            

            for event in pygame.event.get():
                match event.type: 
                    case pygame.QUIT:
                        self.running = False
                    case pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_ESCAPE:
                                self.scene_running = False
            
            for ui in UI:
                ui.update()
        
            pygame.display.flip()
        if self.scene == current_scene:
            self.scene_running = True #houdt deze true zodat de gepauseerde loop waarin we bezig zijn gwn verder gaat en niet reset    
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
    
    def __str__(self):
        return f"Main game object containing {self.objects}"

screenInfo = pygame.display.Info()

screen_x = (screenInfo.current_w)*0.9
screen_y = (screenInfo.current_h)*0.9
screen_size = [1536,864] #(width x height)
screen = pygame.display.set_mode(screen_size) #voeg pygame.FULLSCREEN als argument toe voor fullscreen

pygame.display.set_caption("Untitled Fight Game - AI in the works!")

game = Game(screen) #We maken ee game class aan die allerlei variabels over de game in het algemeen (zoals screen, lijsten met entities enz, tijd tussen de frames) groepeert zodat we telkens maar een variabel moeten doorgeven en niet duizenden. Zo kan een object makkelijker variabels van andere objecten veranderen (zolang deze zich ergens in de Game object bevinden) 
#zahide 
while game.running:
    game.empty()
    game.scene_running = True
    match game.scene:
        case "default":
            gameLoop(game)
        case "start_menu":
            start_menu(game)
        case "menu":
            selection_menu(game)
        case "pause":
            game.pause()
        case 'game_over':
            game_over(game)
        case "quit":
            quit(game)


pygame.quit()