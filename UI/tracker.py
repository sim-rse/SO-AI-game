from objects import Object
import pygame


class Tracker(Object):
    def __init__(self, game, entity, color='blue', scale=1):
        self.entity = entity
        match color:
            case "blue":
                animationfile = "animations/tracker/blue.json"
            case "red":
                animationfile = "animations/tracker/red.json"
            case _:
                animationfile = "animations/tracker/blue.json"

            
        if entity.target:
            x = entity.target.center.x
            y = entity.target.pos.y - 10
        else:
            x = entity.pos.x
            y = entity.pos.y
        super().__init__(game, x, y, scale = scale, animationfile=animationfile, center = pygame.math.Vector2(x,y))  #de x,y wordt maar efkens gebruikt en dan direct vervangen door de coors voor de center
        self.collider = False
        self.static = True



    def update(self):
        if self.entity.target:
            self.center = pygame.math.Vector2(self.entity.target.center.x, self.entity.target.hitbox["top"] - 10)
            self.playanimation("show")
        else:
            self.playanimation("empty") #als er geen target is wordt de tracker onzichtbaar
        super().update()
         

