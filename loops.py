import pygame, time, hashlib, random
from entities import *
from objects import *
from healthbar import healthbar
from buttons import *
from tracker import Tracker
#from AI import thing, connect
from deatharea import DeathArea 
from powerrup import spawn_random_powerup
clock = pygame.time.Clock()

def gameLoop(game):       #we gaan verschillende loops op deze manier aanmaken (een voor de menu een voor de startscreen en dan een voor het spel)
    screen = game.screen

    keys = []
    color = (100,255,255)  # Kleur achtergrond voor als de achtergrond niet geladen is
    ground_level = game.screen_height*0.8

    player = Player(game,150,550,width=50,height=50, animationfile = "animations/ninja.json", scale = 0.5)
    ground = Object(game, 0,ground_level, width=game.screen_width, height=200,color = (0,100,0))
    walls = [Wall(game,-50,0, width=50, height = screen.get_height()), Wall(game, screen.get_width(),0, width=50, height=screen.get_height())]
    platforms = [Object(game, 150, ground_level-100, width=200, height=30), Object(game, 650, ground_level-100, width=200, height=30), 
                 Object(game, 400, ground_level-200, width=200, height=30), Object(game, 800, ground_level-250, width=200, height=30),
                 Object(game, 900, ground_level-100, width=40, height=100), Object(game, 940, ground_level-100, width=80, height=10)]
    misc = [DeathArea(game, top = -500, bottom=1500, left=-500, right=1800)]
    objects = [player, ground]
    UI = [healthbar(player, game, width=30), Tracker(game, player, color="blue")]#PauseButton(game,screen.get_width()/2,100,"pause de game", border_color=(0,0,0))
    
    game.add(objects)
    game.add(walls)
    game.add(platforms)
    game.add_UI(UI)

    enemy = Enemy(game, 600, 650)
    game.add(enemy)

    grav = True
    font = pygame.font.SysFont("monospace", 15)

    last_time = time.time()
    last_powerup_time = time.time()

    while game.scene_running and game.running:
        clock.tick(game.fps)

        # delta time
        dt = time.time() - last_time
        last_time = time.time()
        if dt == 0: fps = 0
        else: fps = 1/dt
        #game.dt = dt
        
        if game.debugging:
            pygame.display.set_caption(f"Untitled Fight Game [DEBUG] - fps: {str(fps)}")

        for event in pygame.event.get():
            match event.type: 
                case pygame.QUIT:
                    game.running = False
                case pygame.KEYDOWN:
                    if event.key == pygame.K_F5:        #zwaartekracht toggelen
                        if grav:
                            game.gravity = 0.1
                            for obj in objects:
                                if not obj.static and obj.affected_by_gravity:
                                    obj.acc.y = 0
                                    obj.vel.y = 0
                            grav = False
                        else:
                            game.gravity = 1
                            grav = True
                    if event.key == pygame.K_F6:
                        for obj in objects:
                            if not obj.static:
                                obj.pos.y = 50
                    if event.key == pygame.K_F7:
                        game.scene_running = False
                    if event.key == pygame.K_F8:
                        spawn_random_powerup(game)
                    if event.key == pygame.K_ESCAPE:
                        game.pause()
                    key = pygame.key.name(event.key)
                    if len(keys)>=8:
                        keys.pop(0)
                        keys.append(key)
                    else:
                        keys.append(key)

                    patat = hashlib.md5(str(keys).encode())
                    if str(patat.hexdigest()) == "97bd60a0f2d7cd76cf49e96e69d8996d":
                        color = (0,255,255)
                        player.loadAnimations("animations\\luigi.json",scale=2)
                    #print(f"str keys is: {str(keys)} and hash is: {patat.hexdigest()}")
                case pygame.KEYUP:
                    pass
                    
                case pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()

        # Achtergrond weergeven (blit de achtergrond op de screen)
        screen.fill(color=color)  # Indien achtergrond niet geladen is, vul het scherm met een default kleur

        # Achtergrond laden indien beschikbaar
        if game.background:
            screen.blit(game.background, (0, 0))  # Tekent de geselecteerde achtergrond op positie (0, 0)

        #updaten van de 3 verschillende layers
        for i in misc:      
            i.update()
        for obj in game.objects:
            obj.update()       #updaten van het object zelf en een lijst van alle andere objecten doorgeven
        for i in game.UI:
            i.update()
            
        label = font.render(f"Player position   x: {round(player.pos.x,2)} y: {round(player.pos.y,2)}", 1, (0,0,0))
        screen.blit(label, (20, 20))

        pygame.display.flip()

def start_menu(game):
    screen = game.screen
    color = (0,0,0)
    font = pygame.font.SysFont("monospace", 50)
    label = font.render("Untitled Fight Game", 1, (255,255,255))

    width = 300
    UI = [SceneButton(game,screen.get_width()/2 - width/2,500,"Play","menu",width=width,height=50), SceneButton(game,screen.get_width()/2 - width/2,600,"Quit","quit",width=width,height=50)]

    game.add_UI(UI)
    while game.running and game.scene_running:
        clock.tick(game.fps)
        screen.fill(color)
        
        for event in pygame.event.get():
            match event.type: 
                case pygame.QUIT:
                    game.running = False
        
        for ui in UI:
            ui.update()
        
        pygame.display.flip()

def quit(game):
    print("quitting")
    game.running = False