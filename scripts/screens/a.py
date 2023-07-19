import pygame
import pygame_gui

pygame.init()

# Screen settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300
background_color = pygame.Color('grey')

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Theme dictionary for transparent button
transparent_button_theme = {
    "button": {
        "normal_bg": "images/transparent_bg.png",  # A transparent background image
        "hover_bg": "images/transparent_bg.png",
        "down_bg": "images/transparent_bg.png",
        "text_color": "#000000",
        "font": pygame.font.Font(None, 24),
        "border_width": 0,
        "shadow_width": 0,
    }
}

# UI Manager with theme
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), theme_path=transparent_button_theme)

# Create a transparent button
button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((150, 100), (100, 50)),
                                      text='Transparent',
                                      manager=manager)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        manager.process_events(event)

    manager.update(1/60.0)

    screen.fill(background_color)
    manager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()
