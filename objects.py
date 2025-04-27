import pygame
import json

from utils import checkDict
from spritesheet import Spritesheet
from animations import Animations

class Object:
    def __init__(self, game, x, y, width = 0, height = 0, image = None, color = 'blue', animationfile = None, scale = 1):        #image geeft een pad naar de afbeeldin, color = Als er geen afbeelding is, maak een gekleurd vierkant.
        self.game = game

        self.pos = pygame.math.Vector2(x,y)     #positie

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

        self.flipSprite = False #wordt bij bv de speler gebruikt om een naar links kijkende animaties te maken uit naar rechts kijkende sprites
        #Als True, dan wordt het plaatje gespiegeld
        

    @property   #Je hoeft self.width en self.height niet zelf bij te houden, dat komt van het plaatje (texture).
    def width(self):
        return self.texture.get_width()
    
    @property
    def height(self):
        return self.texture.get_height()

    @property
    def hitbox(self):       #geeft de coordinaten van de hoekpunten terug, handig voor de collisions
        return {"top":self.pos.y,"bottom":self.pos.y+self.height,"left":self.pos.x,"right":self.pos.x+self.width}
    
    def blit(self):
        screen = self.game.screen
        if self.flipSprite:             #Als flipSprite aanstaat, wordt het plaatje horizontaal gespiegeld, Anders tekenen we het gewoon normaal op het scherm.
            screen.blit(pygame.transform.flip(self.texture, True, False), (self.pos.x, self.pos.y))
        else:
            screen.blit(self.texture, (self.pos.x, self.pos.y)) #bij fotos werkt het licht anders dan bij vormen ma doet hetzelfde als pygame.draw.rect(...) bijvoorbeeld
    
    def update(self,otherobjects = None):
        
        if self.animated:                   # als het object een animatie heeft: 
            self.animationHandler()         #de animatie geüpdatet,het juiste frame gekozen,en getekend op het scherm.
            self.animations.update()
            self.texture = self.animations.image
        self.blit()
        
    def loadAnimations(self, file, scale=1):       #scale verandert de groote van alle frames met factor scale, wordt gebruikt door  de makeAnimation() methode
                                    #Functie om animaties te laden uit een JSON-bestand;
        with open(file) as f:       #Opent het bestand (meestal een .json) dat animatiegegevens bevat
            data = json.load(f)

        for sheet in data:
            print(f"[info: sheet] {sheet}")
            colorkey = checkDict(sheet,"colorkey", (0,0,0))     #checks if the key existx in the dict. if it does then that value will be used, otherwise it takes the third argument as default one  
            spritesheet = Spritesheet(path = sheet["spritesheet"], width = sheet["width"], height = sheet["height"], colorkey = tuple(colorkey))        #Maakt een nieuw Spritesheet-object aan

            for animation_name, animation_data in sheet["animations"].items():       #zonder de .items() krijg je alleen de namen van de keys en niet hun waarden erbij
                #print(animation_name, animation_data)

                temp_scale = checkDict(animation_data,"scale", scale)                # Haalt de schaalfactor op uit de data, of gebruikt standaard 'scale' parameter
                anim = spritesheet.makeAnimation(frames=animation_data["frames"],column=animation_data["column"], row=animation_data["row"], direction=animation_data["direction"], scale = temp_scale)     # deze maakt een lijst van frames voor de animaties 
                next = checkDict(animation_data, "next", None)  #Welke animatie moet erna komen (optioneel)
                loop = checkDict(animation_data, "loop", False) # Moet de animatie in een lus herhalen? (True/False)
                self.animations.load(name = animation_name, animation = anim, loop = loop, next=next)     #next is ook een (onnodige) functie, dus ideaal de naam veranderen in de toekomst
    
    def playanimation(self, animation):     # Speelt een bepaalde animatie af
        self.animations.play(animation)

    def updateAnimation(self):           #we hebben die twee hier nodig om errors te vermijden, ze worden echter bij child klassen gebruikt
        pass

    def animationHandler(self):        
        pass

