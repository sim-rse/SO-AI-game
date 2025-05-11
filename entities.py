import pygame, time, random
from objects import MovingObject
from queue import PriorityQueue
from AI import AI, Waypoint
from powerup import PowerUp

class Entity(MovingObject):
    def __init__(self, game, x, y, width = 0, height = 0, image = "placeholder.png", animationfile = None, scale = 1, health = 20, center = None):
        super().__init__(game, x, y, width, height, image, hasCollisionEnabled=True, affected_by_gravity=True, animationfile = animationfile, scale = scale, center = center)

        self.health = health
        self.strength = 2

        self.target = None
        self.list_of_targets = PriorityQueue()

        self.collider = False
        self.invincible = False
        self.jump_force = 18
        self.walkSpeed = 12

        self.punch_cooldown = 0.5
        self.shoot_cooldown = 1 

        self.last_punch_time = 0
        self.last_shoot_time = 0
        self.last_action_time = 0

        self.current_action = None
        self.current_action_length = 0

        self.protecting = False

        self.birth_time = time.time()
    
    def die(self):
        self.playanimation("die")
    
    def jump(self):
        if self.onGround:
            self.vel.y = -self.jump_force       #https://www.youtube.com/watch?v=bn3ZUCZ0vMo

    def getDamage(self, damage):
        if not (self.invincible or self.protecting):
            self.health -= damage
        self.playanimation("get_damaged")

    def punch(self):
        self.playanimation("punch")
        for otherEntity in self.game.entities:
            if otherEntity is not self and self.collideswith(otherEntity, range_= 10):
                otherEntity.getDamage(self.strength)
        
    def shoot(self,target):
        self.game.add(Projectile(self.game, self.pos.x, self.pos.y, target = target, owner=self, exploding=True, scale=0.5))

    def update(self):
        super().update()        #doet wat de update van de parent doet plus wat hieronder staat
        if self.health <= 0: 
            self.die()
        if self.vel.x < 0:
            self.flipSprite = True          #bij het op de scherm zetten van de sprites worden ze gespiegeld zodat ze naar links kijken (dit blijft zo totdat er weer op rechts wordt gedrukt)
        elif self.vel.x > 0:
            self.flipSprite = False

    @property
    def jumpheight(self):
        return self.jump_force**2/(2*self.game.gravity)     #de maximumhoogte dat bereikt wordt (zie wet behoud van energie)
    @property
    def jumpwidth(self):
        return self.walkSpeed * (2*self.jump_force/self.game.gravity)       #de grootstse afstand dat het in een sprong kan afleggen
    
    @property
    def ready_to_punch(self):
        return time.time() - self.last_punch_time > self.punch_cooldown

    @property
    def ready_to_shoot(self):
        return time.time() - self.last_shoot_time > self.shoot_cooldown
    
    @property
    def action_cooldown(self):
        diff = time.time() - self.last_action_time
        if self.current_action_length - diff > 0:
            return self.current_action_length - diff
        else: 
            return 0
    
    @property
    def punching(self):                                 #dit is voor de animaties, de cooldowns voor de volgende punch of shoot zijn de ready_to_[...]
        if time.time() - self.last_punch_time < 0.3:
            return True
        return False
        
    @property
    def shooting(self):
        if time.time() - self.last_shoot_time < 0.4:
            return True
        return False

