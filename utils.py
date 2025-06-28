import time
import pygame


def checkDict(dict_to_check,key_to_find, value_if_not_found):
    if key_to_find in dict_to_check:
        return dict_to_check[key_to_find]
    else:
        return value_if_not_found
    
class SelectionList: #Een lijst waar je doorheen kan bladeren.
    def __init__(self):
        self.list = [] # De eigenlijke lijst van objecten.
        self.current_pos = 0

    def append(self,obj):# Voeg een item toe aan de lijst.
        self.list.append(obj)

    def remove(self,obj):# verwijder een item uit de lijst.
        self.list.remove(obj)

    def go_next(self): # Ga naar het volgende item in de lijst.
        self.current = (self.current+1)% self.length #% self.length zorgt ervoor dat het terug naar 0 gaat als het einde bereikt is.

    def go_previous(self): # Ga naar het vorige item in de lijst.
        self.current = (self.current-1)% self.length

    @property
    def length(self): # Geeft het aantal items in de lijst terug.
        return len(self.list)

    @property
    def next(self): # Geeft de index van het volgende item.
        return (self.current+1)% self.length
    
    @property
    def previous(self): # Geeft de index van het vorige item.
        return (self.current-1)% self.length
    
    @property
    def current(self): #Geeft de index van het huidige item.
        return self.list[self.current_pos]
    
    @current.setter 
    def current(self, value: str): #Zet de huidige positie op basis van een item.
        if value in self.list: # Alleen als het item bestaat.
            self.current_pos = self.list.index(value)

class pathShower: # Een klasse om een pad te tonen op het scherm.
    def __init__(self,game, path:list):
        self.path = path # Sla het pad op (lijst van punten)
        self.game = game # Sla het spelobject op (voor toegang tot het scherm).

    def update(self):# Teken het pad op het scherm.
        pygame.draw.lines(self.game.screen, (0,255,0), False, [point.pos for point in self.path])         # Tekent groene lijnen tussen de punten in het pad.
