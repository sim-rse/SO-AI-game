import pygame, time, random  # Importeer pygame voor gamefunctionaliteit, time voor tijdbeheer, en random voor willekeurige keuzes.
from objects import MovingObject  # Importeer MovingObject als basis voor bewegende objecten.
from queue import PriorityQueue  # Importeer PriorityQueue voor het beheren van doelen.
from AI import AI, Waypoint  # Importeer AI en Waypoint voor kunstmatige intelligentie en padvinden.
from powerup import PowerUp  # Importeer PowerUp voor power-ups in het spel.

# Definieer de Entity-klasse, die een bewegend object in het spel vertegenwoordigt.
class Entity(MovingObject):
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20, center=None):
        super().__init__(game, x, y, width, height, image, hasCollisionEnabled=True, affected_by_gravity=True, animationfile=animationfile, scale=scale, center=center)  # Roep de constructor van MovingObject aan.

        self.health = health  # Gezondheid van de entiteit.
        self.strength = 2  # Hoeveel schade de entiteit kan toebrengen.
        self.target = None  # Het doelwit van de entiteit.
        self.list_of_targets = PriorityQueue()  # Een prioriteitenlijst voor doelen.
        self.collider = False  # Geeft aan of de entiteit botsingen kan detecteren.
        self.invincible = False  # Geeft aan of de entiteit onkwetsbaar is.
        self.jump_force = 18  # De kracht waarmee de entiteit kan springen.
        self.walkSpeed = 12  # De loopsnelheid van de entiteit.
        self.punch_cooldown = 0.5  # De tijd tussen twee stoten.
        self.shoot_cooldown = 1  # De tijd tussen twee schoten.
        self.last_punch_time = 0  # Tijdstip van de laatste stoot.
        self.last_shoot_time = 0  # Tijdstip van het laatste schot.
        self.last_action_time = 0  # Tijdstip van de laatste actie.
        self.current_action = None  # De huidige actie van de entiteit.
        self.current_action_length = 0  # De duur van de huidige actie.
        self.protecting = False  # Geeft aan of de entiteit zich beschermt.
        self.birth_time = time.time()  # Tijdstip waarop de entiteit is gemaakt.

    def die(self):  # Methode die wordt aangeroepen wanneer de entiteit sterft.
        self.playanimation("die")  # Speel de sterfanimatie af.

    def jump(self):  # Laat de entiteit springen.
        if self.onGround:  # Controleer of de entiteit op de grond staat.
            self.vel.y = -self.jump_force  # Stel de verticale snelheid in om te springen.

    def getDamage(self, damage):  # Verminder de gezondheid van de entiteit.
        if not (self.invincible or self.protecting):  # Controleer of de entiteit niet onkwetsbaar is of zich beschermt.
            self.health -= damage  # Verminder de gezondheid.
        self.playanimation("get_damaged")  # Speel de animatie voor schade af.

    def punch(self):  # Laat de entiteit een stoot uitvoeren.
        self.playanimation("punch")  # Speel de stootanimatie af.
        for otherEntity in self.game.entities:  # Controleer botsingen met andere entiteiten.
            if otherEntity is not self and self.collideswith(otherEntity, range_=10):  # Controleer of de entiteit binnen bereik is.
                otherEntity.getDamage(self.strength)  # Breng schade toe aan de andere entiteit.

    def shoot(self, target):  # Laat de entiteit een projectiel afvuren.
        self.game.add(Projectile(self.game, self.pos.x, self.pos.y, target=target, owner=self, exploding=True, scale=0.5))  # Voeg een projectiel toe aan het spel.

    def update(self):  # Methode die elke frame wordt aangeroepen.
        super().update()  # Roep de update-methode van de ouderklasse aan.
        if self.health <= 0:  # Controleer of de gezondheid 0 of lager is.
            self.die()  # Laat de entiteit sterven.
        if self.vel.x < 0:  # Controleer of de entiteit naar links beweegt.
            self.flipSprite = True  # Spiegel de sprite zodat deze naar links kijkt.
        elif self.vel.x > 0:  # Controleer of de entiteit naar rechts beweegt.
            self.flipSprite = False  # Zorg ervoor dat de sprite niet gespiegeld is.

    @property
    def jumpheight(self):  # Bereken de maximale spronghoogte.
        return self.jump_force**2 / (2 * self.game.gravity)  # Gebruik de wet van behoud van energie.

    @property
    def jumpwidth(self):  # Bereken de maximale sprongafstand.
        return self.walkSpeed * (2 * self.jump_force / self.game.gravity)  # Gebruik de sprongkracht en zwaartekracht.

    @property
    def ready_to_punch(self):  # Controleer of de entiteit klaar is om te stoten.
        return time.time() - self.last_punch_time > self.punch_cooldown  # Controleer of de cooldown is verstreken.

    @property
    def ready_to_shoot(self):  # Controleer of de entiteit klaar is om te schieten.
        return time.time() - self.last_shoot_time > self.shoot_cooldown  # Controleer of de cooldown is verstreken.

    @property
    def action_cooldown(self):  # Bereken de resterende cooldown voor acties.
        diff = time.time() - self.last_action_time  # Bereken het tijdsverschil sinds de laatste actie.
        if self.current_action_length - diff > 0:  # Controleer of de actie nog bezig is.
            return self.current_action_length - diff  # Geef de resterende tijd terug.
        else:
            return 0  # Geen cooldown meer.

    @property
    def punching(self):  # Controleer of de entiteit aan het stoten is.
        if time.time() - self.last_punch_time < 0.3:  # Controleer of de stoot recent is uitgevoerd.
            return True  # De entiteit is aan het stoten.
        return False  # De entiteit is niet aan het stoten.

    @property
    def shooting(self):  # Controleer of de entiteit aan het schieten is.
        if time.time() - self.last_shoot_time < 0.4:  # Controleer of het schot recent is uitgevoerd.
            return True  # De entiteit is aan het schieten.
        return False  # De entiteit is niet aan het schieten.