class Projectile(Entity):
    def __init__(self, game, x, y, width=0, height=0, image="images/bomb.png", animationfile=None, scale=1, health=20, target = None, owner = None, exploding = False):
        super().__init__(game, x, y, width, height, image, animationfile, scale, health)

        self.explosionrange = 5
        self.flyspeed = 5
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
        for col in self.game.colliders + self.game.fighters:
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
                #print(knockback_direction.xy)
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
    def __init__(self, game, x, y, width = 0, height = 0, image = "placeholder.png", animationfile = None, scale = 1, health = 100):
        super().__init__(game, x, y, width, height, image, animationfile, scale)
        self.walkSpeed = 10
        self.shoot_key_hold = False
        self.sneaking = False
        self.health = health

        self.last_punch_time = 0

    def getKeyPress(self):
        keys = pygame.key.get_pressed()
        #beweging van de speler
        accel = [0,0]
        if not self.protecting:     #als de player zich beschermt kan hij niets anders doen
            if keys[pygame.K_RIGHT]:
                accel[0] += self.walkSpeed
            if keys[pygame.K_LEFT]:
                accel[0] += -self.walkSpeed
            if keys[pygame.K_UP]:
                self.jump()                 #te vinden bij Entity class
            
            if keys[pygame.K_SPACE]:
                if time.time() - self.last_punch_time>0.5: 
                    self.punch()
                    self.last_punch_time = time.time()

        self.smoothSpeedChange(accel[0])        #indien we deze methode gebruiken blijft de speler staan indien we zowel links en rechts indrukken, en als je een toets loslaat heb je ook geen problemen met de richting die niet juist kan zijn
        
        
        if keys[pygame.K_DOWN]:
            self.sneaking = True
            self.protecting = True
        else:
            self.sneaking = False
            self.protecting = False
                
        if keys[pygame.K_a]:
            """if not self.last_press:
                self.last_press = time.time()
            if time.time() - self.last_press > 1:""" #zou er in de toekomst meer dan een enemy zijn dan moet je door de lijst van enemies kunnen gaan (en niet telkens de dichtbijzijnde krijgen)    , dit zijn de beginselen ervan, negeer het voorlopig
            
            list_of_targets = PriorityQueue()
            for i in [ent for ent in self.game.enemies if not ent == self]:
                list_of_targets.put((self.pos.distance_to(i.pos), i))           #de afstand tussen self en de andere entity wordt als prioriteit gebruikt
            
            self.target = list_of_targets.get()[1]
        else:
            self.target = None

            
        if keys[pygame.K_z]:
            if not self.shoot_key_hold and not self.protecting:
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
        if self.shooting:
            self.playanimation("shoot")
        elif self.punching:
            self.playanimation("punch")
        elif self.protecting:
            self.playanimation("protect")
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
        self.game.scene = "game_over"
        self.game.scene_running = False
        self.game.winner = "Enemy"
        
    def update(self):
        self.getKeyPress()
        super().update()

