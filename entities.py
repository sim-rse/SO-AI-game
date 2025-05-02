import pygame, math, time
from objects import Object, MovingObject
from queue import PriorityQueue

class Entity(MovingObject):
    def __init__(self, game, x, y, width = 0, height = 0, image = "placeholder.png", animationfile = None, scale = 1, health = 20):
        super().__init__(game, x, y, width, height, image, hasCollisionEnabled=True, affected_by_gravity=True, animationfile = animationfile, scale = scale)

        self.health = health
        self.strength = 2

        self.target = None
        self.list_of_targets = PriorityQueue()
    
    def die(self):
        self.playanimation("die")
    
    def jump(self):
        if self.onGround:
            self.vel.y = -14

    def getDamage(self, damage):
        self.health -= damage
        self.playanimation("get_damaged")

    def punch(self, otherEntity = None):
        self.playanimation("punch")
        if otherEntity:
            otherEntity.getDamage(self.strength)
        
    def shoot(self,target):
        self.game.add(Projectile(self.game, self.pos.x, self.pos.y, target = target))

    def update(self):
        super().update()        #doet wat de update van de parent doet plus wat hieronder staat
        if self.health <= 0: 
            self.die()

    def getDistanceFrom(self,otherEntity):
        return math.sqrt((otherEntity.pos.x - self.pos.x)**2+(otherEntity.pos.y-self.pos.y)**2)

class Projectile(Entity):
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20, target = None, owner = None, exploding = False):
        super().__init__(game, x, y, width, height, image, animationfile, scale, health)

        self.explosionrange = 5
        self.flyspeed = 2
        self.exploding = exploding

        self.owner = owner
        if target:
            self.target = target
        else:
            self.target = pygame.math.Vector2(0,0)
        self.direction = (self.target - self.pos).normalize()       #de richting naar waar het moet, genormaliseerd zodat we het kunnen gebruiken voor de componenten

        self.affected_by_gravity = 0
        self.collider = False
        self.collisionsEnabled = False

        self.vel.x = self.direction.x*self.flyspeed
        self.vel.y = self.direction.y*self.flyspeed

    def die(self):
        super().die()
        if self.exploding:
            self.game.add(Explosion(self.game, self.pos.x, self.pos.y, explosionrange = self.explosionrange, center=self.center))    #creert een explosie in het centrum van de projectile
        self.game.remove(self)
        

    def update(self):
        self.updatePos()
        for col in self.game.colliders:
            if col == self.owner:
                pass
            else:
                if self.collideswith(col):
                    if not self.exploding and isinstance(col, Entity):      #als het explodeert komt de damage van de explosion die optreedt bij self.die()
                        col.getDamage(self.strength)
                    self.die()
        self.blit()

class Explosion(Entity):
    def __init__(self, game, x, y, scale=1, center=None, explosionrange = 0, strength = 0):
        super().__init__(game, x, y, scale = scale, center=center)#, animationfile = "animations/explosion.png"
        self.playanimation("explosion")
        self.static = True
        self.explosionrange = explosionrange
        self.strength = strength
        for ent in self.game.entities:
            if ent.collideswith(self, range_ = self.explosionrange):        #als de explosionrange 0 is krijgen enkel de geraakte entities damage (zoals bij kogels ofz)
                ent.getDamage(self.strength)

                knockback_direction = pygame.math.Vector2(ent.pos.x - self.pos.x,ent.pos.y-self.pos.y).normalize()
                ent.vel = knockback_direction*self.strength*2*(10/self.getDistanceFrom(ent))

    
        

class Player(Entity):
    def __init__(self, game, x, y, width = 0, height = 0, image = "placeholder.png", animationfile = None, scale = 1):
        super().__init__(game, x, y, width, height, image, animationfile, scale)
        self.walkSpeed = 10
        #later komen de states en abilities hier

    def getKeyPress(self):
        keys = pygame.key.get_pressed()
        #beweging van de speler
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
        self.smoothSpeedChange(accel[0])        #indien we deze methode gebruiken blijft de speler staan indien we zowel links en rechts indrukken, en als je een toets loslaat heb je ook geen problemen met de richting die niet juist kan zijn
        
        
        if keys[pygame.K_a]:
            """if not self.last_press:
                self.last_press = time.time()
            if time.time() - self.last_press > 1:""" #zou er in de toekomst meer dan een enemy zijn dan moet je door de lijst van enemies kunnen gaan (en niet telkens de dichtbijzijnde krijgen)    , dit zijn de beginselen ervan, negeer het voorlopig
            
            list_of_targets = PriorityQueue()
            for i in [ent for ent in self.game.entities if not ent == self]:
                list_of_targets.put((self.getDistanceFrom(i), i))
            
            self.target = list_of_targets.get()
        else:
            self.target = None

            
        if keys[pygame.K_z]:
            if self.target:
                target_position = self.target.pos
            elif self.flipSprite:
                target_position = pygame.math.Vector2(self.pos.x-1, self.pos.y)
            else:
                target_position = pygame.math.Vector2(self.pos.x + self.width + 1, self.pos.y)
            
            self.shoot(target_position)

            


    def animationHandler(self):
        if self.vel.y<0:
            self.playanimation("jump")
        elif self.onGround and self.vel.x !=0:
            self.playanimation("walk")
        elif self.vel.y>0:
            self.playanimation("fall")
        else:
            self.playanimation("default")
        
    def update(self):
        self.getKeyPress()
        super().update()

class Enemy(Entity):
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20):
        super().__init__(game, x, y, width, height, image, animationfile, scale, health)

        self.target = None 
