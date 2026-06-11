import pygame
import random
import sys

# Настройки игры (поле 30х30, панель управления сверху)
GRID_SIZE = 30
CELL_SIZE = 25
MINE_COUNT = 120
WIDTH = GRID_SIZE * CELL_SIZE
PANEL_HEIGHT = 50
HEIGHT = (GRID_SIZE * CELL_SIZE) + PANEL_HEIGHT

# Цвета
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: (0, 0, 0),
    8: (128, 128, 128)
}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Сапер 30x30 с кнопкой сброса")
font = pygame.font.SysFont(None, 24)

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0

    def draw(self, surface):
        # Сдвигаем отрисовку ячеек вниз на высоту панели
        rect = pygame.Rect(self.x * CELL_SIZE, (self.y * CELL_SIZE) + PANEL_HEIGHT, CELL_SIZE, CELL_SIZE)
        if not self.is_revealed:
            pygame.draw.rect(surface, GRAY, rect)
            if self.is_flagged:
                pygame.draw.line(surface, RED, rect.topleft, rect.bottomright, 3)
                pygame.draw.line(surface, RED, rect.topright, rect.bottomleft, 3)
        else:
            pygame.draw.rect(surface, DARK_GRAY, rect)
            if self.is_mine:
                pygame.draw.circle(surface, BLACK, rect.center, CELL_SIZE // 3)
            elif self.neighbor_mines > 0:
                text = font.render(str(self.neighbor_mines), True, COLORS.get(self.neighbor_mines, BLACK))
                surface.blit(text, text.get_rect(center=rect.center))
        
        pygame.draw.rect(surface, WHITE, rect, 1)

def create_grid():
    grid = [[Cell(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
    
    mines_placed = 0
    while mines_placed < MINE_COUNT:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if not grid[x][y].is_mine:
            grid[x][y].is_mine = True
            mines_placed += 1
            
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if not grid[x][y].is_mine:
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[nx][ny].is_mine:
                            count += 1
                grid[x][y].neighbor_mines = count
    return grid

def reveal_cell(grid, x, y):
    cell = grid[x][y]
    if cell.is_revealed or cell.is_flagged:
        return
    cell.is_revealed = True
    
    if cell.is_mine:
        return

    if cell.neighbor_mines == 0:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    reveal_cell(grid, nx, ny)

def check_win(grid):
    for row in grid:
        for cell in row:
            if not cell.is_mine and not cell.is_revealed:
                return False
    return True

def draw_top_panel(surface):
    # Рисуем фон панели
    panel_rect = pygame.Rect(0, 0, WIDTH, PANEL_HEIGHT)
    pygame.draw.rect(surface, DARK_GRAY, panel_rect)
    
    # Кнопка Restart
    button_width = 120
    button_height = 30
    button_x = (WIDTH // 2) - (button_width // 2)
    button_y = (PANEL_HEIGHT // 2) - (button_height // 2)
    
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(surface, GREEN, button_rect)
    pygame.draw.rect(surface, WHITE, button_rect, 2)
    
    text_surf = font.render("RESTART", True, WHITE)
    surface.blit(text_surf, text_surf.get_rect(center=button_rect.center))
    
    # Разделительная линия
    pygame.draw.line(surface, WHITE, (0, PANEL_HEIGHT), (WIDTH, PANEL_HEIGHT), 2)

def main():
    grid = create_grid()
    clock = pygame.time.Clock()
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                # Клик по верхней панели (кнопка RESTART)
                if mouse_y < PANEL_HEIGHT:
                    button_width = 120
                    button_x = (WIDTH // 2) - (button_width // 2)
                    button_y = (PANEL_HEIGHT // 2) - (15)
                    
                    if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + 30:
                        grid = create_grid()
                        game_over = False
                
                # Клик по игровому полю
                elif not game_over:
                    x = mouse_x // CELL_SIZE
                    y = (mouse_y - PANEL_HEIGHT) // CELL_SIZE
                    
                    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                        if event.button == 1:  # Левая кнопка мыши
                            if not grid[x][y].is_flagged:
                                reveal_cell(grid, x, y)
                                if grid[x][y].is_mine:
                                    game_over = True
                                    for row in grid:
                                        for cell in row:
                                            if cell.is_mine:
                                                cell.is_revealed = True
                                elif check_win(grid):
                                    game_over = True
                                    
                        elif event.button == 3:  # Правая кнопка мыши
                            if not grid[x][y].is_revealed:
                                grid[x][y].is_flagged = not grid[x][y].is_flagged

        screen.fill(WHITE)
        draw_top_panel(screen)
        
        for row in grid:
            for cell in row:
                cell.draw(screen)
                
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
