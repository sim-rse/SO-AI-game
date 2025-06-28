# -*- coding: utf-8 -*-
"""
Created on Fri May  9 14:32:48 2025

@author: ferha
"""

import pygame
clock = pygame.time.Clock()
# Voeg deze code toe aan je bestaande game-bestand
def game_over(game):
    """
    Functie voor het tonen van het 'Game Over' scherm.
    Toont de winnaar of een gelijkspel.
    """
    screen = game.screen
    screen.fill((0, 0, 0))  # Achtergrond zwart
    font = pygame.font.SysFont("monospace", 50)
    smallfont = pygame.font.SysFont("monospace", 30)

    players = game.players
    
    winner = f"{game.winner} wins!"

    title = font.render("Game Over", True, (255, 0, 0))  # Rode "Game Over"
    winner_text = smallfont.render(winner, True, (255, 255, 255))  # Witte winnaarstekst
    back_text = smallfont.render("Press ENTER to return to menu", True, (200, 200, 200))  # Tekst om terug naar menu te gaan

    # Teken alles op het scherm
    screen.blit(title, (screen.get_width()/2 - title.get_width()/2, screen.get_height()*0.3))
    screen.blit(winner_text, (screen.get_width()/2 - winner_text.get_width()/2, screen.get_height()*0.45))
    screen.blit(back_text, (screen.get_width()/2 - back_text.get_width()/2, screen.get_height()*0.6))

    pygame.display.flip()

    # Loop om het Game Over scherm te tonen en te wachten op gebruikersinput
    while game.running and game.scene_running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    game.running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_RETURN:  # Druk op Enter om terug naar menu te gaan
                            game.scene = "start_menu"
                            game.scene_running = False
        clock.tick(game.fps)