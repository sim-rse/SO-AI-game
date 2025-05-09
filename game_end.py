# -*- coding: utf-8 -*-
"""
Created on Fri May  9 14:32:48 2025

@author: ferha
"""

import pygame

# Voeg deze code toe aan je bestaande game-bestand
def game_over(game: Game):
    """
    Functie voor het tonen van het 'Game Over' scherm.
    Toont de winnaar of een gelijkspel.
    """
    screen = game.screen
    screen.fill((0, 0, 0))  # Achtergrond zwart
    font = pygame.font.SysFont("monospace", 50)
    smallfont = pygame.font.SysFont("monospace", 30)

    players = game.players
    # Controleer wie de winnaar is of dat het een gelijkspel is
    if len(players) < 2:
        winner = "Unknown"
    else:
        if players[0].health <= 0:
            winner = "Player 2 Wins!"
        elif players[1].health <= 0:
            winner = "Player 1 Wins!"
        else:   
            winner = "Draw"

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
        game.clock.tick(game.fps)

# Voeg deze code toe aan je game loop of gevecht loop om de health te controleren en de game over scene te starten

def gameLoop(game: Game):
    """
    De hoofdgame loop voor de gevechten.
    Controleert spelers en start game over wanneer een speler geen health meer heeft.
    """
    # Game logica zoals beweging, aanvallen, enz.
    # Bijvoorbeeld:
    for player in game.players:
        player.update()  # Je update misschien je spelers hier

    # Controleer of een speler geen health meer heeft en start Game Over
    for player in game.players:
        if player.health <= 0:
            game.scene = "game_over"
            game.scene_running = False
            break  # Stop de loop zodra iemand verloren heeft

    # De rest van de game loop
    # Tekenen, animaties, enz.
    game.clock.tick(game.fps)