class Projectile(Entity):  # Klasse voor projectielen zoals kogels of vuurballen.
    def __init__(self, game, x, y, width=0, height=0, image="images/bomb.png", animationfile=None, scale=1, health=20, target=None, owner=None, exploding=False):
        super().__init__(game, x, y, width, height, image, animationfile, scale, health)  # Roep de constructor van de ouderklasse aan.

        self.explosionrange = 5  # Het bereik van de explosie.
        self.flyspeed = 5  # De snelheid waarmee het projectiel vliegt.
        self.exploding = exploding  # Geeft aan of het projectiel explodeert bij impact.

        self.owner = owner  # De eigenaar van het projectiel (bijvoorbeeld een speler of vijand).
        if target:  # Als er een doelwit is opgegeven:
            self.target = target  # Stel het doelwit in.
        else:  # Als er geen doelwit is opgegeven:
            self.target = pygame.math.Vector2(0, 0)  # Stel een standaard doelwit in (0, 0).
        self.direction = (self.target - self.pos).normalize()  # Bereken de richting waarin het projectiel moet bewegen.

        self.affected_by_gravity = 0  # Het projectiel wordt niet beïnvloed door zwaartekracht.
        self.collider = False  # Botsingen zijn uitgeschakeld.
        self.collisionsEnabled = False  # Botsingen zijn volledig uitgeschakeld.

        self.vel.x = self.direction.x * self.flyspeed  # Stel de horizontale snelheid in op basis van de richting en snelheid.
        self.vel.y = self.direction.y * self.flyspeed  # Stel de verticale snelheid in op basis van de richting en snelheid.

    def die(self):  # Methode die wordt aangeroepen wanneer het projectiel "sterft" (bijvoorbeeld bij impact).
        super().die()  # Roep de die-methode van de ouderklasse aan.
        self.game.remove(self)  # Verwijder het projectiel uit het spel.
        if self.exploding:  # Als het projectiel explodeert:
            self.game.add(Explosion(self.game, self.pos.x, self.pos.y, explosionrange=self.explosionrange, center=self.center))  # Voeg een explosie toe op de locatie van het projectiel.

    def update(self):  # Methode die elke frame wordt aangeroepen.
        self.updatePos()  # Werk de positie van het projectiel bij.
        for col in self.game.colliders + self.game.fighters:  # Controleer botsingen met colliders en vechters.
            if col == self.owner:  # Als het botsende object de eigenaar is:
                pass  # Doe niets.
            else:  # Als het botsende object niet de eigenaar is:
                if self.collideswith(col):  # Controleer of het projectiel botst met het object.
                    if not self.exploding and isinstance(col, Entity):  # Als het projectiel niet explodeert en het object een entiteit is:
                        col.getDamage(self.strength)  # Breng schade toe aan het object.
                    self.die()  # Laat het projectiel sterven.
        self.blit()  # Teken het projectiel op het scherm.

