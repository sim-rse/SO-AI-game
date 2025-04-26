import pygame, time, hashlib
from entities import *
from objects import *

clock = pygame.time.Clock()

def gameLoop(game):       #we gaan verschillende loops op deze manier aanmaken (een voor de menu een voor de startscreen en dan een voor het spel)
    screen = game.screen
    game.scene_running = True

    keys = []
    color = (100,255,255)

    player = Player(game,50,50,width=50,height=50, animationfile = "test.json", scale = 2)
    ground = Object(game, 0,game.screen_height*0.8, width=game.screen_width, height=200,color = (0,100,0))
    objects = [player, ground, Object(game, 120,game.screen_height*0.8-30, width=50, height=30), Object(game, 400,game.screen_height*0.8-80, width=200, height=30),Object(game, 520,525, width=100, height=100) ]
    entities = [player]
    gravity = True

    font = pygame.font.SysFont("monospace", 15)

    

    last_time = time.time()
    while game.scene_running and game.running:
        clock.tick(60)
        # delta time
        dt = time.time() - last_time
        last_time = time.time()
        if dt==0: fps = 0
        else: fps = 1/dt
        #game.dt = dt
        if game.debugging:
            pygame.display.set_caption(f"fps: {str(fps)}")

        for event in pygame.event.get():
            match event.type: 
                case pygame.QUIT:
                    game.running = False
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
                    if event.key == pygame.K_F7:
                        game.scene_running = False

                    key = pygame.key.name(event.key)
                    if len(keys)>=8:        #sought hash is 6855703423273221168
                        keys.pop(0)
                        keys.append(key)
                    else:
                        keys.append(key)

                    patat = hashlib.md5(str(keys).encode())
                    if str(patat.hexdigest()) == "97bd60a0f2d7cd76cf49e96e69d8996d":
                        color = (0,255,255)
                        player.loadAnimations("luigi.json",scale=2)
                    #print(f"str keys is: {str(keys)} and hash is: {patat.hexdigest()}")
                case pygame.KEYUP:
                    pass
                    
                case pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()

        screen.fill(color=color)
        for obj in objects:
            otherobjects = [i for i in objects if i != obj]
            obj.update(otherobjects)       #updaten van het object zelf en een lijst van alle andere objecten doorgeven

        label = font.render(f"Player position   x: {round(player.X,2)} y: {round(player.Y,2)}", 1, (0,0,0))
        screen.blit(label, (20, 20))

        pygame.display.flip()