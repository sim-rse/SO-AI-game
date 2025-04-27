# -*- coding: utf-8 -*-
"""
Created on Sat Apr 26 23:55:10 2025

@author: ferha
"""
import pygame
class healthbar(object):
    def __init__(self, behouder, width=None, height=10, color=(255,0,0), border_color=(0,0,0), offset_y=15):
        # behouder is het object waarvoor we de healthbar maken
        # width is de breedte, als None wordt het de breedte van het object zelf
        # height is de hoogte van de healthbar
        # color is de kleur van de healthbar
        # border_color is de kleur van de rand rond de healthbar
        # offset_y is de hoogte boven het object (personage)

        self.behouder = behouder  # Het object waarvoor de healthbar wordt getoond
        self.max_health = behouder.health  # Max health van de behouder (om verhouding te berekenen)
        self.offset_y = offset_y  # Hoeveel pixels de healthbar boven de behouder moet zitten

        # Als width niet is gegeven, gebruiken we de breedte van het object zelf
        if width is None:
            width = behouder.width

        self.width = width  # Breedte van de healthbar
        self.height = height  # Hoogte van de healthbar
        self.color = color  # Kleur van de healthbar
        self.border_color = border_color  # Kleur van de rand rondom de healthbar
        
        # Positie van de healthbar is hetzelfde als het object, maar met een offset boven het object
        self.X = behouder.X
        self.Y = behouder.Y - self.offset_y

    def update(self):
        # Deze functie past de grootte van de healthbar aan op basis van de huidige health
        health_ratio = self.behouder.health / self.max_health  # Verhouding van health

        # Update de breedte van de healthbar op basis van de verhouding van health
        self.width = self.max_health * health_ratio

        # Zorg ervoor dat de healthbar blijft volgen met het object
        self.X = self.behouder.X
        self.Y = self.behouder.Y - self.offset_y

    def draw(self, scherm):
        # Eerst de rand tekenen
        pygame.draw.rect(scherm, self.border_color, (self.X - 1, self.Y - 1, self.max_health + 2, self.height + 2))
        
        # Dan de echte healthbar tekenen
        pygame.draw.rect(scherm, self.color, (self.X, self.Y, self.width, self.height))