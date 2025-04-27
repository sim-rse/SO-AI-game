# -*- coding: utf-8 -*-
"""
Created on Sat Apr 26 23:55:10 2025

@author: ferha
"""
class healthbar(object):
    def __init__(self, behouder, width=None, height = 10, color = (255,0,0),border_color = (0,0,0), offset_y = 15): #behouder is de object zelf waarvoor we de balk doen, offset_y = hoeveel pixels we het boven de behouder willen 
# als width=None dan neemt de level van het leven de balk gwn over 
    self.behouder = behouder
    self.max_health = behouder.health  #opslaan max health om verhouding te berekenen
    self.offset_y = offset_y  # afstand boven het personage
    
    #breedte standaard
    if width is None: 
        width = behouder.width
    
    #de balk maken maar healthbar is ook een objecht(kindje van object) dus we roepen super 
    #ook color= color laten want anders voert de object classe zijn eigen standaardkleur uit 
    super().__init__(behouder.X, behouder.Y - offset_y, width, height, color=color) 
    self.bordor_color = border_color
    
    
    