class MovingObject(Object):
    def __init__(self, game, x, y, width=0, height=0, image=None, hasCollisionEnabled=False, affected_by_gravity=True, color='blue', animationfile=None, scale=1):
        super().__init__(game, x, y, width, height, image, color, animationfile, scale)

        self.velX = 0           
        self.velY = 0
        self.vel = pygame.math.Vector2(0,0)     #snelheid (velocity)
        self.acc = pygame.math.Vector2(0,0)           #acceleratie

        self.static = False
        self.gravity = self.game.gravity
        self.collisionsEnabled = hasCollisionEnabled
        self.affected_by_gravity = affected_by_gravity  #heeft zwaartekracht invloed
        self._gravity = self.game.gravity          #sterkte van de zwaartekracht (kan ook op 0 worden ingesteld, dan is er momenteel geen zwaartekracht)

        self.onGround = False

    """@property
    def gravity(self):
        return self.game.gravity
    @property.setter
    def gravity(self):
        pass"""
    
    def updatePos(self, otherObjects):
        dt = self.game.dt        #tijdsverschil tussen de frames in seconden om beweging onafhankelijk van de fps te maken (voorlopig heb ik het op 1 gezet want de game was anders veel te traag)
       
        # Eerst kijken naar de x as
        self.vel.x += self.acc.x*dt  #nieuwe snelheid en positie
        self.pos.x += self.vel.x*dt
        
        #collisions checken
        if self.collisionsEnabled:
            for otherObject in otherObjects:
                if self.collideswith(otherObject):
                    if self.vel.x > 0:
                        self.pos.x = otherObject.hitbox["left"] - self.width
                    elif self.vel.x < 0:
                        self.pos.x = otherObject.hitbox["right"]
                    self.vel.x = 0

        # dan de y as
        self.vel.y += (self.acc.y+self.game.gravity)*dt
        self.pos.y += self.vel.y*dt
        
        self.onGround = False #neemt aan dat de object niet op de grond is, maar als er wel vanonder collision is wordt het wel als op de grond beschouwd (zie enkele lijnen onder)

        if self.collisionsEnabled:
            for otherObject in otherObjects:
                if self.collideswith(otherObject):
                    if self.vel.y > 0:
                        self.onGround = True                                #als er vanonder collision is, is het op de grond
                        self.pos.y = otherObject.hitbox["top"] - self.height
                    elif self.vel.y < 0:
                        self.pos.y = otherObject.hitbox["bottom"]
                    self.vel.y = 0

    def smoothSpeedChange(self,targetValue):
        difference = targetValue - self.vel.x
        if abs(difference)>0.1:
            if self.onGround:
                force = 0.4
            else: 
                force = 0.2 
            self.acc.x = difference*force
        else:
            self.acc.x = difference          #zodat hij niet oneindig klein begint te gaan en dat de walk animatie blijft spelen bv.
    
    def collideswith(self, otherObject, range_ = 0):        #van WPO6 gekopieerd, ma we werken hier enkel met rechthoeken
        #basically de hitboxen van de twee objecten berekenen, afhankelijk van wat minder zwaar is voor de computer houden wij deze methode of de hitbox() methode
        x1 = self.pos.x
        y1 = self.pos.y
        x2 = self.pos.x + self.width
        y2 = self.pos.y + self.height
        
        otherObjectx1 = otherObject.pos.x - range_  #Met range_ kun je oof zien of de self zich op een bepaalde afstand van otherObject bevindt                 
        otherObjecty1 = otherObject.pos.y - range_
        otherObjectx2 = otherObject.pos.x + otherObject.width + range_
        otherObjecty2 = otherObject.pos.y + otherObject.height + range_
        
        if x1 < otherObjectx2 and x2 > otherObjectx1 and y1 < otherObjecty2 and y2 > otherObjecty1:
            return True
        else:
            return False
        
    def update(self, otherObjects):
        self.updatePos(otherObjects)
        super().update()