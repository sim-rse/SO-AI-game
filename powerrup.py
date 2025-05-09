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
    def __init__(self, game, x, y, effect, image):
        super().__init__(game, x,y, image = image)   # x-positie op het scherm , y-positie op het scherm (begint bovenaan)
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

        """# Als hij nog niet op de grond ligt
        if not self.on_ground:
            self.vel_y += game.gravity               # Voeg zwaartekracht toe aan de valsnelheid
            self.pos.y += self.vel_y                     # Beweeg hem naar beneden

            # Als hij de onderkant van het scherm raakt
            if self.pos.y >= game.screen_height - self.height:
                self.pos.y = game.screen_height - self.height  # Zet hem netjes op de grond
                self.on_ground = True                      # Geef aan dat hij op de grond ligt"""

        # Kijk of hij een speler raakt
        for speler in game.players:
            if self.collider and self.collides_with(speler):  # Als ze botsen
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

    def apply(self, speler):
        """Geef het effect van de power-up aan de speler"""
        if self.effect == "shrink":                       # Als het effect "kleiner maken" is
            speler.width *= 0.5                           # Halveer de breedte
            speler.height *= 0.5                          # Halveer de hoogte

        elif self.effect == "heal":                       # Als het effect "genezen" is
            if hasattr(speler, "max_health"):             # Als de speler een maximale gezondheid heeft
                speler.health = min(speler.max_health, speler.health + 25)  # Voeg 25 toe, maar niet boven max
            else:
                speler.health += 25                       # Anders, verhoog gewoon met 25

        elif self.effect == "strength":                   # Als het effect "kracht" is
            if not hasattr(speler, "strength"):           # Als de speler nog geen kracht-waarde heeft
                speler.strength = 10                      # Begin bij 10
            speler.strength *= 1.5                        # Verhoog kracht met 50%

# Functie om willekeurig een power-up te laten vallen
def spawn_random_powerup(game):
    keuzes = ["shrink", "heal", "strength"]               # Mogelijke soorten power-ups
    soort = random.choice(keuzes)                         # Kies er willekeurig één uit

    afbeeldingen = {                                      # Koppel elke soort aan een plaatje
        "shrink": "images\\powerups\\shrink.gif"
        #"heal": "images\\powerrups\\health.gif",
        #"strength": "images\\powerrups\\sterker.gif"
    }

    afbeelding = afbeeldingen["shrink"]                      # Kies het juiste plaatje
    x = random.randint(100, game.screen_width - 100)      # Kies een willekeurige plek op het scherm
    y = 0                                                 # Begin bovenaan

    powerup = PowerUp(game, x, y, soort, afbeelding)            # Maak een power-up object
    game.add(powerup)                                     # Voeg het toe aan het spel