class Enemy(Entity):
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20):
        super().__init__(game, x, y, width, height, image, animationfile, scale, health)

        self.target = game.players[0]
        self.walkSpeed = 5
        self.ai = AI(game, self)
        self.getPath(self.target)
        
        #self.path.append(Waypoint(game, self.target.pos.x, self.target.pos.y))
        if len(self.path)>0:
            self.current_waypoint = self.path.pop()
        else:
            self.current_waypoint = Waypoint(game,x,y)
        
    def die(self):
        self.game.scene = "game_over"
        self.game.scene_running = False
        self.game.winner = f"Player"

    def animationHandler(self):
        if self.shooting:
            self.playanimation("shoot")
        elif self.punching:
            self.playanimation("punch")
        elif self.protecting:
            self.playanimation("protect")
        elif self.vel.y<0:
            self.playanimation("jump")
        elif self.onGround and self.vel.x !=0:
            self.playanimation("walk")
        elif self.vel.y>0:
            self.playanimation("fall")
        else:
            self.playanimation("default")

    def movement(self):
        path = self.path
        
        pos = self.center_bottom
        waypoint = self.current_waypoint

        if len(path) !=0:
            if pos.distance_to(waypoint.pos) <= 5 and self.onGround:
                self.current_waypoint = path.pop()
            for num, i in enumerate(path):
                if pos.distance_to(waypoint.pos) > pos.distance_to(i.pos):
                    self.path = path[:num]
                    self.current_waypoint = path.pop()
        else:
            self.getPath(self.target)
        waypoint = self.current_waypoint
        
        if waypoint.pos.x + 10< pos.x:                                          #als de enemy in een 10 pixel range is kan het stoppen (dit voorkomt heen en weer gaan)
            self.smoothSpeedChange(-self.walkSpeed)
            if waypoint.pos.y < pos.y and self.jumpwidth > abs(self.pos.x - waypoint.pos.x) and self.onGround:           #and waypoint.pointType == "dropdown_R"
                self.jump()
        elif waypoint.pos.x - 10> pos.x:
            self.smoothSpeedChange(self.walkSpeed)
            if waypoint.pos.y < pos.y and self.jumpwidth > abs(self.pos.x - waypoint.pos.x) and self.onGround:           #and waypoint.pointType == "dropdown_L"
                self.jump()
        else:
            self.smoothSpeedChange(0)
    
    def getPath(self, target):
        path  = self.ai.find_path(self.center_bottom, target.center_bottom)
        if path != []:
            self.path:list = path
            self.current_waypoint = self.path.pop()
        else:
            self.path = []
            print("Path not found!!")

    def show_path(self):
        try:
            pygame.draw.lines(self.game.screen, (0,255,0), False, [point.pos for point in self.path], width=5)
        except:
            pass

    def actionHandler(self):
        if self.action_cooldown == 0:
            action = self.get_action()
            #initialiseren van de acties
            match action:
                case "attack":
                    self.getPath(self.target)
                    self.current_action_length = 4
                case "idle":
                    self.current_action_length = 2
                case "protect":
                    self.current_action_length = 1.5
                case "runaway":
                    furthest = None
                    for i in self.ai.waypoints:
                        if not furthest or i.pos.distance_to(self.target.pos) > furthest.pos.distance_to(self.target.pos):
                            furthest = i
                    if furthest:
                        self.getPath(furthest)
                    self.current_action_length = 3
                case "shoot":
                    self.current_action_length = 2
                    self.shoot(self.target.pos)
                case "powerup":
                    closest = None
                    for i in self.game.powerups:
                        if not closest or i.pos.distance_to(self.pos) < closest.pos.distance_to(self.pos):
                            closest = i
                    if closest:
                        self.getPath(closest)
                    self.current_action_length = 10
                    
            self.last_action_time = time.time()
            self.current_action = action

        action = self.current_action        
        self.protecting = False
        #updaten van de acties
        match action:
                case "attack":
                    if len(self.path)<1:
                        self.getPath(self.target)
                    #print(self.path)
                    self.movement()
                    if self.collideswith(self.target):
                        self.punch()
                        self.current_action_length = 0
                case "idle":
                    self.smoothSpeedChange(0)
                case "protect":
                    self.protecting = True
                    self.smoothSpeedChange(0)
                case "runaway":
                    self.movement()
                case "shoot":
                    self.smoothSpeedChange(0)
                case "powerup":
                    self.movement()

    def get_action(self):
        #if actioncooldown is 0: choose new action
        distance_from_target = self.pos.distance_to(self.target.pos)

        diff = self.target.health - self.health 

        #de health diff's vertellen hoeveel hp de enemy of de speler minder heeft dan de andere (alles < 0 wordt 0)
        if diff<0: 
            player_health_diff = -diff
            health_diff = 0
        else:
            health_diff = diff
            player_health_diff = 0

        powerup_spawned = [i for i in self.game.objects if isinstance(i, PowerUp)] != []
            
        powerup_weight = powerup_spawned*health_diff#*self.pos.distance_to powerup ofz

        if distance_from_target < 300:
            attack_weight = self.ready_to_punch * 30 + player_health_diff*2
            runaway_weight = (not self.ready_to_punch)*2*health_diff
            protect_weight = (not self.ready_to_punch)*10 + health_diff
            return random.choices(["attack", "idle", "protect", "runaway"], weights = [attack_weight, 5,protect_weight, runaway_weight]).pop()      #pop omdat het een list returnt
        elif 300 < distance_from_target < 800:
            attack_weight = self.ready_to_punch * 20 + player_health_diff*2
            runaway_weight = (not (self.ready_to_punch or self.ready_to_shoot))*health_diff
            protect_weight = (not (self.ready_to_punch or self.ready_to_shoot))*5 + health_diff
            shoot_weight = self.ready_to_shoot * 10 + health_diff
            return random.choices(["attack", "idle", "protect", "runaway", 'shoot', "powerup"], weights = [attack_weight, 5,protect_weight, runaway_weight, shoot_weight, powerup_weight]).pop()
        else:
            attack_weight = self.ready_to_punch * 1
            shoot_weight = self.ready_to_shoot * 20 + health_diff
            return random.choices(["attack", "idle", 'shoot', "powerup"], weights = [attack_weight, 10, shoot_weight, powerup_weight]).pop()

    def update(self):
        super().update()
        if self.game.debugging == True:
            for point in self.ai.waypoints:
                point.update()              #tekent de punten
            self.show_path()                #toont de pad tussen de punten
        self.actionHandler()                #beslist wat de enemy doet als actie (blijft staan, valt aan, enz)
        
