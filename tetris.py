import pygame
import sys
from tetromino import Tetromino

successes, failures = pygame.init()
print("Initializing pygame: {0} successes & {1} failures".format(successes, failures))

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREY = (127, 127, 127)

SCREEN_HEIGHT = 700
SCREEN_WIDTH = 800

PLAY_HEIGHT = 600
PLAY_WIDTH = 300
BLOCK_SIZE = 30

TOP_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_Y = SCREEN_HEIGHT - PLAY_HEIGHT

FPS = 25
GAME_TITLE = "Tetris"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)

clock = pygame.time.Clock()


class TetrisGame(object):
    def __init__(self, row, column):
        self.row_count = row
        self.col_count = column
        self.grid = [[0 for _ in range(self.col_count)] for _ in range(self.row_count)]
        self.cur_tetromino = Tetromino(4, 0)
        self.next_tetromino = Tetromino(4, 0)
        self.start = 1
        self.score = 0

    def draw_mesh(self, _screen):
        for x in range(self.row_count):
            for y in range(self.col_count):
                pygame.draw.rect(
                    _screen, GREY, [TOP_X + (y * BLOCK_SIZE), TOP_Y + (x * BLOCK_SIZE), BLOCK_SIZE, BLOCK_SIZE], 1
                )
        pygame.draw.rect(_screen, RED, [TOP_X, TOP_Y, PLAY_WIDTH, PLAY_HEIGHT], 1)

    def draw_text(self, _screen):
        sys_font = pygame.font.SysFont("", 55, True, False)
        font = pygame.font.SysFont("", 30, True, False)

        tetris = sys_font.render("Tetris", True, WHITE)
        score = font.render("Score: " + str(self.score), True, WHITE)

        game_over = font.render("Game Over", True, WHITE)
        press_esc = font.render("Press ESC", True, WHITE)

        _screen.blit(tetris, [(SCREEN_WIDTH - tetris.get_width())/2, 0])
        _screen.blit(score, [(3 * SCREEN_WIDTH + PLAY_WIDTH)/4 - BLOCK_SIZE, 0])
        if not self.start:
            _screen.blit(game_over, [(SCREEN_WIDTH - game_over.get_width())//2, SCREEN_HEIGHT//2])
            _screen.blit(press_esc, [(SCREEN_WIDTH - press_esc.get_width())//2, SCREEN_HEIGHT//2 + 65])

    def draw_tetromino(self, _screen):
        # Falling Pieces
        for x in range(self.cur_tetromino.size):
            for y in range(self.cur_tetromino.size):
                if self.cur_tetromino.get_tetromino()[x][y] == 1:
                    pygame.draw.rect(_screen, self.cur_tetromino.color,
                                     [TOP_X + (y + self.cur_tetromino.row_pos) * BLOCK_SIZE + 1,
                                      TOP_Y + (x + self.cur_tetromino.col_pos) * BLOCK_SIZE + 1, BLOCK_SIZE - 2,
                                      BLOCK_SIZE - 2])

        # Fallen Pieces
        for x in range(self.row_count):
            for y in range(self.col_count):
                if self.grid[x][y] != 0:
                    pygame.draw.rect(_screen, self.grid[x][y], [TOP_X + y * BLOCK_SIZE + 1, TOP_Y + x * BLOCK_SIZE + 1,
                                                                BLOCK_SIZE - 2, BLOCK_SIZE - 2])

        # Next Piece
        font = pygame.font.SysFont('', 30)
        text_next_shape = font.render('Next Shape', True, WHITE)

        x_pos = (3 * SCREEN_WIDTH + PLAY_WIDTH)/4 - BLOCK_SIZE
        y_pos = SCREEN_HEIGHT//2
        for x in range(self.next_tetromino.size):
            for y in range(self.next_tetromino.size):
                if self.next_tetromino.get_tetromino()[x][y] == 1:
                    pygame.draw.rect(_screen, self.next_tetromino.color,
                                     [x_pos + y * BLOCK_SIZE, y_pos + x * BLOCK_SIZE, BLOCK_SIZE - 2, BLOCK_SIZE - 2])
        _screen.blit(text_next_shape, (x_pos - BLOCK_SIZE, y_pos - BLOCK_SIZE))

    def detect_collision(self):
        detect_collision = False
        for x in range(self.cur_tetromino.size):
            for y in range(self.cur_tetromino.size):
                if self.cur_tetromino.get_tetromino()[x][y] == 1:
                    if x + self.cur_tetromino.col_pos > self.row_count - 1 or \
                            y + self.cur_tetromino.row_pos > self.col_count - 1 or \
                            y + self.cur_tetromino.row_pos < 0 or \
                            self.grid[x + self.cur_tetromino.col_pos][y + self.cur_tetromino.row_pos] != 0:
                        detect_collision = True
        return detect_collision

    def touch_down(self):
        for x in range(self.cur_tetromino.size):
            for y in range(self.cur_tetromino.size):
                if self.cur_tetromino.get_tetromino()[x][y] == 1:
                    self.grid[x + self.cur_tetromino.col_pos][y + self.cur_tetromino.row_pos] = self.cur_tetromino.color
        self.clear_rows()
        self.cur_tetromino = self.next_tetromino
        self.next_tetromino = Tetromino(4, 0)
        if self.detect_collision():
            self.start = 0

    def clear_rows(self):
        rows = 0
        for x in range(self.row_count):
            empty_col = 0
            for y in range(self.col_count):
                if self.grid[x][y] == 0:
                    empty_col += 1
            if empty_col == 0:
                rows += 1
                for _x in range(x, 1, -1):
                    for _y in range(self.col_count):
                        self.grid[_x][_y] = self.grid[_x-1][_y]
        self.score += rows ** 2

    def move_right(self):
        self.cur_tetromino.row_pos += 1
        if self.detect_collision():
            self.cur_tetromino.row_pos -= 1

    def move_left(self):
        self.cur_tetromino.row_pos -= 1
        if self.detect_collision():
            self.cur_tetromino.row_pos += 1

    def up(self):
        old_rotation = self.cur_tetromino.rotation
        self.cur_tetromino.rotate()
        if self.detect_collision():
            self.cur_tetromino.rotation = old_rotation

    def move_down(self):
        self.cur_tetromino.col_pos += 1
        if self.detect_collision():
            self.cur_tetromino.col_pos -= 1
            self.touch_down()


T = TetrisGame(20, 10)

counter = 0
running = True
while running:
    counter += 1
    if counter > 100000:
        counter = 0

    if counter % (FPS // 2) == 0:
        if T.start:
            T.move_down()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                T = TetrisGame(20, 10)
                counter = 0
            elif event.key == pygame.K_w or event.key == pygame.K_UP:
                T.up()
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                T.move_left()
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                T.move_right()

    keys = pygame.key.get_pressed()
    if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and T.start:
        T.move_down()

    screen.fill(BLACK)

    T.draw_mesh(screen)
    T.draw_tetromino(screen)
    T.draw_text(screen)

    pygame.display.flip()
    clock.tick(FPS)
