import pygame
import os

# Inicializa o Pygame
pygame.init()

# Configurações da Tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokémon Battle")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Carregar Imagens
try:
    BACKGROUND = pygame.image.load(os.path.join("D:\\PI-III\\assets", "background.png"))
    print("Background image loaded successfully.")
except pygame.error as e:
    print(f"Failed to load background image: {e}")
    BACKGROUND = None

try:
    HP_BAR = pygame.image.load(os.path.join("D:\\PI-III\\assets", "hp_bar.png"))
    print("HP bar image loaded successfully.")
except pygame.error as e:
    print(f"Failed to load HP bar image: {e}")
    HP_BAR = None

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

def draw_pokemon(pokemon, x, y):
    if pokemon.sprite:
        screen.blit(pokemon.sprite, (x, y))
    else:
        print(f"Failed to load sprite for {pokemon.name}")

def draw_hp_bar(pokemon, x, y):
    if HP_BAR:
        screen.blit(HP_BAR, (x, y))
        hp_ratio = pokemon.current_hp / pokemon.hp
        pygame.draw.rect(screen, RED, (x + 30, y + 10, 200, 20))
        pygame.draw.rect(screen, GREEN, (x + 30, y + 10, 200 * hp_ratio, 20))
    else:
        print("HP bar image not loaded, skipping HP bar drawing.")

def battle(pokemon1, pokemon2):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    running = True
    while running:
        print("Entering main loop...")  # Adicionado para depuração

        # Preenche a tela com branco
        screen.fill(WHITE)

        # Desenha o fundo
        if BACKGROUND:
            screen.blit(BACKGROUND, (0, 0))
        else:
            print("No background image, skipping drawing.")

        # Desenha os Pokémon e suas barras de HP
        draw_pokemon(pokemon1, 100, 250)
        draw_pokemon(pokemon2, 500, 50)

        draw_hp_bar(pokemon1, 50, 400)
        draw_hp_bar(pokemon2, 450, 50)

        draw_text(f"{pokemon1.name}", font, BLACK, screen, 50, 370)
        draw_text(f"{pokemon2.name}", font, BLACK, screen, 450, 20)

        # Lida com eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Atualiza a tela
        pygame.display.flip()

        # Controla a taxa de frames
        clock.tick(30)

    pygame.quit()
