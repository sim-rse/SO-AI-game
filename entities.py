import pygame, math, time  # Voor het maken van de game, inclusief graphics, animaties en input. Voor wiskundige berekeningen en tijdsbeheer.
from objects import Object, MovingObject  # Voor het maken van objecten in de gamewereld.
from queue import PriorityQueue  # Voor het beheren van een lijst met doelen (bijvoorbeeld vijanden).
from AI import AI, Waypoint  # Voor kunstmatige intelligentie en padvinden.


class Entity(MovingObject):  # Basisklasse voor alle bewegende objecten in de game.
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20, center=None):
        super().__init__(game, x, y, width, height, image, hasCollisionEnabled=True, affected_by_gravity=True, animationfile=animationfile, scale=scale, center=center)  # Roept de constructor van de ouderklasse aan.
        self.health = health  # Gezondheid van het object.
        self.strength = 2  # Hoeveel schade het object kan toebrengen.
        self.target = None  # Het doelwit van het object.
        self.list_of_targets = PriorityQueue()  # Een prioriteitenlijst met doelen.
        self.collider = False  # Geeft aan of het object botsingen kan detecteren.
        self.invincible = False  # Geeft aan of het object onkwetsbaar is.
        self.jump_force = 16  # Hoe hoog het object kan springen.
        self.walkSpeed = 10  # Hoe snel het object kan lopen.

    def die(self):  # Methode die wordt aangeroepen wanneer het object sterft.
        self.playanimation("die")  # Speelt de sterfanimatie af.

    def jump(self):  # Laat het object springen.
        if self.onGround:  # Controleert of het object op de grond staat.
            self.vel.y = -self.jump_force  # Stelt de verticale snelheid in om te springen.

    def getDamage(self, damage):  # Vermindert de gezondheid van het object.
        if not self.invincible:  # Controleert of het object niet onkwetsbaar is.
            self.health -= damage  # Vermindert de gezondheid.
        self.playanimation("get_damaged")  # Speelt de animatie voor schade af.

    def punch(self, otherEntity=None):  # Laat het object een andere entiteit slaan.
        self.playanimation("punch")  # Speelt de animatie voor slaan af.
        if otherEntity:  # Controleert of er een doelwit is.
            otherEntity.getDamage(self.strength)  # Brengt schade toe aan het doelwit.

    def shoot(self, target):  # Laat het object een projectiel schieten.
        self.game.add(
            Projectile(
                self.game,
                self.center.x,
                self.center.y - self.height,
                target=target,
                owner=self,
                exploding=True,
                image="images/fireball.png"  # Afbeelding van het projectiel.
            )
        )

    def update(self):  # Methode die elke frame wordt aangeroepen.
        super().update()  # Roept de update-methode van de ouderklasse aan.
        if self.health <= 0:  # Controleert of de gezondheid 0 of lager is.
            self.die()  # Laat het object sterven.

    @property
    def jumpheight(self):  # Berekent de maximale spronghoogte.
        return self.jump_force**2 / (2 * self.game.gravity)

    @property
    def jumpwidth(self):  # Berekent de maximale sprongafstand.
        return self.walkSpeed * (2 * self.jump_force / self.game.gravity)


