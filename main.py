#-------------------------------------------------------------------#
#         Voorlopige main (start) file voor de game                 #
#-------------------------------------------------------------------#
import pygame
import time
import os
import json
from spritesheet import Spritesheet
from animations import Animations
pygame.init()

screenInfo = pygame.display.Info()

screen_x = (screenInfo.current_w)*0.9
screen_y = (screenInfo.current_h)*0.9
screen_size = [screen_x,screen_y] #(width x height)
screen = pygame.display.set_mode(screen_size) #voeg pygame.FULLSCREEN als argument toe voor fullscreen

pygame.display.set_caption("Untitled Fight Game - Nu met animaties!")

clock = pygame.time.Clock()

class Object:
    def __init__(self, x, y, width = 0, height = 0, image = None, hasCollisionEnabled = False, isStatic = True, color = 'blue', animationfile = None, scale = 1):
        self.X = x                  #positie
        self.Y = y
        self.animated = False

        
        if animationfile:
            self.animated = True

            self.animations = Animations()
            self.loadAnimations(animationfile,scale)
            self.animations.play('default')
            self.texture = self.animations.image
            #print(f"type texture :{type(self.texture)}")
        #elif os.path.exists(pad naar animationfile met de naam van de classe zodat we het niet telkens moeten bijgeven)
        elif image:
            self.texture = pygame.image.load(image) #laden van de texture (jargon voor afbeelding fyi)
            
            if height !=0 or width !=0:             #zou je een width en height geven dan kan je de speler herschalen
                self.texture = pygame.transform.scale(self.texture, (width, height))
            self.animations.load("default",[self.texture])
        else:
            self.texture = pygame.Surface((width,height))
            self.texture.fill(color)

        self.width = self.texture.get_width()
        self.height = self.texture.get_height()

        self.velX = 0           #snelheid (velocity)
        self.velY = 0
        self.accX = 0           #acceleratie

        self.flipSprite = False #wordt bij bv de speler gebruikt om een naar links kijkende animaties te maken uit naar rechts kijkende sprites

        if isStatic:            #zwaartkracht geven
            self.accY = 0 
        else: 
            self.accY = 1
        
        
        self.collisionsEnabled = hasCollisionEnabled
        self.static = isStatic          #als het statisch is, heeft zwaartekracht geen invloed
        self.hitbox = self.getHitbox()
        self.onGround = False

        

    def getHitbox(self):       #geeft de coordinaten van de hoekpunten terug, handig voor de collisions
        return {"top":self.Y,"bottom":self.Y+self.height,"left":self.X,"right":self.X+self.width}
    
    def updatePos(self, otherObjects, dt):

        # Eerst kijken naar de x as
        self.velX += self.accX*dt  #nieuwe snelheid en positie
        self.X += self.velX*dt
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

        # dan de y as
        #if not self.static and not

        self.velY += self.accY*dt
        self.Y += self.velY*dt
        self.hitbox = self.getHitbox()
        
        self.onGround = False #neemt aan dat de object niet op de grond is, maar als er wel vanonder collision is wordt het wel als op de grond beschouwd (zie enkele lijnen onder)

        if self.collisionsEnabled:
            for otherObject in otherObjects:
                if self.collideswith(otherObject):
                    if self.velY > 0:
                        self.onGround = True                                #als er vanonder collision is, is het op de grond
                        self.Y = otherObject.hitbox["top"] - self.height
                    elif self.velY < 0:
                        self.Y = otherObject.hitbox["bottom"]
                    self.velY = 0
                    self.hitbox = self.getHitbox()

        #deze gaan we voor een betere structuur naar ergens anders moeten verplaatsen
        if self.flipSprite:
            screen.blit(pygame.transform.flip(self.texture, True, False), (self.X, self.Y))
        else:    
            screen.blit(self.texture, (self.X, self.Y)) #bij fotos werkt het licht anders dan bij vormen ma doet hetzelfde als pygame.draw.rect(...) bijvoorbeeld
    
    def update(self, otherObjects, dt=1):
        self.updatePos(otherObjects,dt)
        if self.animated:
            self.animationHandler()
            self.animations.update()
            self.texture = self.animations.image
        

    def smoothSpeedChange(self,targetValue):
        difference = targetValue - self.velX
        if difference>0.1:
            if self.onGround:
                force = 0.4
            else: 
                force = 0.2 
            self.accX = difference*force
        else:
            self.accX = difference          #zodat hij niet oneindig klein begint te gaan en dat de walk animatie blijft spelen bv.
    
    def collideswith(self, otherObject):        #van WPO6 gekopieerd, ma we werken hier enkel met rechthoeken
        #basically de hitboxen van de twee objecten berekenen, afhankelijk van wat minder zwaar is voor de computer houden wij deze methode of de gethitbox() methode
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

    def loadAnimations(self, file, scale=1):       #scale verandert de groote van alle frames met factor scale, wordt gebruikt door  de makeAnimation() methode
        with open(file) as f:
            data = json.load(f)

        for sheet in data:
            print(f"[info: sheet] {sheet}")
            spritesheet = Spritesheet(path = sheet["spritesheet"], width = sheet["width"], height = sheet["height"])

            for animation_name, animation_data in sheet["animations"].items():       #zonder de .items() krijg je alleen de namen van de keys en niet hun waarden erbij
                #print(animation_name, animation_data)
                anim = spritesheet.makeAnimation(frames=animation_data["frames"],column=animation_data["column"], row=animation_data["row"], direction=animation_data["direction"], scale = scale)
                self.animations.load(name = animation_name, animation = anim, loop = animation_data["loop"])

    def playanimation(self, animation):
        self.animations.play(animation)

    def updateAnimation(self):
        pass
    def animationHandler(self):
        pass

