import pygame
import json
import math

from utils import checkDict
from spritesheet import Spritesheet
from animations import Animations

class Object:
    def __init__(self, game, x, y, width = 0, height = 0, image = None, color = 'blue', animationfile = None, scale = 1, center = None):        #image geeft een pad naar de afbeeldin, color = Als er geen afbeelding is, maak een gekleurd vierkant.
        # Initialiseer het object met standaardwaarden zoals positie, grootte, afbeelding, kleur, animaties, etc.
        self.game = game
        self.pos = pygame.math.Vector2(x,y) #Zet de positie van het object op basis van de opgegeven x, y coördinaten.
        self.animated = False
        self.static = True  # Dit object is statisch, het beweegt niet.
        self.collider = True        #is het voor de anderen als een vast object beschouwd (of de collisions voor deze object enabled zijn wordt in MovinObject ingesteld)
        
        if animationfile: # Als er een animatiebestand is opgegeven:
            self.animated = True  #Zet de animatie-instelling op True.
            #print(f"animating {self}")
            self.animations = Animations() # Maak een Animations object aan.
            self.loadAnimations(animationfile,scale) #Laad animaties uit het bestand.
            self.animations.playDefault() # Speel de standaardanimatie.
            self.texture = self.animations.image # Zet de afbeelding van het object op de huidige animatie.
            #print(f"type texture :{type(self.texture)}")
        #elif os.path.exists(pad naar animationfile met de naam van de classe zodat we het niet telkens moeten bijgeven)
        elif image: # Als er geen animatie is maar wel een afbeelding:
            print(image)
            self.texture = pygame.image.load(image) #laden van de texture (jargon voor afbeelding fyi)
            self.texture = pygame.transform.scale(self.texture, (self.width*scale, self.height*scale)) # Schaal de afbeelding.
            
            if height !=0 or width !=0:             #zou je een width en height geven dan kan je de speler herschalen
                self.texture = pygame.transform.scale(self.texture, (width, height))
            #self.animations.load("default",[self.texture])
        else: # Als er geen afbeelding of animatie is:
            self.texture = pygame.Surface((width,height)) # Maak een vlak oppervlak.
            self.texture.fill(color) # vul de opgegeven vlak met de opgegeven kleur 
            #print(f"filled surface with color: {color}")

        if center: # Als er een centrum is opgegeven:
            self.center = center # Zet het centrum van het object.

        self.flipSprite = False  # Standaard wordt het object niet gespiegeld.
        

    @property   #Je hoeft self.width en self.height niet zelf bij te houden, dat komt van het plaatje (texture).
    def width(self):
        return self.texture.get_width() # Haal de breedte op van de afbeelding of het oppervlak.
    
    @property
    def height(self):
        return self.texture.get_height() # Haal de hoogte op van de afbeelding of het oppervlak.

    @property # Maak een property voor de hitbox van het object (voor botsingen).   
    def hitbox(self):       #geeft de coordinaten van de hoekpunten terug, handig voor de collisions
        return {"top":self.pos.y,"bottom":self.pos.y+self.height,"left":self.pos.x,"right":self.pos.x+self.width}
    
    #de onderste properties worden gebruikt om het ergens in de code gemakkelijker te maken, het zijn de coordinaten van de zwaartepunt centrum op de grond
    @property # Bereken het centrum van het object.
    def center(self):
        return pygame.math.Vector2((self.hitbox['left']+self.hitbox['right'])/2 , (self.hitbox['top']+self.hitbox['bottom'])/2)
    @center.setter #Zet de waarde voor het centrum van het object.
    def center(self, value: pygame.math.Vector2):
        self.pos.x = value.x - self.width/2
        self.pos.y = value.y - self.height/2

    @property # Bereken het centrum van de onderkant van het object.
    def center_bottom(self):
        return pygame.math.Vector2((self.hitbox['left']+self.hitbox['right'])/2 , self.hitbox['bottom'])
    @center_bottom.setter # Zet de waarde voor het centrum van de onderkant van het object.
    def center_bottom(self, value: pygame.math.Vector2):
        self.pos.x = value.x - self.width/2
        self.pos.y = value.y - self.height

    def collideswith(self, otherObject, range_ = 0):        #van WPO6 gekopieerd, ma we werken hier enkel met rechthoeken
        #basically de hitboxen van de twee objecten berekenen, afhankelijk van wat minder zwaar is voor de computer houden wij deze methode of de hitbox() methode
        x1 = self.pos.x  # Bepaal de linker x-coördinaat van de hitbox.
        y1 = self.pos.y # Bepaal de bovenste y-coördinaat van de hitbox.
        x2 = self.pos.x + self.width # Bepaal de rechter x-coördinaat van de hitbox.
        y2 = self.pos.y + self.height # Bepaal de onderste y-coördinaat van de hitbox.
        
        # Bepaal de hitbox van het andere object, rekening houdend met een mogelijke range (d.w.z. hoe ver je object mag zijn voor botsing).
        otherObjectx1 = otherObject.pos.x - range_  #Met range_ kun je oof zien of de self zich op een bepaalde afstand van otherObject bevindt                 
        otherObjecty1 = otherObject.pos.y - range_
        otherObjectx2 = otherObject.pos.x + otherObject.width + range_
        otherObjecty2 = otherObject.pos.y + otherObject.height + range_
        
        # Als de hitboxen overlappen, geef dan True terug (er is een botsing).
        if x1 < otherObjectx2 and x2 > otherObjectx1 and y1 < otherObjecty2 and y2 > otherObjecty1:
            return True
        else:
            return False # Geen botsing.

    def getDistanceFrom(self,otherObject): # Bereken de afstand tussen dit object en een ander object.
        return math.sqrt((otherObject.pos.x - self.pos.x)**2+(otherObject.pos.y-self.pos.y)**2) #Pythagoras

    def blit(self): # Teken het object op het scherm.
        screen = self.game.screen
        if self.flipSprite:  # Als het object gespiegeld moet worden:
            screen.blit(pygame.transform.flip(self.texture, True, False), (self.pos.x, self.pos.y)) # Teken de gespiegeld afbeelding.
        else: # Teken de afbeelding normaal.
            screen.blit(self.texture, (self.pos.x, self.pos.y)) #bij fotos werkt het licht anders dan bij vormen ma doet hetzelfde als pygame.draw.rect(...) bijvoorbeeld
    
    def update(self,otherobjects = None): # Update de status van het object.
        if self.animated:  # als het object een animatie heeft: 
            self.animationHandler()   # Werk de animatie bij.
            self.animations.update()  #update de animatie 
            self.texture = self.animations.image #Zet de huidige animatie-afbeelding als texture.
        self.blit() #Teken het object op het scherm.
        
    def loadAnimations(self, file, scale=1):       #scale verandert de groote van alle frames met factor scale, wordt gebruikt door  de makeAnimation() methode
    #Functie om animaties te laden uit een JSON-bestand;
        with open(file) as f: #Opent het bestand (meestal een .json) dat animatiegegevens bevat
            data = json.load(f) # Laad de gegevens uit het bestand.

        for sheet in data: #Loop door alle animaties in het bestand.
            #print(f"[info: sheet] {sheet}")
            sheet_scale = checkDict(sheet,"scale",scale) # Verkrijg de schaal van de animatie.
            colorkey = checkDict(sheet,"colorkey", (0,0,0)) #verkrijg de kleur die als transparant moet worden behandeld.
            spritesheet = Spritesheet(path = sheet["spritesheet"], width = sheet["width"], height = sheet["height"], colorkey = tuple(colorkey))        #Maakt een nieuw Spritesheet-object aan

            for animation_name, animation_data in sheet["animations"].items():       #zonder de .items() krijg je alleen de namen van de keys en niet hun waarden erbij
                #print(animation_name, animation_data)

                temp_scale = checkDict(animation_data,"scale", sheet_scale)      # Verkrijg de schaal van de animatie.
                anim = spritesheet.makeAnimation(frames=animation_data["frames"],column=animation_data["column"], row=animation_data["row"], direction=animation_data["direction"], scale = temp_scale)     # deze maakt een lijst van frames voor de animaties 
                next = checkDict(animation_data, "next", None)  #Welke animatie moet erna komen (optioneel)
                loop = checkDict(animation_data, "loop", False) # Moet de animatie in een lus herhalen? (True/False)
                self.animations.load(name = animation_name, animation = anim, loop = loop, next=next)     # Laad de animatie in. #next is ook een (onnodige) functie, dus ideaal de naam veranderen in de toekomst
    
    def playanimation(self, animation):     # Speelt een bepaalde animatie af
        if self.animated:
            self.animations.play(animation)

    def updateAnimation(self):           #we hebben die twee hier nodig om errors te vermijden, ze worden echter bij child klassen gebruikt
        pass

    def animationHandler(self):        
        pass

