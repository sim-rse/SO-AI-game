#coole sprites ma geen stap animatie: https://diegosanches.com/science-kombat (scroll naar beneden)
import pygameimport Object, MovingObject
from loops import *riorityQueue
from objects import *ypoint
from entities import *
from start_menu import selection_menu
from powerrup import PowerUp x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20, center=None):
from game_end import game_over x, y, width, height, image, hasCollisionEnabled=True, affected_by_gravity=True, animationfile=animationfile, scale=scale, center=center)

pygame.init()health = health
        self.strength = 2
class Game():
    def __init__(self,screen):
        self.screen = screen = PriorityQueue()
        self.dt = 1
        self.window_scale = 1
        self.fps = 60le = False
        self.jump_force = 16
        self.running = True

        self.scene = "default"
        self.scene_running = False
        self.gravity = 1
    def jump(self):
        self.debugging = True
            self.vel.y = -self.jump_force  # https://www.youtube.com/watch?v=bn3ZUCZ0vMo
        self.objects = []
        self.UI = []lf, damage):
        self.backgrounds = [le:
        pygame.image.load("images/projectimage1.jpg").convert(),
        pygame.image.load("images/projectimage2.jpg").convert(),
        pygame.image.load("images/projectimage3.jpg").convert()
        ]unch(self, otherEntity=None):
        self.background_index = 0")
        if otherEntity:
    @propertytherEntity.getDamage(self.strength)
    def background(self):
        return self.backgrounds[self.background_index]
        self.game.add(
    @background.setter(
    def background(self, value):
        if type(value)==int:x,
            self.background_index = valueht,
                target=target,
    def add(self,obj):self,
        if type(obj) == list:e,
            for i in obj:ages/fireball.png"  # Pass the fireball image here
                self.objects.append(i)
        else:
            self.objects.append(obj)
    def update(self):
    def remove(self,obj): 
        if type(obj) == list:
            for i in obj:
                if i in self.objects:       #er was ander soms een error bij projectiles waarbij het zich twee keer probeerde te removen (dit was een tijdelijke fix, maar als u dit ziet ben ik het vergeten deftig op te lossen)
                    self.objects.remove(i)
        else:eight(self):
            
            if obj in self.objects:
                self.objects.remove(obj)
    def jumpwidth(self):
    def empty(self, keepUI = False): self.jump_force / self.game.gravity)  
        self.objects = []
        if not keepUI:
            self.UI = []:
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20, target=None, owner=None, exploding=False):
    def add_UI(self,obj):game, x, y, width, height, image, animationfile, scale, health)
        if type(obj) == list:
            for i in obj:ge = 5
                self.UI.append(i)reased speed for better movement
        else:exploding = exploding
            self.UI.append(obj)
        self.owner = owner
    def remove_UI(self,obj):
        if type(obj) == list:get
            for i in obj:
                self.UI.remove(i)math.Vector2(0, 0)
        else:
            self.UI.remove(obj)o the target
        if (self.target - self.pos).length_squared() != 0:
    def pause(self):       #deze scene werkt lichtjes anders: het moet ergens binnen de loop van de andere scenes geroepen worden zodat we dan terug naar de andere 
                                #kheb het ook hiet gezet ipv in loops.py door circulaire imports
        screen: pygame.display = self.screentor2(1, 0)  # Standaard richting naar rechts
        current_scene = self.scene
        keys = []cted_by_gravity = 0
        color = (30,30,30)lse
        width = 200ionsEnabled = False
        UI = [SceneButton(self,screen.get_width()/2 - width/2,screen.get_height()*0.4,"Back to game","default",width=width,height=50), SceneButton(self,screen.get_width()/2 - width/2,screen.get_height()*0.5,"Quit","start_menu",width=width,height=50)]   #de naam van de scene kan technisch gezien random zijn, want we keren toch terug naar de vorige scene
        # Set initial velocity based on direction and speed
        pygame.draw.rect(screen, (50,50,50,200), pygame.Rect(screen.get_width()*0.2, screen.get_height()*0.2, screen.get_width()*0.6, screen.get_height()*0.6))
        pygame.draw.rect(screen, (255,0,0,200), pygame.Rect(screen.get_width()*0.22, screen.get_height()*0.22, screen.get_width()*0.56, screen.get_height()*0.56), width=10)
        
        font = pygame.font.SysFont("monospace", 30)th target {target}")
        title = font.render("Game Paused", 1, (255,255,255), (50,50,50))
        screen.blit(title, (screen.get_width()/2 - title.get_width()/2, screen.get_height()*0.21))
        # Update position based on velocity
        while self.running and self.scene_running:
            clock.tick(self.fps)
            #screen.fill(color)lf.pos.x, self.pos.y)  # Update the rect for collision detection
            
        # Check for collisions
            for event in pygame.event.get():
                match event.type: 
                    case pygame.QUIT:
                        self.running = False
                    case pygame.KEYDOWN:d isinstance(col, Entity):  # If it explodes, damage comes from the explosion
                        match event.key:trength)
                            case pygame.K_ESCAPE:
                                self.scene_running = False
            move the projectile if it goes off-screen
            for ui in UI: or self.pos.x > self.game.screen_width or self.pos.y < 0 or self.pos.y > self.game.screen_height:
                ui.update()
        
            pygame.display.flip()
        if self.scene == current_scene:
            self.scene_running = True #houdt deze true zodat de gepauseerde loop waarin we bezig zijn gwn verder gaat en niet reset    
    @property
    def entities(self)::
        return [ent for ent in self.objects if isinstance(ent, Entity)]=100, strength=30):
        super().__init__(game, x, y, scale=scale, animationfile="animations/explosion.json", center=center)
    @propertyplayanimation("explosion")
    def players(self):True
        return [obj for obj in self.objects if isinstance(obj, Player)]
        self.strength = strength
    @propertycollisionsEnabled = False
    def colliders(self):_gravity = False
        return [obj for obj in self.objects if obj.collider]
        for ent in self.game.entities:
    @propertyf ent.collideswith(self, range_=self.explosionrange):  # If explosionrange is 0, only entities hit directly take damage
    def screen_width(self):ge(self.strength)
        return self.screen.get_width()
    @property   knockback_direction = pygame.math.Vector2(ent.center.x - self.center.x, ent.center.y - self.center.y)
    def screen_height(self):back_direction.xy == [0, 0]:
        return self.screen.get_height().normalize_ip()  # Normalize the vector if it's not 0
    
    def __str__(self):l = knockback_direction * self.strength * 2  # Apply knockback
        return f"Main game object containing {self.objects}"
    def update(self):
    def movement(self):
        path = self.path        if hasattr(self, "animations") and self.animations.current.name == "default":
        pos = self.center_bottom
        waypoint = self.current_waypoint  # Fixed: Use self.current_waypoint instead of self.current_waypoint_bottom

        if len(path) != 0:
            if pos.distance_to(waypoint.pos) <= 5:
                self.current_waypoint = path.pop()
        self.game.remove(self)
        if waypoint.pos.x + 1 < pos.x:
            self.smoothSpeedChange(-self.walkSpeed)
            if waypoint.pos.y < pos.y and waypoint.pointType == "dropdown_R" and self.onGround:):
                self.jump()(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1):
        elif waypoint.pos.x - 1 > pos.x:, x, y, width, height, image, animationfile, scale)
            self.smoothSpeedChange(self.walkSpeed)d = 10
            if waypoint.pos.y < pos.y and waypoint.pointType == "dropdown_L" and self.onGround:hold = False
                self.jump()lse
        else:
            self.smoothSpeedChange(0)= 500  # Cooldown in milliseconden
