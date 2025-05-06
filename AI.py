from objects import Empty
import pygame
import math

class link:         #test class voor de link tussen de waypoints, zal mss gebruikt worden mss niet (voorlopig ongebruikt btw)
    def __init__(self, waypoint, distance, actionType):
        self.waypoint = waypoint
        self.distance = distance
        self.action = actionType

class Waypoint():
    def __init__(self, game, x, y, ptype = None):
        self.game = game
        self.pos = pygame.math.Vector2(x,y)
        self.texture = pygame.image.load('images/UI/waypoint.png')
        self.pointType = ptype

        self.links = []     #list met (distance, Waypoint)

    def update(self):
        if self.game.debugging:
            self.game.screen.blit(self.texture , (self.pos.x - self.texture.get_width()/2, self.pos.y - self.texture.get_height()))
            for link in self.links:
                pygame.draw.line(self.game.screen, (255,0,0), self.pos, link[1].pos, width=3)

    def link(self, waypoint, unidirectional = False):
        if waypoint not in self.linkedWaypoints:            #als de waypoint nog niet in de list wan waypoints is
            distance = self.pos.distance_to(waypoint.pos)
            self.links.append((distance, waypoint))
            if not unidirectional:
                waypoint.links.append((distance, self))
    

    @property
    def linkedWaypoints(self):
        return [i[1] for i in self.links]

def raycast(game, start:pygame.math.Vector2, end:pygame.math.Vector2):        #gebruik het ENKEL voor rechten evenwijdig met x of y as
    height = end.y - start.y
    width = end.x - start.x
    ray = Empty(game, start.x ,start.y, width, height)
    current = None
    for col in game.colliders:
        if ray.collideswith(col):
            if start.y>end.y and width == 0: 
                coord = pygame.math.Vector2(start.x,col.hitbox["bottom"])           #top en bottom omgekeerd omdat oorsprong in linkerbovenhoek staat bij pygame
                if not current or current[0]>coord.distance_to(ray.pos):
                    current = (coord.distance_to(ray.pos), coord)
            elif start.y<end.y and width == 0: 
                coord = pygame.math.Vector2(start.x,col.hitbox["top"])
                if not current or current[0]>coord.distance_to(ray.pos):
                    current = (coord.distance_to(ray.pos), coord)
            elif start.x>end.x and height == 0: 
                coord = pygame.math.Vector2(col.hitbox["right"],start.y)
                if not current or current[0]>coord.distance_to(ray.pos):
                    current = (coord.distance_to(ray.pos), coord)
            elif start.x<end.x and height == 0: 
                coord = pygame.math.Vector2(col.hitbox["left"],start.y)
                if not current or current[0]>coord.distance_to(ray.pos):
                    current = (coord.distance_to(ray.pos), coord)
    if current:
        """
        print("--------------------------")
        print("current: ", current)
        print("current[1]: ",current[1])
        print("___________________________")"""
        return current[1]

    return None

