#-------------------------------------------------------------------#
#         Voorlopige main (start) file voor de game                 #
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
    def __init__(self, x, y, width = 0, height = 0, image = None, hasCollisionEnabled = False, isStatic = True):
        self.X = x                  #positie
        self.Y = y

        if image:
            self.texture = pygame.image.load(image) #laden van de texture (jargon voor afbeelding fyi)
            if height !=0 or width !=0:
                self.texture = pygame.transform.scale(self.texture, (width, height))
        else:
            self.texture = pygame.Surface((width,height))
            self.texture.fill('blue')

        self.width = self.texture.get_width()
        self.height = self.texture.get_height()
        print(self.texture)

        self.velX = 0           #snelheid (velocity)
        self.velY = 0
        self.accX = 0           #acceleratie
        self.accY = 0

        self.collisionsEnabled = hasCollisionEnabled
        self.static = isStatic          #als het statisch is, heeft zwaartekracht geen invloed
        self.hitbox = self.getHitbox()

    def getHitbox(self):       #geeft de coordinaten van de hoekpunten terug, handig voor de collisions
        return {"top":self.Y,"bottom":self.Y+self.height,"left":self.X,"right":self.X+self.width}
    
    def updatePos(self, otherObjects):

        # Update X first
        self.velX += self.accX  #nieuwe snelheid en positie
        self.X += self.velX
        self.hitbox = self.getHitbox()
        #collisions checken
        if self.collisionsEnabled:
            for otherObject in otherObjects:
                if self.collideswith(otherObject):
                    if self.velX > 0:
                        self.X = otherObject.hitbox["left"] - self.width
                    elif self.velX < 0:
                        self.X = otherObject.hitbox["right"]
                    self.velX = 0
                    self.hitbox = self.getHitbox()

        # Then update Y
        self.velY += self.accY
        self.Y += self.velY
        self.hitbox = self.getHitbox()
        if self.collisionsEnabled:
            for otherObject in otherObjects:
                if self.collideswith(otherObject):
                    if self.velY > 0:
                        self.Y = otherObject.hitbox["top"] - self.height
                    elif self.velY < 0:
                        self.Y = otherObject.hitbox["bottom"]
                    self.velY = 0
                    self.hitbox = self.getHitbox()

        screen.blit(self.texture, (self.X, self.Y)) #bij fotos werkt het licht anders dan bij vormen ma doet hetzelfde als pygame.draw.rect(...) bijvoorbeeld

    
    def update(self, otherObjects):
        self.updatePos(otherObjects)

    def smoothSpeedChange(self,targetValue, steps = 10):        #to be implemented
        pass
    
    def collideswith(self, otherObject):        #van WPO6 gekopieerd, ma we werken hier enkel met rechthoeken
        x1 = self.X
        y1 = self.Y
        x2 = self.X + self.width
        y2 = self.Y + self.height
        
        otherObjectx1 = otherObject.X
        otherObjecty1 = otherObject.Y
        otherObjectx2 = otherObject.X + otherObject.width
        otherObjecty2 = otherObject.Y + otherObject.height
        
        if x1 < otherObjectx2 and x2 > otherObjectx1 and y1 < otherObjecty2 and y2 > otherObjecty1:
            return True
        else:
            return False

class Entity(Object):
    def __init__(self, x, y, width = 0, height = 0, image = "placeholder.png", health = 20):
        super().__init__(x, y, width, height, image, hasCollisionEnabled=True, isStatic=False)

        self.health = health
    
    def die(self):
        pass #of call een global game over functie

    def update(self,otherObjects):
        super().update(otherObjects)        #doet wat de update van de parent doet plus wat hieronder staat
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
            #print(f"right, newpos: {self.X}")
        if keys[pygame.K_LEFT]:
            accel[0] += -5
            #print(f"left, newpos: {self.X}")
        if keys[pygame.K_UP]:       #voorlopig oneindig jumps mogelijk, moet nog een checkIfOnGround() functie zetten
            accel[1] += -5
            #print(f"UP, newpos: {self.Y}")
        if keys[pygame.K_DOWN]:
            accel[1] += 5
            #print(f"DOWN, newpos: {self.Y}")
        self.velX = accel[0]        #indien we deze methode gebruiken blijft de speler staan indien we zowel links en rechts indrukken, en als je een toets loslaat heb je ook geen problemen met de richting
        self.velY = accel[1]

    def update(self,otherObjects):
        self.getMovement()
        super().update(otherObjects)



def gameLoop(running = True):
    player = Player(50,50,width=50,height=50)
    entities = [player, Object(50,150,width=100,height=50)]

    #print(f"entities: {entities}")


    while running:
        clock.tick(50)

        for event in pygame.event.get():
            match event.type: 
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    if event.key == pygame.K_F5:
                        for ent in entities:
                            if not ent.static:
                                ent.accY = 9.81/2
                    if event.key == pygame.K_F6:
                        for ent in entities:
                            if not ent.static:
                                ent.Y = 50
                                ent.accY = 0
                                ent.velY=0
                case pygame.KEYUP:
                    if event.key == pygame.K_F5:
                        for ent in entities:
                            ent.accY = 0
                    
        screen.fill(color=(255,255,255))
        for ent in entities:
            otherEntities = [i for i in entities if i != ent]
            ent.update(otherEntities)       #updaten van het object zelf en een lijst van alle andere objecten doorgeven

            """if ent.collisionsEnabled:   #handles collision if collisions are enabled for the entity
                ent.collisionHandling(otherEntities)"""
        pygame.display.flip()

        

gameLoop()








pygame.quit()