class Wall(Object): # Klasse voor een muur-object, dat een statisch object is.
    def __init__(self, game, x, y, width=0, height=0):
        super().__init__(game, x, y, width, height, color = (0,0,0,0)) # Roep de Object constructor aan met de juiste kleur voor een muur.
        

class Empty(Object): # Klasse voor een leeg object, bijvoorbeeld een object zonder collider.
    def __init__(self, game, x=0, y=0, width=0, height=0, center_bottom = None):
        super().__init__(game, x, y, width, height, color = (0,0,0,0))  # Roep de Object constructor aan met de juiste kleur.
        self.collider = False  # Zet de collider uit voor dit object.
        if center_bottom:
            self.center_bottom = center_bottom # Zet het centrum van de onderkant als dat nodig is.

class MovingObject(Object): # Klasse voor een object dat beweegt, zoals een speler of vijand.
    def __init__(self, game, x, y, width=0, height=0, image=None, hasCollisionEnabled=False, affected_by_gravity=True, color='blue', animationfile=None, scale=1, center = None):
        super().__init__(game, x, y, width, height, image, color, animationfile, scale, center = center) # Roep de Object constructor aan met de juiste waarden.

        self.velX = 0           
        self.velY = 0
        self.vel = pygame.math.Vector2(0,0)     #snelheid (velocity)
        self.acc = pygame.math.Vector2(0,0)           #acceleratie = versnelling

        self.static = False # Dit object is niet statisch, het beweegt.
        self.gravity = self.game.gravity
        self.collisionsEnabled = hasCollisionEnabled #Zet in of dit object botsingen heeft.
        self.affected_by_gravity = affected_by_gravity  #heeft zwaartekracht invloed
        self._gravity = self.game.gravity          #sterkte van de zwaartekracht (kan ook op 0 worden ingesteld, dan is er momenteel geen zwaartekracht)

        self.onGround = False # Geef aan dat het object niet op de grond staat.

    """@property
    def gravity(self):
        return self.game.gravity
    @property.setter
    def gravity(self):
        pass"""
    
    def updatePos(self, otherObjects=None): # Update de positie van het object.
        dt = self.game.dt        #tijdsverschil tussen de frames in seconden om beweging onafhankelijk van de fps te maken (voorlopig heb ik het op 1 gezet want de game was anders veel te traag)
        otherObjects = [obj for obj in self.game.colliders if not obj == self] # Verkrijg alle andere objecten behalve dit object.

        # Eerst kijken naar de x as
        self.vel.x += self.acc.x*dt  #nieuwe snelheid en positie
        self.pos.x += self.vel.x*dt
        
        # Controleer op botsingen met andere objecten.
        if self.collisionsEnabled:
            for otherObject in otherObjects:
                if self.collideswith(otherObject):# Als er een botsing is:
                    if self.vel.x > 0:
                        self.pos.x = otherObject.hitbox["left"] - self.width # Zet de positie van het object als het bots met de rechterkant van een ander object.
                    elif self.vel.x < 0:
                        self.pos.x = otherObject.hitbox["right"] # Zet de positie van het object als het bots met de linkerkant van een ander object.
                    self.vel.x = 0 # Zet de snelheid naar 0 als er een botsing is

        # Werk de y-positie bij met zwaartekracht.
        if self.affected_by_gravity:
            self.vel.y += (self.acc.y+self.game.gravity)*dt  #Voeg de zwaartekracht toe aan de snelheid.
        else:
            self.vel.y += self.acc.y*dt #Als er geen zwaartekracht is, voeg dan alleen de versnelling toe.
        self.pos.y += self.vel.y*dt  #Werk de y-positie bij.
        
        self.onGround = False #neemt aan dat de object niet op de grond is, maar als er wel vanonder collision is wordt het wel als op de grond beschouwd (zie enkele lijnen onder)

        # Controleer botsingen voor de y-as.
        if self.collisionsEnabled:
            for otherObject in otherObjects:
                if self.collideswith(otherObject):
                    if self.vel.y > 0:
                        self.onGround = True # Als er een botsing is van onder, beschouw het object als 'op de grond'.
                        self.pos.y = otherObject.hitbox["top"] - self.height #Zet de y-positie boven de botsing.
                    elif self.vel.y < 0:
                        self.pos.y = otherObject.hitbox["bottom"] #Zet de y-positie onder de botsing.
                    self.vel.y = 0 # Zet de snelheid op 0 als er een botsing is.

    def smoothSpeedChange(self,targetValue): # Maak een vloeiende verandering in snelheid.
        difference = targetValue - self.vel.x # Bereken het verschil tussen de huidige snelheid en het doel.
        if abs(difference)>0.1:   # Als het verschil groot genoeg is:
            if self.onGround:
                force = 0.4 # Meer kracht op de grond.
            else: 
                force = 0.2 # Minder kracht in de lucht.
            self.acc.x = difference*force # Pas de versnelling aan op basis van het verschil.
        else:
            self.acc.x = difference  # Zet de versnelling gelijk aan het verschil om soepel te stoppen.

        
    def update(self): #update de beweging van het object
        if not self.static:  #als het object niet statisch is
            self.updatePos() #werk dan de positie bij
        super().update() # Update het object via de parent klasse (Object).