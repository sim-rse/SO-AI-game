# -*- coding: utf-8 -*-
"""
Created on Mon May  5 20:16:06 2025

@author: ferha
"""   
import pygame           # Hiermee kun je games maken
import random           # Voor willekeurige keuzes (bijv. positie)
import time             # Om tijd bij te houden
from objects import MovingObject

# Klasse voor de PowerUp
class PowerUp(MovingObject):
    def __init__(self, game, x, y, effect, image = None, animation=None):
        super().__init__(game, x,y, image = image, animationfile=animation, scale=0.5)   # x-positie op het scherm , y-positie op het scherm (begint bovenaan)
        self.effect = effect                         # Wat voor effect de power-up geeft ("shrink", "heal", "strength")
        self.vel_y = 0                               # Snelheid waarmee hij naar beneden valt
        self.on_ground = False                       # Of de power-up op de grond ligt
        self.collider = False                        # Of de power-up kan speler met de botsen 
        self.collisionsEnabled = True                # Of de powerup botst met de omgeving
        self.spawn_time = time.time()                # Tijd waarop de power-up gemaakt is

    def update(self):
        game = self.game
        super().update()
        """Elke frame wordt deze functie uitgevoerd om de power-up te updaten"""

        # Kijk of hij een speler raakt
        for speler in game.fighters:
            if self.collides_with(speler):                    # Als ze botsen
                self.apply(speler)                            # Geef het effect aan de speler
                game.remove(self)                             # Verwijder de power-up
                return

        # Verwijder de power-up automatisch na 10 seconden
        if time.time() - self.spawn_time > 10:
            game.remove(self)                             # Verwijder hem na 10 seconden

    def collides_with(self, other):
        """Check of twee objecten botsen (eenvoudige vierkante botsing)"""
        return (
            self.pos.x < other.pos.x + other.width and            # Linkerkant van power-up raakt rechterkant speler
            self.pos.x + self.width > other.pos.x and             # Rechterkant van power-up raakt linkerkant speler
            self.pos.y < other.pos.y + other.height and           # Bovenkant van power-up raakt onderkant speler
            self.pos.y + self.height > other.pos.y                # Onderkant van power-up raakt bovenkant speler
        )
    def apply(self):
        pass

class Shrink(PowerUp):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, "shrink", "images\\powerups\\shrink.png")

    def apply(self, speler):
        """Geef het effect van de power-up aan de speler"""
        if self.effect == "shrink":                       # Als het effect "kleiner maken" is
            return
            speler.width *= 0.5                           # Halveer de breedte
            speler.height *= 0.5                          # Halveer de hoogte

class Heal(PowerUp):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, "heal", "images\\powerups\\health.png")

    def apply(self, speler):
        if hasattr(speler, "max_health"):             # Als de speler een maximale gezondheid heeft
            speler.health = min(speler.max_health, speler.health + 25)  # Voeg 25 toe, maar niet boven max
        else:
            speler.health += 25                       # Anders, verhoog gewoon met 25

class Strength(PowerUp):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, "strength", animation = "animations\\powerups\\sterker.json")

    def apply(self, speler):
            if not hasattr(speler, "strength"):           # Als de speler nog geen kracht-waarde heeft
                speler.strength = 10                      # Begin bij 10
            speler.strength *= 1.5                        # Verhoog kracht met 50%



# Functie om willekeurig een power-up te laten vallen
def spawn_random_powerup(game):
    keuzes = [Shrink, Heal, Strength]                     # Mogelijke soorten power-ups
    soort = random.choice(keuzes)                         # Kies er willekeurig één uit

    
    x = random.randint(100, game.screen_width - 100)      # Kies een willekeurige plek op het scherm
    y = 0                                                 # Begin bovenaan

    powerup = soort(game, x, y)            # Maak een power-up object
    game.add(powerup)                                     # Voeg het toe aan het spel