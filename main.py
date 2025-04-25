#-------------------------------------------------------------------#
#         Voorlopige main (start) file voor de game                 #
#-------------------------------------------------------------------#

#coole sprites ma geen stap animatie: https://diegosanches.com/science-kombat (scroll naar beneden)
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

def checkDict(dict_to_check,key_to_find, value_if_not_found):
    if key_to_find in dict_to_check:
        return dict_to_check[key_to_find]
    else:
        return value_if_not_found
#                                                                                   ↱ entity → de verschillende personnages (moet nog gemaakt worden) → player en enemy
# de voorlopige classen, mijn idee voor de hierarchie van de classen:       object ˧
#                                                                                   ↳ andere dingen: platormen, buttons, ... Ze stammen allemaal af van de object classe
class Object:
    def __init__(self, x, y, width = 0, height = 0, image = None, color = 'blue', animationfile = None, scale = 1):
        self.X = x                  #positie
        self.Y = y
        self.animated = False
        self.static = True

        if animationfile:
            self.animated = True
            print(f"animating {self}")
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
            #self.animations.load("default",[self.texture])
        else:
            self.texture = pygame.Surface((width,height))
            self.texture.fill(color)
            print(f"filled surface with color: {color}")

        #self.width = self.texture.get_width()
        #self.height = self.texture.get_height()

        

        self.flipSprite = False #wordt bij bv de speler gebruikt om een naar links kijkende animaties te maken uit naar rechts kijkende sprites
    
        

    @property
    def width(self):
        return self.texture.get_width()
    
    @property
    def height(self):
        return self.texture.get_height()

    @property
    def hitbox(self):       #geeft de coordinaten van de hoekpunten terug, handig voor de collisions
        return {"top":self.Y,"bottom":self.Y+self.height,"left":self.X,"right":self.X+self.width}
    
    def blit(self):
        #deze gaan we voor een betere structuur naar ergens anders moeten verplaatsen
        if self.flipSprite:
            screen.blit(pygame.transform.flip(self.texture, True, False), (self.X, self.Y))
        else:
            screen.blit(self.texture, (self.X, self.Y)) #bij fotos werkt het licht anders dan bij vormen ma doet hetzelfde als pygame.draw.rect(...) bijvoorbeeld
    
    def update(self, otherObjects, dt=1):
        
        if self.animated:
            self.animationHandler()
            self.animations.update()
            self.texture = self.animations.image
        self.blit()
        
    def loadAnimations(self, file, scale=1):       #scale verandert de groote van alle frames met factor scale, wordt gebruikt door  de makeAnimation() methode
        with open(file) as f:
            data = json.load(f)

        for sheet in data:
            print(f"[info: sheet] {sheet}")
            spritesheet = Spritesheet(path = sheet["spritesheet"], width = sheet["width"], height = sheet["height"])

            for animation_name, animation_data in sheet["animations"].items():       #zonder de .items() krijg je alleen de namen van de keys en niet hun waarden erbij
                #print(animation_name, animation_data)

                temp_scale = checkDict(animation_data,"scale", scale)
                anim = spritesheet.makeAnimation(frames=animation_data["frames"],column=animation_data["column"], row=animation_data["row"], direction=animation_data["direction"], scale = temp_scale)
                next = checkDict(animation_data, "next", None)
                loop = checkDict(animation_data, "loop", False)
                self.animations.load(name = animation_name, animation = anim, loop = loop, next=next)     #next is ook (onnodige) een functie, dus ideaal de naam veranderen in de toekomst

    def playanimation(self, animation):
        self.animations.play(animation)

    def updateAnimation(self):
        pass

    def animationHandler(self):
        pass

class MovingObject(Object):
    def __init__(self, x, y, width=0, height=0, image=None, hasCollisionEnabled=False, isStatic=True, color='blue', animationfile=None, scale=1):
        super().__init__(x, y, width, height, image, color, animationfile, scale)

        self.velX = 0           #snelheid (velocity)
        self.velY = 0
        self.accX = 0           #acceleratie

        if isStatic:            #zwaartkracht geven
            self.accY = 0 
        else: 
            self.accY = 1
        
        self.collisionsEnabled = hasCollisionEnabled
        self.static = isStatic          #als het statisch is, heeft zwaartekracht geen invloed

        self.onGround = False
    
    def updatePos(self, otherObjects, dt):

        # Eerst kijken naar de x as
        self.velX += self.accX*dt  #nieuwe snelheid en positie
        self.X += self.velX*dt
        
        #collisions checken
        if self.collisionsEnabled:
            for otherObject in otherObjects:
                if self.collideswith(otherObject):
                    if self.velX > 0:
                        self.X = otherObject.hitbox["left"] - self.width
                    elif self.velX < 0:
                        self.X = otherObject.hitbox["right"]
                    self.velX = 0

        # dan de y as
        #if not self.static and not

        self.velY += self.accY*dt
        self.Y += self.velY*dt
        
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

    def smoothSpeedChange(self,targetValue):
        difference = targetValue - self.velX
        if abs(difference)>0.1:
            if self.onGround:
                force = 0.4
            else: 
                force = 0.2 
            self.accX = difference*force
        else:
            self.accX = difference          #zodat hij niet oneindig klein begint te gaan en dat de walk animatie blijft spelen bv.
    
    def collideswith(self, otherObject):        #van WPO6 gekopieerd, ma we werken hier enkel met rechthoeken
        #basically de hitboxen van de twee objecten berekenen, afhankelijk van wat minder zwaar is voor de computer houden wij deze methode of de hitbox() methode
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
        
    def update(self, otherObjects, dt=1):
        if not self.static:
            self.updatePos(otherObjects,dt)
        super().update(otherObjects, dt)
    
class Entity(MovingObject):
    def __init__(self, x, y, width = 0, height = 0, image = "placeholder.png", animationfile = None, scale = 1, health = 20):
        super().__init__(x, y, width, height, image, hasCollisionEnabled=True, isStatic=False, animationfile = animationfile, scale = scale)

        self.health = health
        self.strength = 2
    
    def die(self):
        self.playanimation("die")
        #of call een global game over functie
    
    def jump(self):
        if self.onGround:
            self.velY = -14

    def getDamage(self, damage):
        self.health -= damage
        self.playanimation("get_damaged")

    def punch(self, otherEntity = None):
        self.playanimation("punch")
        if otherEntity:
            otherEntity.getDamage(self.strength)
        

    def update(self, otherObjects, dt=1):
        super().update(otherObjects)        #doet wat de update van de parent doet plus wat hieronder staat
        if self.health <= 0: 
            self.die()

class Player(Entity):
    def __init__(self, x, y, width = 0, height = 0, image = "placeholder.png", animationfile = None, scale = 1):
        super().__init__(x, y, width, height, image, animationfile, scale)
        self.walkSpeed = 10
        #later komen de states en abilities hier

    def getKeyPress(self):
        keys = pygame.key.get_pressed()
        accel = [0,0]

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
        if keys[pygame.K_SPACE]:
            self.punch()

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
        self.getKeyPress()
        super().update(otherObjects)

class Enemy(Entity):
    def __init__(self, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20):
        super().__init__(x, y, width, height, image, animationfile, scale, health)

    

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
    objects = [player, ground, Object(120,screen_y*0.8-30, width=50, height=30), Object(400,screen_y*0.8-80, width=200, height=30),Object(520,525, width=100, height=100) ]
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

        

gameLoop()
pygame.quit()