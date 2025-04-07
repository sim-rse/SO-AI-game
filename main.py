#-------------------------------------------------------------------#
#         Voorlopige main (start) file voor de fight game           #
#-------------------------------------------------------------------#
import pygame
pygame.init()

screenInfo = pygame.display.Info()

screen_x = (screenInfo.current_w)*0.9
screen_y = (screenInfo.current_h)*0.9
screen_size = [screen_x,screen_y] #(width x height)
screen = pygame.display.set_mode(screen_size) #voeg pygame.FULLSCREEN als argument toe voor fullscreen

clock = pygame.time.Clock()

class Object:
    def __init__(self, x, y, width = 0, height = 0, image = "placeholder.png"):
        self.X = x                  #positie
        self.Y = y
        self.width = width
        self.height = height

        self.texture = pygame.image.load(image) #laden van de texture (jargon voor afbeelding fyi)
        print(self.texture)

        self.velX = 0           #snelheid (velocity)
        self.velY = 0

        self.accX = 0           #acceleratie
        self.accY = 0

    def updatePos(self):        
        self.velX += self.accX #nieuwe snelheid en versnelling
        self.velY += self.accY
        self.X += self.velX
        self.Y += self.velY

        screen.blit(self.texture,(self.X, self.Y))  #bij fotos werkt het licht anders dan bij vormen ma doet hetzelfde als pygame.draw.rect(...) bijvoorbeeld
    
    def update(self):
        self.updatePos()

    def smoothSpeedChange(self,targetValue, steps = 10):
        self.targetVel = targetValue
        difference = targetValue - self.velX


class Entity(Object):
    def __init__(self, x, y, width = 0, height = 0, image = "placeholder.png", health = 20):
        super().__init__(x, y, width, height, image)

        self.health = health
    
    def die(self):
        pass #of call een global game over functie

    def update(self):
        self.updatePos()
        if self.health <= 0: 
            self.die()

class Player(Entity):
    def __init__(self, x, y, width = 0, height = 0, image = "placeholder.png"):
        super().__init__(x, y, width, height, image)
        #later komen de stats en abilities hier

    def getMovement(self):
        keys = pygame.key.get_pressed()

        accel = [0,0]

        if keys[pygame.K_RIGHT]:
            accel[0] +=5
            print(f"right, newpos: {self.X}")
        if keys[pygame.K_LEFT]:
            accel[0] += -5
            print(f"left, newpos: {self.X}")
        if keys[pygame.K_UP]:       #voorlopig oneindig jumps mogelijk, moet nog een checkIfOnGround() functie zetten
            accel[1] += -5
            print(f"UP, newpos: {self.Y}")
        if keys[pygame.K_DOWN]:
            accel[1] += 5
            print(f"DOWN, newpos: {self.Y}")
        self.velX = accel[0]        #indien we deze methode gebruiken blijft de speler staan indien we zowel links en rechts indrukken, en als je een toets loslaat heb je ook geen problemen met de richting
        self.velY = accel[1]

    def update(self):
        self.getMovement()
        super().update()



def gameLoop(running = True):
    player = Player(50,50)
    entities = [player]
    print(f"entities: {entities}")


    while running:
        clock.tick(50)

        for event in pygame.event.get():
            match event.type: 
                case pygame.QUIT:
                    running = False
                    
        screen.fill(color=(255,255,255))
        for ent in entities:
            ent.update()
        pygame.display.flip()

        

gameLoop()








pygame.quit()