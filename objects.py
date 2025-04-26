import pygame
import json

from utils import checkDict
from spritesheet import Spritesheet
from animations import Animations

class Object:
    def __init__(self, gamevar, x, y, width = 0, height = 0, image = None, color = 'blue', animationfile = None, scale = 1):
        self.gamevar = gamevar

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
        screen = self.gamevar.screen
        if self.flipSprite:
            screen.blit(pygame.transform.flip(self.texture, True, False), (self.X, self.Y))
        else:
            screen.blit(self.texture, (self.X, self.Y)) #bij fotos werkt het licht anders dan bij vormen ma doet hetzelfde als pygame.draw.rect(...) bijvoorbeeld
    
    def update(self,otherobjects = None):
        
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
            colorkey = checkDict(sheet,"colorkey", (0,0,0))     #checks if the key existx in the dict. if it does then that value will be used, otherwise it takes the third argument as default one  
            spritesheet = Spritesheet(path = sheet["spritesheet"], width = sheet["width"], height = sheet["height"], colorkey = tuple(colorkey))

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
    def __init__(self, gamevar, x, y, width=0, height=0, image=None, hasCollisionEnabled=False, isStatic=True, color='blue', animationfile=None, scale=1):
        super().__init__(gamevar, x, y, width, height, image, color, animationfile, scale)

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
    
    def updatePos(self, otherObjects):
        dt = self.gamevar.dt        #tijdsverschil tussen de frames in seconden om beweging onafhankelijk van de fps te maken (voorlopig heb ik het op 1 gezet want de game was anders veel te traag)
       
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
        
    def update(self, otherObjects):
        
        if not self.static:         #dit moet nog weg, want object (dus niet bewegende object) is nu een aparte classe
            self.updatePos(otherObjects)
        super().update()