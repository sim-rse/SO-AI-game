import pygame, time, hashlib, random
from entities import *
from objects import *
from UI.healthbar import healthbar
from UI.buttons import *
from UI.tracker import Tracker
#from AI import thing, connect
from deatharea import DeathArea 
from powerup import spawn_random_powerup
clock = pygame.time.Clock()

def gameLoop(game):       #we gaan verschillende loops op deze manier aanmaken (een voor de menu een voor de startscreen en dan een voor het spel)
    screen = game.screen
    keys = []
    color = (100,255,255)  # Kleur achtergrond voor als de achtergrond niet geladen is


    ground_level = game.screen_height*0.85
    match game.arena:
        case "jungle":
            background = pygame.image.load("images/projectimage1.jpg").convert()

            ground = Object(game, 0,ground_level, width=game.screen_width, height=200,color = (0,100,0))
            walls = [Wall(game,-50,0, width=50, height = screen.get_height()), Wall(game, screen.get_width(),0, width=50, height=screen.get_height())]
            platforms = [Object(game, 150, ground_level-100, width=200, height=30), Object(game, 800, ground_level-100, width=200, height=30), 
                        Object(game, 490, ground_level-200, width=220, height=30),
                        Object(game, 1100, ground_level-100, width=40, height=100), Object(game, 1100, ground_level-120, width=80, height=20)]
        case "mounts":
            background = pygame.image.load("images/projectimage2.jpg").convert()

            platforms = [Object(game, 850, ground_level-100, width=200, height=30), 
                         Object(game, 1150, ground_level-200, width=200, height=30),
                         Object(game, 1350, ground_level-300, width=100, height=30)]
            ground = Object(game, 0,ground_level, width=game.screen_width, height=200,color = (0,100,0))
            walls = []
        case "mounts2":
            background = pygame.image.load("images/projectimage3.jpg").convert()

            platforms = [Object(game, 550, ground_level-100, width=200, height=30), 
                         Object(game, 320, ground_level-200, width=200, height=30),
                         Object(game, 870, ground_level-200, width=100, height=30),]
            width = game.screen_width*0.8
            ground = Object(game,game.screen_width*0.1,ground_level, width=width, height=30,color = (0,50,0))
            walls = []
        case _:
            background = pygame.image.load("images/projectimage3.jpg").convert()
            
            platforms = []
            ground = Object(game, 0,ground_level, width=game.screen_width, height=200,color = (0,100,0))
            walls = [Wall(game,-50,0, width=50, height = screen.get_height()), 
                     Wall(game, screen.get_width(),0, width=50, height=screen.get_height())]

    background = pygame.transform.scale(background, (screen.get_width(),screen.get_height()))


    match game.player_character:
        case "Iron Stan":
            animationfile = "animations/ironman.json"
        case "K. Onami":
            animationfile = "animations/ninja.json"

    player = Player(game,150,550,width=50,height=50, animationfile = animationfile, scale = 1)
    misc = [DeathArea(game, top = -500, bottom=1500, left=-500, right=1800)]
    objects = [player, ground]
    
    game.add(objects)
    game.add(walls)
    game.add(platforms)
    
    enemy = Enemy(game, 600, 650, health=100, animationfile="animations/test.json", scale=2)
    game.add(enemy)

    UI = [healthbar(player, game), healthbar(enemy, game), Tracker(game, player, color="blue"), Tracker(game, enemy, color="red")]#PauseButton(game,screen.get_width()/2,100,"pause de game", border_color=(0,0,0))
    game.add_UI(UI)

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
                    if game.debugging:
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
                        if event.key == pygame.K_F9:
                            enemy.getPath(enemy.target)
                            enemy.current_action = "attack"
                            enemy.last_action_time = time.time()
                            enemy.current_action_length = 10

                    
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
                        #hier had een betere cheat code moeten komen, ma geen tijd :'( (een hint voor de cheat code in kwestie staat wel ergens verstopt in de game...)
                        print("Cheat code gevonden!!!")
                        for i in range(100):
                            spawn_random_powerup(game)
                        pass
                    
                case pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()

        # Achtergrond weergeven (blit de achtergrond op de screen)
        screen.fill(color=color)  # Indien achtergrond niet geladen is, vul het scherm met een default kleur

        # Achtergrond laden indien beschikbaar
        if background:
            screen.blit(background, (0, 0))  # Tekent de geselecteerde achtergrond op positie (0, 0)

        if time.time()-last_powerup_time > 15:
            spawn_random_powerup(game)
            last_powerup_time = time.time()
        #updaten van de 3 verschillende layers
        for i in misc:      
            i.update()
        for obj in game.objects:
            obj.update()       #updaten van het object zelf en een lijst van alle andere objecten doorgeven
        for i in game.UI:
            i.update()
            
        label = font.render(f"Player position   x: {round(player.pos.x,2)} y: {round(player.pos.y,2)}", 1, (255,255,255))
        screen.blit(label, (20, 20))
        label = font.render(f"Enemy actions     action: {enemy.current_action}, cooldown: {enemy.action_cooldown}", 1, (255,255,255))
        screen.blit(label, (20,50))

        pygame.display.flip()


def start_menu(game):
    screen = game.screen
    color = (0,0,0)
    font = pygame.font.SysFont("monospace", 50)
    label = font.render("Untitled Fight Game", 1, (255,255,255))

    bg = pygame.image.load("images/AI_startscreen.png")
    bg = pygame.transform.scale(bg, (screen.get_width(),screen.get_height()))
    width = 300
    UI = [SceneButton(game,screen.get_width()/2 - width/2,500,"Play","menu",width=width,height=50, color=(150,150,150), border_color=(50,50,50)), SceneButton(game,screen.get_width()/2 - width/2,600,"Quit","quit",width=width,height=50, color=(150,150,150), border_color=(50,50,50))]

    game.add_UI(UI)
    while game.running and game.scene_running:
        clock.tick(game.fps)
        screen.blit(bg, (0,0))
        
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