class Entity(Object):
    def __init__(self, x, y, width = 0, height = 0, image = "placeholder.png", animationfile = None, scale = 1, health = 20):
        super().__init__(x, y, width, height, image, hasCollisionEnabled=True, isStatic=False, animationfile = animationfile, scale = scale)

        self.health = health
    
    def die(self):
        pass #of call een global game over functie
    
    def jump(self):
        if self.onGround:
            self.velY = -14

    def update(self, otherObjects, dt=1):
        super().update(otherObjects)        #doet wat de update van de parent doet plus wat hieronder staat
        if self.health <= 0: 
            self.die()

class Player(Entity):
    def __init__(self, x, y, width = 0, height = 0, image = "placeholder.png", animationfile = None, scale = 1):
        super().__init__(x, y, width, height, image, animationfile, scale)
        self.walkSpeed = 10
        #later komen de states en abilities hier

    def getMovement(self):
        keys = pygame.key.get_pressed()
        accel = [0,0]
        test = 0
        for i in keys:
            if i == True:
                test += 1
        if keys[pygame.K_RIGHT]:
            accel[0] += self.walkSpeed
            self.flipSprite = False
        if keys[pygame.K_LEFT]:
            accel[0] += -self.walkSpeed
            self.flipSprite = True          #bij het op de scherm zetten van de sprites worden ze gespiegeld zodat ze naar links kijken (dit blijft zo totdat er weer op rechts wordt gedrukt)
        if keys[pygame.K_a]:
            pass
        if keys[pygame.K_UP]:
            self.jump()                 #te vinden bij Entity class
        if keys[pygame.K_DOWN]:
            pass
        #print(test)
        self.smoothSpeedChange(accel[0])        #indien we deze methode gebruiken blijft de speler staan indien we zowel links en rechts indrukken, en als je een toets loslaat heb je ook geen problemen met de richting die niet juist kan zijn

    def animationHandler(self):
        if self.velY<0:
            self.playanimation("jump")
        elif self.onGround and self.velX !=0:
            self.playanimation("walk")
        elif self.velY>0:
            self.playanimation("fall")
        else:
            self.playanimation("default")
        
    def update(self,otherObjects,dt=1):
        self.getMovement()
        super().update(otherObjects)

class Button(Object):
    def __init__(self, x, y, text, clickedFunction, width = 100, height = 50, image = None):
        super().__init__(x,y,width,height,image)

        self.text = text
    
    def checkClick(self):
        pass




def timeInteval():          #negeer deze, voorlopig niet gebruikt
    now = time.time()
    if prev_frame_time:
        dt = now - prev_frame_time 
        prev_frame_time = now
        print(now)
        yield dt
    else:
        prev_frame_time = now
        yield 1
        

def gameLoop(running = True):       #we gaan verschillende loops op deze manier aanmaken (een voor de menu een voor de startscreen en dan een voor het spel)
    player = Player(50,50,width=50,height=50, animationfile = "test.json", scale = 2)
    ground = Object(0,screen_y*0.8, width=screen_x, height=200,color = (0,100,0))
    entities = [player, ground, Object(120,screen_y*0.8-30, width=50, height=30), Object(400,screen_y*0.8-80, width=200, height=30),Object(520,525, width=100, height=100) ]
    gravity = True

    last_time = time.time()
    while running:
        clock.tick(60)
        # delta time
        dt = time.time() - last_time
        last_time = time.time()
        #pygame.display.set_caption(str(dt))

        for event in pygame.event.get():
            match event.type: 
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    if event.key == pygame.K_F5:        #zwaartekracht toggelen
                        if gravity:
                            for ent in entities:
                                ent.accY = 0
                                ent.velY = 0
                            gravity = False
                        else:
                            for ent in entities:
                                if not ent.static:
                                    ent.accY = 1
                            gravity = True
                    if event.key == pygame.K_F6:
                        for ent in entities:
                            if not ent.static:
                                ent.Y = 50
                case pygame.KEYUP:
                    pass
                    
        screen.fill(color=(255,255,255))
        for ent in entities:
            otherEntities = [i for i in entities if i != ent]
            ent.update(otherEntities, dt = dt)       #updaten van het object zelf en een lijst van alle andere objecten doorgeven
        pygame.display.flip()

        

gameLoop()
pygame.quit()