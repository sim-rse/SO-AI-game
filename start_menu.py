# -*- coding: utf-8 -*-
"""
Created on Fri May  2 13:44:17 2025

@author: ferha
"""
import pygame  # Laad de pygame module
clock = pygame.time.Clock()  # Clock object om FPS te regelen

def start_menu(game):
    screen = game.screen  # Haal het schermobject van de game op
    game.scene_running = True  # Zet deze scene actief
    game.empty()  # Verwijder alle objecten van vorige scenes

    # kleuren en fonts instellen
    bg_color = (100, 255, 255)  # Achtergrondkleur van het menu
    font = pygame.font.SysFont("monospace", 30)  # Gewone tekst
    title_font = pygame.font.SysFont("monospace", 40, bold=True)  # Titeltekst
    small_font = pygame.font.SysFont("monospace", 20)  # Voor beschrijving

    # Lijst van personages en hun beschrijvingen
    characters = ["naruto", "Iron man"]  # Voorbeeld namen van personages
    character_descriptions = [
        "nog te doen",  # Beschrijving voor KungFuKat
        "repulsor, schouderraket, supersonic charge en system reboot"  # Beschrijving voor RoboRik
    ]

    selected_char = 0  # Index van gekozen personage
    selected_bg = game.background_index  # Begin met de huidige achtergrond
    menu_index = 0  # Index van geselecteerde menukeuze (0=personage, 1=achtergrond, 2=start)

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
                    if event.key == pygame.K_DOWN:  # Pijltje omlaag
                        menu_index = (menu_index - 1) % 3  # Ga naar vorige optie
                    elif event.key == pygame.K_UP:  # Pijltje omhoog
                        menu_index = (menu_index + 1) % 3  # Ga naar volgende optie
                    elif event.key == pygame.K_LEFT:  # Pijltje links
                        if menu_index == 0:  # Personage wijzigen
                            selected_char = (selected_char - 1) % len(characters)
                        elif menu_index == 1:  # Achtergrond wijzigen
                            selected_bg = (selected_bg - 1) % len(game.backgrounds)
                    elif event.key == pygame.K_RIGHT:  # Pijltje rechts
                        if menu_index == 0:  # Personage wijzigen
                            selected_char = (selected_char + 1) % len(characters)
                        elif menu_index == 1:  # Achtergrond wijzigen
                            selected_bg = (selected_bg + 1) % len(game.backgrounds)
                    elif event.key == pygame.K_RETURN:  # Enter-toets
                        if menu_index == 2:  # Start Game geselecteerd
                            game.player_character = characters[selected_char]  # Bewaar gekozen karakter
                            game.background_index = selected_bg  # Bewaar gekozen achtergrondindex
                            game.background = game.backgrounds[selected_bg]  # Stel huidige achtergrond in
                            game.scene = "default"  # Zet volgende scene naar de game
                            game.scene_running = False  # Sluit dit menu

        # Teken de titel
        titel = title_font.render("Main Menu", True, (0, 0, 0))  # Tekstobject
        screen.blit(titel, (100, 40))  # Zet tekst op scherm

        # --------- Optie 1: Kies Personage ---------
        kleur1 = (255, 0, 0) if menu_index == 0 else (0, 0, 0)  # Rood als geselecteerd
        char_txt = font.render(f"Personage: {characters[selected_char]}", True, kleur1)  # Naam
        screen.blit(char_txt, (100, 120))  # Zet tekst op scherm
        desc = small_font.render(character_descriptions[selected_char], True, kleur1)  # Beschrijving
        screen.blit(desc, (120, 160))  # Zet beschrijving op scherm

        # --------- Optie 2: Kies Achtergrond ---------
        kleur2 = (255, 0, 0) if menu_index == 1 else (0, 0, 0)  # Rood als geselecteerd
        bg_txt = font.render(f"Achtergrond: {selected_bg + 1}", True, kleur2)  # Achtergrond nummer
        screen.blit(bg_txt, (100, 220))  # Zet tekst op scherm
        preview = pygame.transform.scale(game.backgrounds[selected_bg], (300, 170))  # Maak voorbeeld kleiner
        screen.blit(preview, (100, 260))  # Teken achtergrondvoorbeeld

        # --------- Optie 3: Start Game ---------
        kleur3 = (255, 0, 0) if menu_index == 2 else (0, 0, 0)  # Rood als geselecteerd
        start_txt = font.render("START GAME", True, kleur3)  # Starttekst
        screen.blit(start_txt, (100, 450))  # Zet op scherm

        pygame.display.flip()  # Update het scherm