import pygame, time
from entities import *
from objects import *
from utils import checkDict

clock = pygame.time.Clock()

def gameLoop(screen, running = True):       #we gaan verschillende loops op deze manier aanmaken (een voor de menu een voor de startscreen en dan een voor het spel)
    player = Player(50,50,width=50,height=50, animationfile = "test.json", scale = 2)
    ground = Object(0,1920*0.8, width=1080, height=200,color = (0,100,0))
    objects = [player, ground, Object(120,1920*0.8-30, width=50, height=30), Object(400,1920*0.8-80, width=200, height=30),Object(520,525, width=100, height=100) ]
    entities = [player]
    gravity = True

    last_time = time.time()
    while running:
        clock.tick(60)
        # delta time
        dt = time.time() - last_time
        last_time = time.time()
        if dt==0: fps = 0
        else: fps = 1/dt
        pygame.display.set_caption(f"fps: {str(fps)}")

        for event in pygame.event.get():
            match event.type: 
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    if event.key == pygame.K_F5:        #zwaartekracht toggelen
                        if gravity:
                            for obj in objects:
                                obj.accY = 0
                                obj.velY = 0
                            gravity = False
                        else:
                            for obj in objects:
                                if not obj.static:
                                    obj.accY = 1
                            gravity = True
                    if event.key == pygame.K_F6:
                        for obj in objects:
                            if not obj.static:
                                obj.Y = 50
                case pygame.KEYUP:
                    pass
                    
                case pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()

        screen.fill(color=(200,255,255))
        for obj in objects:
            otherobjects = [i for i in objects if i != obj]
            obj.update(otherobjects, dt = dt)       #updaten van het object zelf en een lijst van alle andere objecten doorgeven
        pygame.display.flip()