class Projectile(Entity):  # Klasse voor projectielen zoals vuurballen.
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1, health=20, target=None, owner=None, exploding=False):
        if isinstance(image, str):  # Controleert of de afbeelding een pad is.
            loaded_image = pygame.image.load(image).convert_alpha()  # Laadt de afbeelding.
        else:
            loaded_image = image  # Als het al een pygame.Surface is.

        super().__init__(game, x, y, width, height, loaded_image, animationfile, scale, health)  # Roept de constructor van de ouderklasse aan.

        self.explosionrange = 5  # Bereik van de explosie.
        self.flyspeed = 2  # Snelheid van het projectiel.
        self.exploding = exploding  # Geeft aan of het projectiel explodeert.
        self.owner = owner  # De eigenaar van het projectiel.
        self.target = target or pygame.math.Vector2(0, 0)  # Doelwit van het projectiel.
        self.direction = (self.target - self.pos).normalize()  # Richting waarin het projectiel beweegt.
        self.affected_by_gravity = 0  # Het projectiel wordt niet beïnvloed door zwaartekracht.
        self.collider = False  # Botsingen zijn uitgeschakeld.
        self.collisionsEnabled = False  # Botsingen zijn uitgeschakeld.
        self.vel.x = self.direction.x * self.flyspeed  # Horizontale snelheid.
        self.vel.y = self.direction.y * self.flyspeed  # Verticale snelheid.

    def die(self):  # Methode die wordt aangeroepen wanneer het projectiel sterft.
        super().die()  # Roept de die-methode van de ouderklasse aan.
        self.game.remove(self)  # Verwijdert het projectiel uit de game.
        if self.exploding:  # Controleert of het projectiel explodeert.
            self.game.add(Explosion(self.game, self.pos.x, self.pos.y, explosionrange=self.explosionrange, center=self.center))  # Creëert een explosie.

    def update(self):  # Methode die elke frame wordt aangeroepen.
        self.updatePos()  # Werkt de positie van het projectiel bij.
        for col in self.game.colliders:  # Itereert door alle botsbare objecten.
            if col == self.owner:  # Controleert of het botsende object de eigenaar is.
                pass  # Doet niets als het de eigenaar is.
            else:
                if self.collideswith(col):  # Controleert op botsing.
                    if not self.exploding and isinstance(col, Entity):  # Controleert of het projectiel niet explodeert en het botsende object een entiteit is.
                        col.getDamage(self.strength)  # Brengt schade toe aan het botsende object.
                    self.die()  # Laat het projectiel sterven.
        self.blit()  # Tekent het projectiel op het scherm.


class Explosion(Entity):  # Klasse die een explosie vertegenwoordigt.
    def __init__(self, game, x, y, scale=1, center=None, explosionrange=100, strength=30):
        super().__init__(game, x, y, scale=scale, animationfile="animations/explosion.json", center=center)  # Roept de constructor van de ouderklasse aan.
        self.playanimation("explosion")  # Speelt de explosie-animatie af.
        self.static = True  # Maakt de explosie statisch.
        self.explosionrange = explosionrange  # Bereik van de explosie.
        self.strength = strength  # Kracht van de explosie.
        self.collisionsEnabled = False  # Botsingen zijn uitgeschakeld.
        self.affected_by_gravity = False  # De explosie wordt niet beïnvloed door zwaartekracht.

        for ent in self.game.entities:  # Itereert door alle entiteiten in de game.
            if ent.collideswith(self, range_=self.explosionrange):  # Controleert of een entiteit binnen het bereik van de explosie valt.
                ent.getDamage(self.strength)  # Brengt schade toe aan de entiteit.
                knockback_direction = pygame.math.Vector2(ent.center.x - self.center.x, ent.center.y - self.center.y)  # Berekent de knockback-richting.
                if not knockback_direction.xy == [0, 0]:  # Controleert of de vector niet nul is.
                    knockback_direction.normalize_ip()  # Normaliseert de vector.
                ent.vel = knockback_direction * self.strength * 2  # Past knockback toe op de entiteit.

    def update(self):  # Methode die elke frame wordt aangeroepen.
        super().update()  # Roept de update-methode van de ouderklasse aan.
        if self.animations.current.name == "default":  # Controleert of de explosie-animatie is afgelopen.
            self.die()  # Verwijdert de explosie.

    def getDamage(self, damage):  # Explosies kunnen geen schade oplopen.
        pass

    def die(self):  # Methode die wordt aangeroepen wanneer de explosie sterft.
        self.game.remove(self)  # Verwijdert de explosie uit de game.


