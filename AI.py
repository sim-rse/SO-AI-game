from objects import Empty, Wall
import pygame
import math
import queue, random
from rich import print
from pygame.math import Vector2
pygame.init()
font = pygame.font.SysFont("monospace", 13)

class link:         #test class voor de link tussen de waypoints, zal mss gebruikt worden mss niet (voorlopig ongebruikt btw)
    def __init__(self, waypoint, distance, actionType=None):
        self.waypoint = waypoint
        self.distance = distance
        self.action = actionType
    def __str__(self):
        return f"link object naar waypoint {self.waypoint}"

class Waypoint():
    def __init__(self, game, x, y, ptype = None):
        self.game = game
        self.pos = pygame.math.Vector2(x,y)
        self.texture = pygame.image.load('images/UI/waypoint.png')
        self.pointType = ptype

        self.links = []     #list met (distance, Waypoint)

    def update(self):
        if self.game.debugging:
            label = font.render(str(self.pos), 0 ,(0,0,255))
            self.game.screen.blit(label, (self.pos.x, self.pos.y-20))
            self.game.screen.blit(self.texture , (self.pos.x - self.texture.get_width()/2, self.pos.y - self.texture.get_height()))
            for link in self.links:
                pygame.draw.line(self.game.screen, (255,0,0), self.pos, link.waypoint.pos, width=3)

    def link(self, waypoint, unidirectional = False):
        if waypoint == self:
            print(f"Toevoegen van {self} aan {self}")
        if waypoint not in self.linkedWaypoints:            #als de waypoint nog niet in de list wan waypoints is
            distance = self.pos.distance_to(waypoint.pos)
            self.links.append(link(waypoint,distance))
            if not unidirectional:
                waypoint.links.append(link(self, distance))

    def __str__(self):
        return f"[red]Waypoint object op positie {self.pos}[/red]"#en poittype {self.pointType}
    

    @property
    def linkedWaypoints(self):
        return [i.waypoint for i in self.links]

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

class AI:
    def __init__(self,game,entity):
        self.entity = entity
        self.game = game
        self.waypoints = self.getWaypoints()
        self.connectWaypoints()


    def getWaypoints(self):        #we gebruiken entity om de min hoogte bovenop de waypoints te hebben
        game = self.game
        entity = self.entity
        temp_waypoints = []
        jumpheight = entity.jumpheight

        #maakt waypoints aan bij alle tophoeken van de colliders
        for obj in game.colliders:
            if not isinstance(obj, Wall):
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
                    waypoint.link(newpoint, unidirectional = True)
                waypoints.append(newpoint)
            waypoints.append(waypoint)


        #checken of er geen punten op dezelfde plaats zijn
        coords = []
        new_points = []
        for point in waypoints:
                if point.pos not in coords:
                    coords.append(point.pos)
                    new_points.append(point)

        return new_points

    def connectWaypoints(self):
        entity = self.entity
        game = self.game
        waypoints = self.waypoints
        for point in waypoints:
            current = (-1,None) #lege placeholder zodat we none voor de waypoint krijgen zou der geen ander gevonden worden

            for newPoint in waypoints:   
                if newPoint != point: 
                    if point.pos.y == newPoint.pos.y and point.pos.x<newPoint.pos.x:        #als er een punt op dezelfde hoogte en rechts van de oorspronkelijke punt gevonden wodt
                        if point.pos.distance_to(newPoint.pos) < current [0] or current[0]==-1: #we zoeken de rechtse punt die het dichtsbij is
                            if point.pointType != "dropdown_R" and newPoint.pointType != "dropdown_L" and not raycast(game, pygame.math.Vector2(point.pos.x, point.pos.y-10), pygame.math.Vector2(newPoint.pos.x, newPoint.pos.y-10)):       #als de rechtse punt een dropdown_L is betekent het dat er een gap is tussen de twee punten (de bot kan dus niet gwn rechtdoor lopen), en als raycast iets terugzendt is er een muur en moet het dus ook springen
                                print(newPoint.pointType)
                                current = (point.pos.distance_to(newPoint.pos), newPoint)
                                #print(f"Newvector at same height: {}")

                    #if point.pos.y < newPoint.pos.y and point.pos.x>point.pos.y:
                    #    pass
            
            if current[1]:      #als current[1] None is zijn er dus geen punten die 'rechtser' zijn, en er is geen link te maken met de ether
                point.link(current[1])
                pass

            current = (-1, None)
            for newPoint in waypoints:   
                if newPoint != point: 

                    if point.pointType == "dropdown_R" and (newPoint.pos.y <= point.pos.y and point.pos.y - entity.jumpheight <= newPoint.pos.y) and (newPoint.pos.x >= point.pos.x and point.pos.x + (entity.jumpwidth + 10) >= newPoint.pos.x):     #de +10 is een soort van marge aangezien de entities niet direct hun maximumsnelheid bereiken
                        current = (point.pos.distance_to(newPoint.pos), newPoint)

                    if point.pointType == "dropdown_L" and (newPoint.pos.y <= point.pos.y and point.pos.y - entity.jumpheight <= newPoint.pos.y) and (newPoint.pos.x <= point.pos.x and point.pos.x - (entity.jumpwidth + 10) <= newPoint.pos.x):     #de +10 is een soort van marge aangezien de entities niet direct hun maximumsnelheid bereiken
                        current = (point.pos.distance_to(newPoint.pos), newPoint)

            if current[1]:
                #point.link(current[1])
                pass

        print("sum is: ", sum([len(point.links) for point in waypoints]))
    def find_path(self, start:pygame.math.Vector2, end: pygame.math.Vector2, waypoints = None):
        if not waypoints:
            waypoints = self.waypoints
        
        start_point = None
        end_point = None

        for point in waypoints:
            if start_point is None or manhattan(point.pos, start) < manhattan(start_point.pos, start):
                #if not (raycast(self.game, Vector2(point.pos.x, start.y), point.pos) or raycast(self.game, start, Vector2(point.pos.x, start.y))): #als er geen muur ligt tussen de dichtsbijzijnde waypoint, anders zoekt hij een andere
                    start_point = point

            if end_point is None or manhattan(point.pos, end) < manhattan(end_point.pos, end):
                #if not (raycast(self.game, Vector2(point.pos.x, start.y), point.pos) or raycast(self.game, start, Vector2(point.pos.x, start.y))):
                    end_point = point

            #print(f"startpoint: {start_point.pos}, start: {start}\n end point: {end_point.pos}, end: {end}")
        
        nodes, path= A_star(start_point, end_point)
        if nodes:
            return get_path(nodes)
        else:
            return []
    
    def show_path(self):
        entitypos = self.entity.pos
        #print("entitypos: ",entitypos)
        targetpos = self.entity.target.pos
        #print("targetpos: ", targetpos)
        if len(self.waypoints)>2:
            try:
                pygame.draw.lines(self.game.screen, (0,255,0), False, [point.pos for point in self.find_path(entitypos, targetpos, self.waypoints)],width=5)
            except:
                print("Geen path gevonden!")

