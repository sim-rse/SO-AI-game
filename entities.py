import pygame, math, time
from objects import Object, MovingObject
from queue import PriorityQueue
from AI import AI, Waypoint

class Entity(MovingObject):
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20, center=None):
        super().__init__(game, x, y, width, height, image, hasCollisionEnabled=True, affected_by_gravity=True, animationfile=animationfile, scale=scale, center=center)

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
            self.vel.y = -self.jump_force  # https://www.youtube.com/watch?v=bn3ZUCZ0vMo

    def getDamage(self, damage):
        if not self.invincible:
            self.health -= damage
        self.playanimation("get_damaged")

    def punch(self, otherEntity=None):
        self.playanimation("punch")
        if otherEntity:
            otherEntity.getDamage(self.strength)

    def shoot(self, target):
        self.game.add(
            Projectile(
                self.game,
                self.center.x,
                self.center.y - self.height,
                target=target,
                owner=self,
                exploding=True,
                image="images/fireball.png"  # Pass the fireball image here
            )
        )

    def update(self):
        super().update()  # Does what the parent update does plus the following
        if self.health <= 0:
            self.die()

    @property
    def jumpheight(self):
        return self.jump_force**2 / (2 * self.game.gravity)  # Maximum height reached (physics)

    @property
    def jumpwidth(self):
        return self.walkSpeed * (2 * self.jump_force / self.game.gravity)  # Maximum jump distance


class Projectile(Entity):
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20, target=None, owner=None, exploding=False):
        # Laad de afbeelding als het een pad is
        if isinstance(image, str):
            loaded_image = pygame.image.load(image).convert_alpha()
        else:
            loaded_image = image  # als het al een pygame.Surface is

        super().__init__(game, x, y, width, height, loaded_image, animationfile, scale, health)

        self.explosionrange = 5
        self.flyspeed = 2
        self.exploding = exploding
        self.owner = owner

        self.target = target or pygame.math.Vector2(0, 0)
        self.direction = (self.target - self.pos).normalize()

        self.affected_by_gravity = 0
        self.collider = False
        self.collisionsEnabled = False

        self.vel.x = self.direction.x * self.flyspeed
        self.vel.y = self.direction.y * self.flyspeed
        


    def die(self):
        super().die()
        self.game.remove(self)
        if self.exploding:
            self.game.add(Explosion(self.game, self.pos.x, self.pos.y, explosionrange=self.explosionrange, center=self.center))  # Create an explosion at the center of the projectile

    def update(self):
        self.updatePos()
        for col in self.game.colliders:
            if col == self.owner:
                pass
            else:
                if self.collideswith(col):
                    if not self.exploding and isinstance(col, Entity):  # If it explodes, damage comes from the explosion
                        col.getDamage(self.strength)
                    self.die()
        self.blit()


class Explosion(Entity):
    def __init__(self, game, x, y, scale=1, center=None, explosionrange=100, strength=30):
        super().__init__(game, x, y, scale=scale, animationfile="animations/explosion.json", center=center)
        self.playanimation("explosion")
        self.static = True
        self.explosionrange = explosionrange
        self.strength = strength
        self.collisionsEnabled = False
        self.affected_by_gravity = False

        for ent in self.game.entities:
            if ent.collideswith(self, range_=self.explosionrange):  # If explosionrange is 0, only entities hit directly take damage
                ent.getDamage(self.strength)

                knockback_direction = pygame.math.Vector2(ent.center.x - self.center.x, ent.center.y - self.center.y)
                if not knockback_direction.xy == [0, 0]:
                    knockback_direction.normalize_ip()  # Normalize the vector if it's not 0

                ent.vel = knockback_direction * self.strength * 2  # Apply knockback

    def update(self):
        super().update()
        if self.animations.current.name == "default":  # If the explosion animation is done, remove the explosion
            self.die()

    def getDamage(self, damage):
        pass

    def die(self):
        self.game.remove(self)


class Player(Entity):
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1):
        super().__init__(game, x, y, width, height, image, animationfile, scale)
        self.walkSpeed = 10
        self.shoot_key_hold = False
        self.sneaking = False
        self.health = 50

    def shoot(self, target):
        self.game.add(
            Projectile(
                self.game,
                self.center.x,
                self.center.y - self.height,
                target=target,
                owner=self,
                exploding=True,
                image="images/fireball.png"  # Pass the fireball image here
            )
        )

    def getKeyPress(self):
        keys = pygame.key.get_pressed()
        accel = [0, 0]
        if keys[pygame.K_RIGHT]:
            accel[0] += self.walkSpeed
            self.flipSprite = False
        if keys[pygame.K_LEFT]:
            accel[0] += -self.walkSpeed
            self.flipSprite = True
        if keys[pygame.K_UP]:
            self.jump()
        if keys[pygame.K_DOWN]:
            self.sneaking = True
        else:
            self.sneaking = False
        if keys[pygame.K_SPACE]:
            self.punch()
        self.smoothSpeedChange(accel[0])

        if keys[pygame.K_z]:
            if not self.shoot_key_hold:
                self.shoot_key_hold = True
                if self.target:
                    target_position = self.target.pos
                elif self.flipSprite:
                    target_position = pygame.math.Vector2(self.pos.x - 1, self.pos.y)
                else:
                    target_position = pygame.math.Vector2(self.pos.x + self.width + 1, self.pos.y)

                self.shoot(target_position)
        else:
            self.shoot_key_hold = False

    def animationHandler(self):
        if self.sneaking:
            self.playanimation("sneak")
        elif self.vel.y < 0:
            self.playanimation("jump")
        elif self.onGround and self.vel.x != 0:
            self.playanimation("walk")
        elif self.vel.y > 0:
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
        self.path: list = self.ai.find_path(self.pos, self.target.pos)
        self.current_waypoint = self.path.pop()

        # Add the current_action attribute
        self.current_action = "idle"  # Default action
        self.action_cooldown = 0  # Cooldown for actions

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
        
        if self.action_cooldown > 0:
            self.action_cooldown -= 1
        else:
            self.current_action = "idle"  # Reset to idle when cooldown ends