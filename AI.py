from objects import Empty
import pygame


class Waypoint():
    def __init__(self, game, x, y):
        self.game = game
        self.pos = pygame.math.Vector2(x,y)
        self.texture = pygame.image.load('images/UI/waypoint.png')

    def update(self):
        if self.game.debugging:
            self.game.screen.blit(self.texture , (self.pos.x - self.texture.get_width()/2, self.pos.y - self.texture.get_height()))

def raycast(game, start:pygame.math.Vector2, end:pygame.math.Vector2):        #gebruik het ENKEL voor rechten evenwijdig met x of y as
    height = end.y - start.y
    width = end.x - start.x
    ray = Empty(game, start.x ,start.y, width, height)
    for col in game.colliders:
        if ray.collideswith(col):
            if start.y>end.y and width == 0: return pygame.math.Vector2(start.x,col.hitbox["bottom"])           #top en bottom omgekeerd omdat oorsprong in linkerbovenhoek staat bij pygame
            elif start.y<end.y and width == 0: return pygame.math.Vector2(start.x,col.hitbox["top"])
            elif start.x>end.x and height == 0: return pygame.math.Vector2(col.hitbox["right"],start.y)
            elif start.x<end.x and height == 0: return pygame.math.Vector2(col.hitbox["left"],start.y)
            else: return None

def thing(game, entity):        #we gebruiken entity om de min hoogte bovenop de waypoints te hebben
    temp_waypoints = []
    #maakt waypoints aan bij alle tophoeken van de colliders
    for obj in game.colliders:
        left_top = Empty(game, center_bottom=obj.pos , width=entity.width , height=entity.height)
        right_top = Empty(game, center_bottom=pygame.math.Vector2(obj.pos.x+obj.width, obj.pos.y), width=entity.width, height=entity.height)

        varL = True
        varR = True
        #kijkt of de entity wel op de plaats van de waypoint kan staan 
        for col in game.colliders:
            if left_top.collideswith(col):
                varL = False
            if right_top.collideswith(col):
                varR = False
        #als het wel plaats heeft, wordt er een waypoint aangemaakt
        if varL:
            temp_waypoints.append(Waypoint(game, left_top.center_bottom.x, left_top.center_bottom.y))
            print(f'Linker Waypoint aangemaakt voor object:{obj} op positie: {left_top.center_bottom.x} , {left_top.center_bottom.y}')
        if varR:
            temp_waypoints.append(Waypoint(game, right_top.center_bottom.x, right_top.center_bottom.y))
            print(f'Rechter Waypoint aangemaakt voor object:{obj}, met pos van objec: {obj.pos} en pos van waypoint: {right_top.center_bottom.x} , {right_top.center_bottom.y}')
    
    waypoints = []
    for waypoint in temp_waypoints:
        intersect = raycast(game, waypoint.pos, pygame.math.Vector2(waypoint.pos.x, waypoint.pos.y + 10000))
        if intersect != None:
            waypoints.append(Waypoint(game,intersect.x, intersect.y))
        waypoints.append(waypoint)

            
    return waypoints

        