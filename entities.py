import pygame
from objects import Object, MovingObject

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