ot_time = 0
screenInfo = pygame.display.Info()
arget):
screen_x = (screenInfo.current_w)*0.9
screen_y = (screenInfo.current_h)*0.9 target is, schiet rechtdoor
screen_size = [1536,864] #(width x height).math.Vector2(self.pos.x + self.width + 1, self.pos.y)
screen = pygame.display.set_mode(screen_size) #voeg pygame.FULLSCREEN als argument toe voor fullscreen

pygame.display.set_caption("Untitled Fight Game - AI in the works!")            Projectile(
                self.game,
game = Game(screen) #We maken ee game class aan die allerlei variabels over de game in het algemeen (zoals screen, lijsten met entities enz, tijd tussen de frames) groepeert zodat we telkens maar een variabel moeten doorgeven en niet duizenden. Zo kan een object makkelijker variabels van andere objecten veranderen (zolang deze zich ergens in de Game object bevinden)    self.center.x,




















pygame.quit()            quit(game)        case "quit":            game_over(game)        case 'game_over':            game.pause()        case "pause":            selection_menu(game)        case "menu":            start_menu(game)        case "start_menu":            gameLoop(game)        case "default":    match game.scene:    game.scene_running = True    game.empty()while game.running:#zahide                 self.center.y - self.height,
                target=target,
                owner=self,
                exploding=True,
                image="images/fireball.png"  # Zorg ervoor dat dit pad correct is
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
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time > self.shoot_cooldown:
                self.last_shot_time = current_time
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

    def die(self):
        self.game.scene = "game_over"
        self.game.scene_running = False

    def movement(self):
        path = self.path
        pos = self.center_bottom
        waypoint = self.current_waypoint_bottom

        if len(path) != 0:
            if pos.distance_to(waypoint.pos) <= 5:
                self.current_waypoint = path.pop()

        if waypoint.pos.x + 1 < pos.x:
            self.smoothSpeedChange(-self.walkSpeed)
            if waypoint.pos.y < pos.y and waypoint.pointType == "dropdown_R" and self.onGround:
                self.jump()
        elif waypoint.pos.x - 1 > pos.x:
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