class Explosion(Entity):  # Klasse voor explosies die optreden bij impact van projectielen.
    def __init__(self, game, x, y, scale=1, center=None, explosionrange=100, strength=30):
        super().__init__(game, x, y, scale=scale, animationfile="animations/explosion.json", center=center)  # Roep de constructor van de ouderklasse aan.
        self.playanimation("explosion")  # Speel de explosie-animatie af.
        self.static = True  # Maak de explosie statisch (niet bewegend).
        self.explosionrange = explosionrange  # Stel het bereik van de explosie in.
        self.strength = strength  # Stel de kracht van de explosie in.
        self.collisionsEnabled = False  # Botsingen zijn uitgeschakeld.
        self.affected_by_gravity = False  # De explosie wordt niet beïnvloed door zwaartekracht.

        for ent in self.game.entities:  # Itereer door alle entiteiten in het spel.
            if ent.collideswith(self, range_=self.explosionrange):  # Controleer of een entiteit binnen het bereik van de explosie valt.
                ent.getDamage(self.strength)  # Breng schade toe aan de entiteit.

                knockback_direction = pygame.math.Vector2(ent.center.x - self.center.x, ent.center.y - self.center.y)  # Bereken de richting van de knockback.
                if not knockback_direction.xy == [0, 0]:  # Controleer of de knockback-richting niet nul is.
                    knockback_direction.normalize_ip()  # Normaliseer de knockback-richting.

                ent.vel = knockback_direction * self.strength * 2  # Pas knockback toe op de entiteit.

    def update(self):  # Methode die elke frame wordt aangeroepen.
        super().update()  # Roep de update-methode van de ouderklasse aan.
        if self.animations.current.name == "default":  # Controleer of de explosie-animatie is afgelopen.
            self.die()  # Verwijder de explosie.

    def getDamage(self, damage):  # Explosies kunnen geen schade oplopen.
        pass  # Doe niets.

    def die(self):  # Methode die wordt aangeroepen wanneer de explosie "sterft".
        self.game.remove(self)  # Verwijder de explosie uit het spel.

