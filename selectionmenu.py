# -*- coding: utf-8 -*-
"""
Created on Fri May  2 13:44:17 2025

@author: ferha
"""
import pygame  # Laad de pygame module 
clock = pygame.time.Clock()  # Clock object om FPS te regelen

def selection_menu(game):
    screen = game.screen  # Haal het schermobject van de game op
    game.scene_running = True  # Zet deze scene actief
    game.empty()  # Verwijder alle objecten van vorige scenes

    # kleuren en fonts instellen
    bg_color = (200, 200, 200)  # Achtergrondkleur van het menu
    font = pygame.font.SysFont("monospace", 30)  # Gewone tekst
    title_font = pygame.font.SysFont("monospace", 40, bold=True)  # Titeltekst
    small_font = pygame.font.SysFont("monospace", 20)  # Voor beschrijving

    # Lijst van personages en hun beschrijvingen
    characters = ["K. Onami", "Iron Stan"]  # Voorbeeld namen van personages
    character_descriptions = [
        "Wijze ninja die alle regels en codes kent...",  # Beschrijving voor naruto
        "Grootse fan van iron man"  # Beschrijving voor iron man
    ]

    selected_char = 0  # Index van gekozen personage
    selected_ar = game.arena_index  # Begin met de huidige achtergrond
    menu_index = 0  # Index van geselecteerde menukeuze (0=personage, 1=achtergrond, 2=start)

    backgrounds = [
        pygame.image.load("images/projectimage1.jpg").convert(),
        pygame.image.load("images/projectimage2.jpg").convert(),
        pygame.image.load("images/projectimage3.jpg").convert()
        ]

    # Zolang deze scene draait en game nog actief is
    while game.scene_running and game.running:
        clock.tick(game.fps)  # Beperk tot max FPS
        screen.fill(bg_color)  # Maak scherm leeg met achtergrondkleur

        # Verwerk gebruikersinput
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:  # Sluitknop van venster
                    game.running = False  # Stop de hele game
                case pygame.KEYDOWN:  # Een toets is ingedrukt
                    if event.key == pygame.K_UP:  # Pijltje omlaag
                        menu_index = (menu_index - 1) % 3  # Ga naar vorige optie
                    elif event.key == pygame.K_DOWN:  # Pijltje omhoog
                        menu_index = (menu_index + 1) % 3  # Ga naar volgende optie
                    elif event.key == pygame.K_LEFT:  # Pijltje links
                        if menu_index == 0:  # Personage wijzigen
                            selected_char = (selected_char - 1) % len(characters)
                        elif menu_index == 1:  # Achtergrond wijzigen
                            selected_ar = (selected_ar - 1) % len(game.arenas)
                    elif event.key == pygame.K_RIGHT:  # Pijltje rechts
                        if menu_index == 0:  # Personage wijzigen
                            selected_char = (selected_char + 1) % len(characters)
                        elif menu_index == 1:  # Achtergrond wijzigen
                            selected_ar = (selected_ar + 1) % len(game.arenas)
                    elif event.key == pygame.K_RETURN:  # Enter-toets
                        if menu_index == 2:  # Start Game geselecteerd
                            game.player_character = characters[selected_char]  # Bewaar gekozen karakter
                            game.arena_index = selected_ar  # Bewaar gekozen achtergrondindex
                            game.arena = game.arenas[selected_ar]  # Stel huidige achtergrond in
                            game.scene = "default"  # Zet volgende scene naar de game
                            game.scene_running = False  # Sluit dit menu

        # Teken de titel
        titel = title_font.render("Main Menu", True, (0, 0, 0))  # Tekstobject
        screen.blit(titel, (game.screen.get_width()/2-titel.get_width()/2, 40))  # Zet tekst op scherm

        # --------- Optie 1: Kies Personage ---------
        kleur1 = (255, 0, 0) if menu_index == 0 else (0, 0, 0)  # Rood als geselecteerd
        choice_title_1 = font.render(f"Kies jouw personnage", True, (0,0,0))
        screen.blit(choice_title_1, (game.screen.get_width()*0.1, 230))  # Zet tekst op scherm
        char_txt = font.render(f"Personage: {characters[selected_char]}", True, kleur1)  # Naam
        screen.blit(char_txt, (game.screen.get_width()/2-char_txt.get_width()/2, 290))  # Zet tekst op scherm
        desc = small_font.render(character_descriptions[selected_char], True, kleur1)  # Beschrijving
        screen.blit(desc, (game.screen.get_width()/2-char_txt.get_width()/2, 340))  # Zet beschrijving op scherm

        # --------- Optie 2: Kies Achtergrond ---------
        kleur2 = (255, 0, 0) if menu_index == 1 else (0, 0, 0)  # Rood als geselecteerd
        choice_title_2 = font.render(f"Kies het arena:", True, (0,0,0))
        screen.blit(choice_title_2, (game.screen.get_width()*0.1, 400))  # Zet tekst op scherm
        bg_txt = font.render(f"Arena: {selected_ar + 1}", True, kleur2)  # Achtergrond nummer
        screen.blit(bg_txt, (game.screen.get_width()/2-char_txt.get_width()/2, 460))  # Zet tekst op scherm
        preview = pygame.transform.scale(backgrounds[selected_ar], (300, 170))  # Maak voorbeeld kleiner
        screen.blit(preview, (game.screen.get_width()/2-char_txt.get_width()/2, 500))  # Teken achtergrondvoorbeeld

        # --------- Optie 3: Start Game ---------
        kleur3 = (255, 0, 0) if menu_index == 2 else (0, 0, 0)  # Rood als geselecteerd
        start_txt = font.render("START GAME", True, kleur3)  # Starttekst
        screen.blit(start_txt, (game.screen.get_width()/2 - start_txt.get_width()/2, 750))  # Zet op scherm

        pygame.display.flip()  # Update het scherm