class Player(Entity):  # De Player-klasse erft van de Entity-klasse.
    def __init__(self, game, x, y, width=0, height=0, image="placeholder.png", animationfile=None, scale=1):
        super().__init__(game, x, y, width, height, image, animationfile, scale)  # Roept de constructor van de Entity-klasse aan.
        self.walkSpeed = 10  # De snelheid waarmee de speler kan lopen.
        self.shoot_key_hold = False  # Houdt bij of de schietknop wordt ingedrukt.
        self.sneaking = False  # Boolean die aangeeft of de speler aan het sluipen is.
        self.health = 50  # De hoeveelheid gezondheidspunten van de speler.

    def shoot(self, target):  # Methode om een projectiel af te vuren.
        self.game.add(
            Projectile(
                self.game,  # Verwijzing naar het spelobject.
                self.center.x,  # De x-coördinaat van het midden van de speler.
                self.center.y - self.height,  # De y-coördinaat net boven de speler.
                target=target,  # Het doelwit van het projectiel.
                owner=self,  # De speler is de eigenaar van het projectiel.
                exploding=True,  # Geeft aan dat het projectiel explodeert bij impact.
                image="images/fireball.png"  # De afbeelding van het projectiel.
            )
        )

    def getKeyPress(self):  # Methode om toetsenbordinvoer te verwerken.
        keys = pygame.key.get_pressed()  # Haalt de huidige status van alle toetsen op.
        accel = [0, 0]  # Versnelling van de speler (x, y).
        if keys[pygame.K_RIGHT]:  # Als de rechterpijltoets wordt ingedrukt:
            accel[0] += self.walkSpeed  # Verhoog de snelheid naar rechts.
            self.flipSprite = False  # Zorg ervoor dat de sprite niet gespiegeld is.
        if keys[pygame.K_LEFT]:  # Als de linkerpijltoets wordt ingedrukt:
            accel[0] += -self.walkSpeed  # Verhoog de snelheid naar links.
            self.flipSprite = True  # Spiegel de sprite.
        if keys[pygame.K_UP]:  # Als de omhoogpijltoets wordt ingedrukt:
            self.jump()  # Laat de speler springen.
        if keys[pygame.K_DOWN]:  # Als de omlaagpijltoets wordt ingedrukt:
            self.sneaking = True  # Zet de sluipmodus aan.
        else:
            self.sneaking = False  # Zet de sluipmodus uit.
        if keys[pygame.K_SPACE]:  # Als de spatiebalk wordt ingedrukt:
            self.punch()  # Laat de speler slaan.
        self.smoothSpeedChange(accel[0])  # Pas de snelheid van de speler soepel aan.

        if keys[pygame.K_z]:  # Als de Z-toets wordt ingedrukt:
            if not self.shoot_key_hold:  # Controleer of de schietknop niet al wordt vastgehouden.
                self.shoot_key_hold = True  # Zet de schietknop op vastgehouden.
                if self.target:  # Als er een doelwit is:
                    target_position = self.target.pos  # Gebruik de positie van het doelwit.
                elif self.flipSprite:  # Als de speler naar links kijkt:
                    target_position = pygame.math.Vector2(self.pos.x - 1, self.pos.y)  # Schiet naar links.
                else:  # Als de speler naar rechts kijkt:
                    target_position = pygame.math.Vector2(self.pos.x + self.width + 1, self.pos.y)  # Schiet naar rechts.

                self.shoot(target_position)  # Vuur een projectiel af naar de doelpositie.
        else:
            self.shoot_key_hold = False  # Zet de schietknop op niet vastgehouden.

    def animationHandler(self):  # Methode om de animaties van de speler te beheren.
        if self.sneaking:  # Als de speler aan het sluipen is:
            self.playanimation("sneak")  # Speel de sluipanimatie af.
        elif self.vel.y < 0:  # Als de speler omhoog beweegt (springt):
            self.playanimation("jump")  # Speel de springanimatie af.
        elif self.onGround and self.vel.x != 0:  # Als de speler op de grond loopt:
            self.playanimation("walk")  # Speel de loopanimatie af.
        elif self.vel.y > 0:  # Als de speler naar beneden beweegt (valt):
            self.playanimation("fall")  # Speel de valanimatie af.
        else:  # Als geen van bovenstaande acties plaatsvindt:
            self.playanimation("default")  # Speel de standaardanimatie af.

    def die(self):  # Methode die wordt aangeroepen wanneer de speler sterft.
        super().die()  # Roept de die-methode van de ouderklasse aan.
        print('Oh noo (sad mario music)')  # Print een bericht in de console.
        self.game.scene = "game_over"  # Zet de spelscène op "game_over".
        self.game.scene_running = False  # Stop de huidige scène.

    def update(self):  # Methode die elke frame wordt aangeroepen.
        self.getKeyPress()  # Verwerk de toetsenbordinvoer.
        super().update()  # Roept de update-methode van de ouderklasse aan.