def A_star(start_point:Waypoint, end_point:Waypoint):
    start_state = {'point':start_point,'parent':None, 'afgelegd': 0}
    q = queue.PriorityQueue()
    random_value = random.randint(1, 1000000)
    q.put((0,random_value,start_state))
    
    traveled = []
    
    #print(f"----------------------------------------------\nWe moeten van punt: {start_point} met coordinaten {start_point.pos}\nNaar punt {end_point} met coordinaten {end_point.pos}")
    while q.empty() == False:
        #print(f"De queue heeft zoveel items: {q.qsize()}")
        priority,random_value,state = q.get()
        directions = state['point'].links
        #print(f"\n\n>> We onderzoeken waypoint: {state["point"]} met volgende links: {directions}")

        for numb, link in enumerate(directions):
            #print("link ", link)
            new_point = link.waypoint
            #print("newpoint ", new_point)
            if new_point not in traveled:
                    new_state = {'point':new_point,'parent':state,'afgelegd':state['afgelegd']+link.distance}
                    #print(f">> [{numb}/{len(directions)}]: Toevoegen van waypoint {new_point.pos}, Maken van een nieuwe state: {new_state}")
                    #print("newpoint, endpoint ", new_point, end_point)
                    if new_point == end_point :
                        #print("Oplossing gevonden!!!")
                        return new_state, traveled
                    else:
                        priority = new_point.pos.distance_to(end_point.pos) + new_state['afgelegd']
                        random_value = random.randint(1,100000)
                        q.put((priority,random_value,new_state))
                        traveled.append(new_point)
            #else:
                #print(f">> [{numb}/{len(directions)}] Het nieuwe punt: {new_point}, link van waypoint {state['point']} is al in traveled: {traveled}")
        #print(f">> done with waypoint: {state["point"]}")
    #print(f"Geen point gevonden!")
    return None, traveled

def get_path(my_node):
    my_list = []
    #print(my_node)
    while True:
        my_list.append(my_node['point'])
        if my_node['parent'] == None:
            return my_list
        my_node = my_node['parent']

def manhattan(start: pygame.math.Vector2, end: pygame.math.Vector2):
    x = abs(start.x - end.x)
    y = abs(start.y - end.y)
    return x + y