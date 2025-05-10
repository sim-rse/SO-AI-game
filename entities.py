import pygame, math, time
from objects import Object, MovingObject
from queue import PriorityQueue
from AI import AI, Waypoint

class Entity(MovingObject):
    def __init__(self, game, x, y, width = 0, height = 0, image = "placeholder.png", animationfile = None, scale = 1, health = 20, center = None):
        super().__init__(game, x, y, width, height, image, hasCollisionEnabled=True, affected_by_gravity=True, animationfile = animationfile, scale = scale, center = center)

        self.health = health
        self.strength = 2

        self.target = None
        self.list_of_targets = PriorityQueue()

        self.collider = False
        self.invincible = False
        self.jump_force = 16
        self.walkSpeed = 10
    
    def die(self):
        self.playanimation("die")
    
    def jump(self):
        if self.onGround:
            self.vel.y = -self.jump_force       #https://www.youtube.com/watch?v=bn3ZUCZ0vMo

    def getDamage(self, damage):
        if not self.invincible:
            self.health -= damage
        self.playanimation("get_damaged")

    def punch(self, otherEntity = None):
        self.playanimation("punch")
        if otherEntity:
            otherEntity.getDamage(self.strength)
        
    def shoot(self,target):
        self.game.add(Projectile(self.game, self.center.x, self.center.y - self.height, target = target, owner=self, exploding=True))

    def update(self):
        super().update()        #doet wat de update van de parent doet plus wat hieronder staat
        if self.health <= 0: 
            self.die()

    @property
    def jumpheight(self):
        return self.jump_force**2/(2*self.game.gravity)     #de maximumhoogte dat bereikt wordt (zie wet behoud van energie)
    @property
    def jumpwidth(self):
        return self.walkSpeed * (2*self.jump_force/self.game.gravity)       #de grootstse afstand dat het in een sprong kan afleggen



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
        self.game.remove(self)
        if self.exploding:
            self.game.add(Explosion(self.game, self.pos.x, self.pos.y, explosionrange = self.explosionrange, center=self.center))    #creert een explosie in het centrum van de projectile
        

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
    def __init__(self, game, x, y, scale=1, center=None, explosionrange = 100, strength = 30):
        super().__init__(game, x, y, scale = scale, animationfile = "animations/explosion.json", center=center)
        self.playanimation("explosion")
        self.static = True
        self.explosionrange = explosionrange
        self.strength = strength
        self.collisionsEnabled = False
        self.affected_by_gravity = False

        for ent in self.game.entities:
            if ent.collideswith(self, range_ = self.explosionrange):        #als de explosionrange 0 is krijgen enkel de geraakte entities damage (zoals bij kogels ofz)
                ent.getDamage(self.strength)

                knockback_direction = pygame.math.Vector2(ent.center.x - self.center.x,ent.center.y-self.center.y)
                print(knockback_direction.xy)
                if not knockback_direction.xy == [0,0]:
                    knockback_direction.normalize_ip()      #normaliseert de vector als het niet 0 is

                ent.vel = knockback_direction*self.strength*2       #*(10/self.getDistanceFrom(ent))
        
    def update(self):
        super().update()
        if self.animations.current.name == "default":        #als de explosion animation af is gaat het weer naar default (lege animatie) als het zo is kan de explosion weg 
            self.die()

    def getDamage(self, damage):
        pass

    def die(self):
        self.game.remove(self)

class Player(Entity):
    def __init__(self, game, x, y, width = 0, height = 0, image = "placeholder.png", animationfile = None, scale = 1):
        super().__init__(game, x, y, width, height, image, animationfile, scale)
        self.walkSpeed = 10
        self.shoot_key_hold = False
        self.sneaking = False
        self.health = 50

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
            self.sneaking = True
        else:
            self.sneaking = False
        if keys[pygame.K_SPACE]:
            self.punch()
        self.smoothSpeedChange(accel[0])        #indien we deze methode gebruiken blijft de speler staan indien we zowel links en rechts indrukken, en als je een toets loslaat heb je ook geen problemen met de richting die niet juist kan zijn
        
        
        if keys[pygame.K_a]:
            """if not self.last_press:
                self.last_press = time.time()
            if time.time() - self.last_press > 1:""" #zou er in de toekomst meer dan een enemy zijn dan moet je door de lijst van enemies kunnen gaan (en niet telkens de dichtbijzijnde krijgen)    , dit zijn de beginselen ervan, negeer het voorlopig
            
            list_of_targets = PriorityQueue()
            for i in [ent for ent in self.game.entities if not ent == self]:
                list_of_targets.put((self.pos.distance_to(i.pos), i))           #de afstand tussen self en de andere entity wordt als prioriteit gebruikt
            
            self.target = list_of_targets.get()[1]
        else:
            self.target = None

            
        if keys[pygame.K_z]:
            if not self.shoot_key_hold:
                self.shoot_key_hold = True
                if self.target:
                    target_position = self.target.pos
                elif self.flipSprite:
                    target_position = pygame.math.Vector2(self.pos.x-1, self.pos.y)
                else:
                    target_position = pygame.math.Vector2(self.pos.x + self.width + 1, self.pos.y)

                self.shoot(target_position)
        else:
            self.shoot_key_hold = False

    def animationHandler(self):
        if self.sneaking:
            self.playanimation("sneak")
        elif self.vel.y<0:
            self.playanimation("jump")
        elif self.onGround and self.vel.x !=0:
            self.playanimation("walk")
        elif self.vel.y>0:
            self.playanimation("fall")
        else:
            self.playanimation("default")

    def die(self):
        super().die()
        print('Oh noo (sad mario music)')
        self.game.scene = "game_over"
        self.game.scene_running = False
        
    def update(self):
        self.getKeyPress()
        super().update()

class Enemy(Entity):
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20):
        super().__init__(game, x, y, width, height, image, animationfile, scale, health)

        self.target = game.players[0]
        self.walkSpeed = 5
        self.ai = AI(game, self)

        self.path:list = self.ai.find_path(self.pos, self.target.pos)
        #self.path.append(Waypoint(game, self.target.pos.x, self.target.pos.y))
        self.current_waypoint = self.path.pop()
        
    def die(self):
        self.game.scene = "game_over"
        self.game.scene_running = False

    def movement(self):
        path = self.path
        
        pos = self.center_bottom
        waypoint = self.current_waypoint
        #print(waypoint.pos.x, pos.x)
        if len(path) !=0:
            if pos.distance_to(waypoint.pos) <= 5:
                self.current_waypoint = path.pop()
        
        if waypoint.pos.x + 1< pos.x:
            self.smoothSpeedChange(-self.walkSpeed)
            if waypoint.pos.y < pos.y and waypoint.pointType == "dropdown_R" and self.onGround:
                self.jump()
        elif waypoint.pos.x - 1> pos.x:
            self.smoothSpeedChange(self.walkSpeed)
            if waypoint.pos.y < pos.y and waypoint.pointType == "dropdown_L" and self.onGround:
                self.jump()
        else:
            self.smoothSpeedChange(0)
        
        


    def update(self):
        super().update()

        
        if self.game.debugging == True:
            for point in self.ai.waypoints:
                point.update()
            self.ai.show_path()
        self.movement()
        """self.direction = self.target.pos-self.pos
        if not self.direction == [0,0]:
            self.direction.normalize_ip()
        self.vel.x = self.walkSpeed*self.direction.x
"""
        