class Player(Entity):  # De Player-klasse erft van de Entity-klasse en vertegenwoordigt de speler.
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=100):
        super().__init__(game, x, y, width, height, image, animationfile, scale)  # Roep de constructor van de Entity-klasse aan.
        self.walkSpeed = 10  # De snelheid waarmee de speler kan lopen.
        self.shoot_key_hold = False  # Houdt bij of de schietknop wordt ingedrukt.
        self.sneaking = False  # Boolean die aangeeft of de speler aan het sluipen is.
        self.health = health  # De hoeveelheid gezondheidspunten van de speler.

        self.last_punch_time = 0  # Tijdstip van de laatste stoot.

    def getKeyPress(self):  # Methode om toetsenbordinvoer te verwerken.
        keys = pygame.key.get_pressed()  # Haalt de huidige status van alle toetsen op.
        accel = [0, 0]  # Versnelling van de speler (x, y).
        if not self.protecting:  # Als de speler zich beschermt, kan hij niets anders doen.
            if keys[pygame.K_RIGHT]:  # Als de rechterpijltoets wordt ingedrukt:
                accel[0] += self.walkSpeed  # Verhoog de snelheid naar rechts.
            if keys[pygame.K_LEFT]:  # Als de linkerpijltoets wordt ingedrukt:
                accel[0] += -self.walkSpeed  # Verhoog de snelheid naar links.
            if keys[pygame.K_UP]:  # Als de omhoogpijltoets wordt ingedrukt:
                self.jump()  # Laat de speler springen (methode te vinden in de Entity-klasse).

            if keys[pygame.K_SPACE]:  # Als de spatiebalk wordt ingedrukt:
                if time.time() - self.last_punch_time > 0.5:  # Controleer of de punch-cooldown is verstreken.
                    self.punch()  # Laat de speler een stoot uitvoeren.
                    self.last_punch_time = time.time()  # Update de tijd van de laatste stoot.

        self.smoothSpeedChange(accel[0])  # Zorgt ervoor dat de snelheid soepel verandert.

        if keys[pygame.K_DOWN]:  # Als de omlaagpijltoets wordt ingedrukt:
            self.sneaking = True  # Zet de sluipmodus aan.
            self.protecting = True  # Zet beschermen aan.
        else:  # Als de omlaagpijltoets niet wordt ingedrukt:
            self.sneaking = False  # Zet de sluipmodus uit.
            self.protecting = False  # Zet beschermen uit.

        if keys[pygame.K_a]:  # Als de "A"-toets wordt ingedrukt:
            list_of_targets = PriorityQueue()  # Maak een prioriteitenlijst voor doelen.
            for i in [ent for ent in self.game.enemies if not ent == self]:  # Itereer door alle vijanden.
                list_of_targets.put((self.pos.distance_to(i.pos), i))  # Voeg vijanden toe aan de lijst, gesorteerd op afstand.
            self.target = list_of_targets.get()[1]  # Stel het dichtstbijzijnde doelwit in.
        else:  # Als de "A"-toets niet wordt ingedrukt:
            self.target = None  # Verwijder het doelwit.

        if keys[pygame.K_z]:  # Als de "Z"-toets wordt ingedrukt:
            if not self.shoot_key_hold and not self.protecting:  # Controleer of de schietknop niet al wordt vastgehouden en de speler niet beschermt.
                self.shoot_key_hold = True  # Zet de schietknop op vastgehouden.
                if self.target:  # Als er een doelwit is:
                    target_position = self.target.pos  # Gebruik de positie van het doelwit.
                elif self.flipSprite:  # Als de speler naar links kijkt:
                    target_position = pygame.math.Vector2(self.pos.x - 1, self.pos.y)  # Schiet naar links.
                else:  # Als de speler naar rechts kijkt:
                    target_position = pygame.math.Vector2(self.pos.x + self.width + 1, self.pos.y)  # Schiet naar rechts.

                self.shoot(target_position)  # Vuur een projectiel af naar de doelpositie.
        else:  # Als de "Z"-toets niet wordt ingedrukt:
            self.shoot_key_hold = False  # Zet de schietknop op niet vastgehouden.

    def animationHandler(self):  # Methode om de animaties van de speler te beheren.
        if self.shooting:  # Als de speler aan het schieten is:
            self.playanimation("shoot")  # Speel de schietanimatie af.
        elif self.punching:  # Als de speler aan het stoten is:
            self.playanimation("punch")  # Speel de stootanimatie af.
        elif self.protecting:  # Als de speler zich beschermt:
            self.playanimation("protect")  # Speel de beschermanimatie af.
        elif self.vel.y < 0:  # Als de speler omhoog beweegt (springt):
            self.playanimation("jump")  # Speel de springanimatie af.
        elif self.onGround and self.vel.x != 0:  # Als de speler op de grond loopt:
            self.playanimation("walk")  # Speel de loopanimatie af.
        elif self.vel.y > 0:  # Als de speler naar beneden beweegt (valt):
            self.playanimation("fall")  # Speel de valanimatie af.
        else:  # Als geen van bovenstaande acties plaatsvindt:
            self.playanimation("default")  # Speel de standaardanimatie af.

    def die(self):  # Methode die wordt aangeroepen wanneer de speler sterft.
        super().die()  # Roep de die-methode van de ouderklasse aan.
        self.game.scene = "game_over"  # Zet de spelscène op "game_over".
        self.game.scene_running = False  # Stop de huidige scène.
        self.game.winner = "Enemy"  # Stel de winnaar in op "Enemy".

    def update(self):  # Methode die elke frame wordt aangeroepen.
        self.getKeyPress()  # Verwerk de toetsenbordinvoer.
        super().update()  # Roep de update-methode van de ouderklasse aan.

