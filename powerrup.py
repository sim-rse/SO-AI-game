# -*- coding: utf-8 -*-
"""
Created on Mon May  5 20:16:06 2025

@author: ferha
"""

import pygame
import random
import time

# Klasse voor de PowerUp
class PowerUp():
    def __init__(self, x, y, effect, image):
        self.x = x                             # x-positie waar power-up uit de lucht valt
        self.y = y                             # y-positie begint bovenaan
        self.effect = effect                   # Wat voor effect de power-up heeft ("shrink", "heal", "strength")
        self.image = image                     # Afbeelding van de power-up
        self.rect = self.image.get_rect(topleft=(self.x, self.y))  # Maak een rechthoek voor botsingen
        self.vel_y = 0                          # Snelheid van de val (verticaal)
        self.on_ground = False                  # Flag of de power-up de grond heeft bereikt
        self.collider = True                    # Kan botsten met de speler
        self.spawn_time = time.time()            # Tijd wanneer de power-up gespawned is (voor automatische verwijdering)

    def update(self, game):
        """Update wordt elke frame uitgevoerd. De power-up valt en botst tegen de speler."""
        
        # Als de power-up nog niet op de grond is
        if not self.on_ground:
            self.vel_y += game.gravity           # Pas zwaartekracht toe
            self.y += self.vel_y                 # Verhoog y-positie (laat hem vallen)
            self.rect.y = self.y                 # Update de rechthoek (voor botsingen)

            # Als de power-up de onderkant van het scherm raakt
            if self.y >= game.screen_height - self.rect.height:
                self.y = game.screen_height - self.rect.height  # Zet hem exact op de grond
                self.rect.y = self.y
                self.on_ground = True            # Markeer dat hij op de grond ligt

        # Kijk of een speler de power-up aanraakt
        for speler in game.players:
            if self.rect.colliderect(speler.rect):    # Als de speler de power-up aanraakt
                self.apply(speler)                    # Pas het effect toe op de speler
                game.remove(self)                     # Verwijder de power-up uit de game na gebruik
                return
        
        # Verwijder de power-up automatisch na 10 seconden (indien hij niet opgepakt is)
        if time.time() - self.spawn_time > 10:
            game.remove(self)                          # Verwijder de power-up automatisch

    def apply(self, speler):
        """Pas het effect van de power-up toe op de speler."""
        
        if self.effect == "shrink":                      # Als het effect "shrink" is (kleiner maken)
            speler.width *= 0.5                          # Verklein de breedte van de speler
            speler.height *= 0.5                         # Verklein de hoogte van de speler
            speler.rect.width = speler.width             # Update de rechthoek van de speler
            speler.rect.height = speler.height

        elif self.effect == "heal":                      # Als het effect "heal" is (genezen)
            if hasattr(speler, "max_health"):            # Als de speler een max_health heeft
                speler.health = min(speler.max_health, speler.health + 25)  # Voeg 25 health toe, zonder de max te overschrijden
            else:
                speler.health += 25                      # Anders, verhoog de gezondheid met 25

        elif self.effect == "strength":                  # Als het effect "strength" is (kracht)
            if not hasattr(speler, "strength"):          # Als de speler geen kracht heeft
                speler.strength = 10                     # Geef de speler een startwaarde van 10
            speler.strength *= 1.5                       # Verhoog de kracht van de speler met 50%

# Functie om een willekeurige power-up te spawnen
def spawn_random_powerup(game):
    """Functie om een willekeurige power-up te laten vallen uit de lucht."""
    
    keuzes = ["shrink", "heal", "strength"]              # Mogelijke effecten voor de power-up
    soort = random.choice(keuzes)                        # Kies willekeurig één effect

    afbeeldingen = {                                     # Koppel elk effect aan een sprite-afbeelding
        "shrink": pygame.image.load("image/power_shrink.png").convert_alpha(),
        "heal": pygame.image.load("image/power_heal.png").convert_alpha(),
        "strength": pygame.image.load("image/power_strength.png").convert_alpha()
    }

    afbeelding = afbeeldingen[soort]                     # Kies de juiste afbeelding op basis van het effect
    x = random.randint(100, game.screen_width - 100)      # Kies een willekeurige x-positie op het scherm
    y = 0                                                 # Laat de power-up bovenaan het scherm vallen

    powerup = PowerUp(x, y, soort, afbeelding)            # Maak een nieuw power-up object
    game.add(powerup)                                     # Voeg de power-up toe aan de game