def thing(game, entity):        #we gebruiken entity om de min hoogte bovenop de waypoints te hebben
    temp_waypoints = []
    jumpheight = entity.jumpheight

    print(f"Jumpheight is: {jumpheight}")

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
            temp_waypoints.append(Waypoint(game, left_top.center_bottom.x, left_top.center_bottom.y, ptype="dropdown_L"))
            #print(f'Linker Waypoint aangemaakt voor object:{obj} op positie: {left_top.center_bottom.x} , {left_top.center_bottom.y}')
        if varR:
            temp_waypoints.append(Waypoint(game, right_top.center_bottom.x, right_top.center_bottom.y, ptype="dropdown_R"))
            #print(f'Rechter Waypoint aangemaakt voor object:{obj}, met pos van objec: {obj.pos} en pos van waypoint: {right_top.center_bottom.x} , {right_top.center_bottom.y}')
    
    waypoints = []
    for waypoint in temp_waypoints:
        if waypoint.pointType == "dropdown_L":
            intersect = raycast(game, pygame.math.Vector2(waypoint.pos.x - entity.width, waypoint.pos.y), pygame.math.Vector2(waypoint.pos.x - entity.width, waypoint.pos.y + 10000))     #we doen +- entity.width zodat de gemaakte onderste waypoint niet direct onder de bestaande zit zodat de bot niet doelloos blijft springen en zijn hoofd botsen op de bovenliggende platform 
        elif waypoint.pointType == "dropdown_R":
            intersect = raycast(game, pygame.math.Vector2(waypoint.pos.x + entity.width, waypoint.pos.y), pygame.math.Vector2(waypoint.pos.x + entity.width, waypoint.pos.y + 10000))
        
        if intersect != None:
            newpoint = Waypoint(game,intersect.x, intersect.y)
            if intersect.y-waypoint.pos.y < jumpheight:         #we gaan deze punten al samen linken voor de pathsearching, maar: als de bovenste waypoint te hoog ligt, dan wordt enkel het pad naar beneden gelinkt en niet andersom  
                newpoint.link(waypoint)
            else:
                pass 
                #waypoint.link(newpoint, unidirectional = True)
            waypoints.append(newpoint)
        waypoints.append(waypoint)


    #checken of er geen punten op dezelfde plaats zijn
    coords = []
    for point in waypoints:
            if point.pos in coords:
                print(f"Removed duplicate waypoint at {point.pos}")
                waypoints.remove(point)
            else:
                coords.append(point.pos)
    return waypoints

def connect(game, waypoints, entity):
    print("jumpwidth: ", entity.jumpwidth)
    for point in waypoints:
        current = (-1,None) #lege placeholder zodat we none voor de waypoint krijgen zou der geen ander gevonden worden

        for newPoint in waypoints:    
            if point.pos.y == newPoint.pos.y and point.pos.x<newPoint.pos.x:        #als er een punt op dezelfde hoogte en rechts van de oorspronkelijke punt gevonden wodt
                if point.pos.distance_to(newPoint.pos) < current [0] or current[0]==-1: #we zoeken de rechtse punt die het dichtsbij is
                    if newPoint.pointType != "dropdown_L" and not raycast(game, pygame.math.Vector2(point.pos.x, point.pos.y-entity.height/2), pygame.math.Vector2(newPoint.pos.x, newPoint.pos.y-entity.height/2)):       #als de rechtse punt een dropdown_L is betekent het dat er een gap is tussen de twee punten (de bot kan dus niet gwn rechtdoor lopen), en als raycast iets terugzendt is er een muur en moet het dus ook springen

                        current = (point.pos.distance_to(newPoint.pos), newPoint)

            if point.pos.y < newPoint.pos.y and point.pos.x>point.pos.y:
                pass
            
            if point.pointType == "dropdown_R" and (newPoint.pos.y <= point.pos.y and point.pos.y - entity.jumpheight <= newPoint.pos.y) and (newPoint.pos.x >= point.pos.x and point.pos.x + (entity.jumpwidth + 10) >= newPoint.pos.x):     #de +10 is een soort van marge aangezien de entities niet direct hun maximumsnelheid bereiken
                current = (point.pos.distance_to(newPoint.pos), newPoint)

            if point.pointType == "dropdown_L" and (newPoint.pos.y <= point.pos.y and point.pos.y - entity.jumpheight <= newPoint.pos.y) and (newPoint.pos.x <= point.pos.x and point.pos.x - (entity.jumpwidth + 10) <= newPoint.pos.x):     #de +10 is een soort van marge aangezien de entities niet direct hun maximumsnelheid bereiken
                current = (point.pos.distance_to(newPoint.pos), newPoint)

        if current[1]:      #als current[1] None is zijn er dus geen punten die 'rechtser' zijn, en er is geen link te maken met de ether
            point.link(current[1])