class Enemy(Entity):  # De Enemy-klasse erft van de Entity-klasse en vertegenwoordigt vijanden in het spel.
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20):
        super().__init__(game, x, y, width, height, image, animationfile, scale, health)  # Roep de constructor van de Entity-klasse aan.

        self.target = game.players[0]  # Stel het eerste doelwit in (de eerste speler in de lijst).
        self.walkSpeed = 5  # De loopsnelheid van de vijand.
        self.ai = AI(game, self)  # Initialiseer de AI voor de vijand.
        self.getPath(self.target)  # Bereken het pad naar het doelwit.

        if len(self.path) > 0:  # Als er een pad is gevonden:
            self.current_waypoint = self.path.pop()  # Stel het huidige waypoint in op het laatste punt in het pad.
        else:  # Als er geen pad is gevonden:
            self.current_waypoint = Waypoint(game, x, y)  # Stel een standaard waypoint in op de huidige positie.

    def die(self):  # Methode die wordt aangeroepen wanneer de vijand sterft.
        self.game.scene = "game_over"  # Zet de spelscène op "game_over".
        self.game.scene_running = False  # Stop de huidige scène.
        self.game.winner = f"Player"  # Stel de winnaar in op "Player".

    def animationHandler(self):  # Methode om de animaties van de vijand te beheren.
        if self.shooting:  # Als de vijand aan het schieten is:
            self.playanimation("shoot")  # Speel de schietanimatie af.
        elif self.punching:  # Als de vijand aan het stoten is:
            self.playanimation("punch")  # Speel de stootanimatie af.
        elif self.protecting:  # Als de vijand zich beschermt:
            self.playanimation("protect")  # Speel de beschermingsanimatie af.
        elif self.vel.y < 0:  # Als de vijand omhoog beweegt (springt):
            self.playanimation("jump")  # Speel de springanimatie af.
        elif self.onGround and self.vel.x != 0:  # Als de vijand op de grond loopt:
            self.playanimation("walk")  # Speel de loopanimatie af.
        elif self.vel.y > 0:  # Als de vijand naar beneden beweegt (valt):
            self.playanimation("fall")  # Speel de valanimatie af.
        else:  # Als geen van bovenstaande acties plaatsvindt:
            self.playanimation("default")  # Speel de standaardanimatie af.

    def movement(self):  # Methode om de beweging van de vijand te beheren.
        path = self.path  # Haal het huidige pad op.
        pos = self.center_bottom  # Haal de positie van de onderkant van de vijand op.
        waypoint = self.current_waypoint  # Haal het huidige waypoint op.

        if len(path) != 0:  # Als er nog waypoints in het pad zijn:
            if pos.distance_to(waypoint.pos) <= 5 and self.onGround:  # Als de vijand dichtbij het huidige waypoint is en op de grond staat:
                self.current_waypoint = path.pop()  # Stel het volgende waypoint in.
            for num, i in enumerate(path):  # Controleer of er een korter pad is.
                if pos.distance_to(waypoint.pos) > pos.distance_to(i.pos):  # Als een ander waypoint dichterbij is:
                    self.path = path[:num]  # Verkort het pad tot dat waypoint.
                    self.current_waypoint = path.pop()  # Stel het nieuwe waypoint in.
        else:  # Als er geen pad meer is:
            self.getPath(self.target)  # Bereken een nieuw pad naar het doelwit.

        waypoint = self.current_waypoint  # Werk het huidige waypoint bij.

        if waypoint.pos.x + 10 < pos.x:  # Als de vijand links van het waypoint is:
            self.smoothSpeedChange(-self.walkSpeed)  # Beweeg naar links.
            if waypoint.pos.y < pos.y and self.jumpwidth > abs(self.pos.x - waypoint.pos.x) and self.onGround:  # Controleer of de vijand moet springen.
                self.jump()  # Laat de vijand springen.
        elif waypoint.pos.x - 10 > pos.x:  # Als de vijand rechts van het waypoint is:
            self.smoothSpeedChange(self.walkSpeed)  # Beweeg naar rechts.
            if waypoint.pos.y < pos.y and self.jumpwidth > abs(self.pos.x - waypoint.pos.x) and self.onGround:  # Controleer of de vijand moet springen.
                self.jump()  # Laat de vijand springen.
        else:  # Als de vijand dichtbij het waypoint is:
            self.smoothSpeedChange(0)  # Stop de beweging.

    def getPath(self, target):  # Bereken het pad naar een doelwit.
        path = self.ai.find_path(self.center_bottom, target.center_bottom)  # Gebruik de AI om een pad te vinden.
        if path != []:  # Als er een pad is gevonden:
            self.path: list = path  # Sla het pad op.
            self.current_waypoint = self.path.pop()  # Stel het eerste waypoint in.
        else:  # Als er geen pad is gevonden:
            self.path = []  # Stel het pad in op een lege lijst.
            print("Path not found!!")  # Print een foutmelding.

    def show_path(self):  # Toon het pad van de vijand op het scherm (voor debugging).
        try:
            pygame.draw.lines(self.game.screen, (0, 255, 0), False, [point.pos for point in self.path], width=5)  # Teken het pad.
        except:
            pass  # Negeer fouten (bijvoorbeeld als het pad leeg is).

    def actionHandler(self):  # Methode om de acties van de vijand te beheren.
        if self.action_cooldown == 0:  # Als de cooldown voor acties is verlopen:
            action = self.get_action()  # Kies een nieuwe actie.
            # Initialiseer de acties.
            match action:
                case "attack":  # Als de actie "aanvallen" is:
                    self.getPath(self.target)  # Bereken het pad naar het doelwit.
                    self.current_action_length = 4  # Stel de duur van de actie in.
                case "idle":  # Als de actie "stilstaan" is:
                    self.current_action_length = 2  # Stel de duur van de actie in.
                case "protect":  # Als de actie "beschermen" is:
                    self.current_action_length = 1.5  # Stel de duur van de actie in.
                case "runaway":  # Als de actie "wegrennen" is:
                    furthest = None  # Zoek het verste waypoint.
                    for i in self.ai.waypoints:  # Itereer door alle waypoints.
                        if not furthest or i.pos.distance_to(self.target.pos) > furthest.pos.distance_to(self.target.pos):  # Zoek het waypoint dat het verst van het doelwit is.
                            furthest = i
                    if furthest:  # Als er een waypoint is gevonden:
                        self.getPath(furthest)  # Bereken het pad naar dat waypoint.
                    self.current_action_length = 3  # Stel de duur van de actie in.
                case "shoot":  # Als de actie "schieten" is:
                    self.current_action_length = 2  # Stel de duur van de actie in.
                    self.shoot(self.target.pos)  # Laat de vijand schieten.
                case "powerup":  # Als de actie "power-up pakken" is:
                    closest = None  # Zoek de dichtstbijzijnde power-up.
                    for i in self.game.powerups:  # Itereer door alle power-ups.
                        if not closest or i.pos.distance_to(self.pos) < closest.pos.distance_to(self.pos):  # Zoek de dichtstbijzijnde power-up.
                            closest = i
                    if closest:  # Als er een power-up is gevonden:
                        self.getPath(closest)  # Bereken het pad naar de power-up.
                    self.current_action_length = 10  # Stel de duur van de actie in.

            self.last_action_time = time.time()  # Update de tijd van de laatste actie.
            self.current_action = action  # Sla de huidige actie op.

        action = self.current_action  # Haal de huidige actie op.
        self.protecting = False  # Zet beschermen uit.
        # Werk de acties bij.
        match action:
            case "attack":  # Als de actie "aanvallen" is:
                if len(self.path) < 1:  # Als er geen pad meer is:
                    self.getPath(self.target)  # Bereken een nieuw pad naar het doelwit.
                self.movement()  # Voer de bewegingslogica uit.
                if self.collideswith(self.target):  # Controleer of de vijand het doelwit raakt.
                    self.punch()  # Voer een stoot uit.
                    self.current_action_length = 0  # Stel de actieduur in op 0.
            case "idle":  # Als de actie "stilstaan" is:
                self.smoothSpeedChange(0)  # Stop de beweging.
            case "protect":  # Als de actie "beschermen" is:
                self.protecting = True  # Zet beschermen aan.
                self.smoothSpeedChange(0)  # Stop de beweging.
            case "runaway":  # Als de actie "wegrennen" is:
                self.movement()  # Voer de bewegingslogica uit.
            case "shoot":  # Als de actie "schieten" is:
                self.smoothSpeedChange(0)  # Stop de beweging.
            case "powerup":  # Als de actie "power-up pakken" is:
                self.movement()  # Voer de bewegingslogica uit.

    def get_action(self):  # Kies een nieuwe actie voor de vijand.
        distance_from_target = self.pos.distance_to(self.target.pos)  # Bereken de afstand tot het doelwit.

        diff = self.target.health - self.health  # Bereken het verschil in gezondheid tussen de vijand en het doelwit.

        # Bereken de gezondheidsverschillen.
        if diff < 0:
            player_health_diff = -diff  # Gezondheidsverschil van de speler.
            health_diff = 0  # Gezondheidsverschil van de vijand.
        else:
            health_diff = diff  # Gezondheidsverschil van de vijand.
            player_health_diff = 0  # Gezondheidsverschil van de speler.

        powerup_spawned = [i for i in self.game.objects if isinstance(i, PowerUp)] != []  # Controleer of er power-ups zijn gespawnd.

        powerup_weight = powerup_spawned * health_diff  # Bereken het gewicht van de power-up actie.

        if distance_from_target < 300:  # Als de vijand dichtbij het doelwit is:
            attack_weight = self.ready_to_punch * 30 + player_health_diff * 2  # Gewicht voor aanvallen.
            runaway_weight = (not self.ready_to_punch) * 2 * health_diff  # Gewicht voor wegrennen.
            protect_weight = (not self.ready_to_punch) * 10 + health_diff  # Gewicht voor beschermen.
            return random.choices(["attack", "idle", "protect", "runaway"], weights=[attack_weight, 5, protect_weight, runaway_weight]).pop()  # Kies een actie.
        elif 300 < distance_from_target < 800:  # Als de vijand op middellange afstand is:
            attack_weight = self.ready_to_punch * 20 + player_health_diff * 2  # Gewicht voor aanvallen.
            runaway_weight = (not (self.ready_to_punch or self.ready_to_shoot)) * health_diff  # Gewicht voor wegrennen.
            protect_weight = (not (self.ready_to_punch or self.ready_to_shoot)) * 5 + health_diff  # Gewicht voor beschermen.
            shoot_weight = self.ready_to_shoot * 10 + health_diff  # Gewicht voor schieten.
            return random.choices(["attack", "idle", "protect", "runaway", "shoot", "powerup"], weights=[attack_weight, 5, protect_weight, runaway_weight, shoot_weight, powerup_weight]).pop()  # Kies een actie.
        else:  # Als de vijand ver weg is:
            attack_weight = self.ready_to_punch * 1  # Gewicht voor aanvallen.
            shoot_weight = self.ready_to_shoot * 20 + health_diff  # Gewicht voor schieten.
            return random.choices(["attack", "idle", "shoot", "powerup"], weights=[attack_weight, 10, shoot_weight, powerup_weight]).pop()  # Kies een actie.

    def update(self):  # Update de status van de vijand.
        super().update()  # Roep de update-methode van de ouderklasse aan.
        if self.game.debugging == True:  # Als debugging is ingeschakeld:
            for point in self.ai.waypoints:  # Itereer door alle waypoints.
                point.update()  # Werk de waypoints bij (teken ze op het scherm).
            self.show_path()  # Toon het pad tussen de waypoints.
        self.actionHandler()  # Beslis welke actie de vijand uitvoert.