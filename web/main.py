import pygame
import random
import asyncio

# --- 游戏配置 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300  # 游戏区域宽度 (10个方块)
PLAY_HEIGHT = 600 # 游戏区域高度 (20个方块)
BLOCK_SIZE = 30

TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 20 # 稍微往下移动一点，给标题留空间

# --- 方块形状定义 (与之前相同) ---
S = [['.....', '.....', '..o..', '.oo..', '.....'],
     ['.....', '..o..', '..oo.', '...o.', '.....']]
Z = [['.....', '.....', '.oo..', '..o..', '.....'],
     ['.....', '..o..', '.oo..', '.o...', '.....']]
I = [['..o..', '..o..', '..o..', '..o..', '.....'],
     ['.....', 'oooo.', '.....', '.....', '.....']]
O = [['.....', '.....', '.oo..', '.oo..', '.....']]
J = [['.....', '.o...', '.ooo.', '.....', '.....'],
     ['.....', '..o..', '..o..', '.oo..', '.....'],
     ['.....', '.....', '.ooo.', '...o.', '.....'],
     ['.....', '..oo.', '..o..', '..o..', '.....']]
L = [['.....', '...o.', '.ooo.', '.....', '.....'],
     ['.....', '.oo..', '..o..', '..o..', '.....'],
     ['.....', '.....', '.ooo.', '.o...', '.....'],
     ['.....', '..o..', '..o..', '.oo..', '.....']]
T = [['.....', '..o..', '.ooo.', '.....', '.....'],
     ['.....', '..o..', '.oo..', '..o..', '.....'],
     ['.....', '.....', '.ooo.', '..o..', '.....'],
     ['.....', '..o..', '..oo.', '..o..', '.....']]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

# --- 类和核心函数 (大部分与之前相同) ---
class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions:
                c = locked_positions[(x, y)]
                grid[y][x] = c
    return grid

def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == 'o':
                positions.append((piece.x + j, piece.y + i))
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
    return positions

def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(piece)
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('sans-serif', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() / 2))

def draw_grid_lines(surface):
    for i in range(21):
        pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE), (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE))
    for j in range(11):
         pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))


def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                new_key = (x, y + inc)
                locked[new_key] = locked.pop(key)
    return inc

def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('sans-serif', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT / 2 - 100
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == 'o':
                pygame.draw.rect(surface, piece.color, (sx + j * BLOCK_SIZE, sy + i * BLOCK_SIZE - 20, BLOCK_SIZE, BLOCK_SIZE), 0)
    surface.blit(label, (sx + 10, sy - 50))


def draw_main_window(surface, grid, score=0, fall_speed_setting=0.27):
    surface.fill((0, 0, 0))
    font = pygame.font.SysFont('sans-serif', 60, bold=True)
    label = font.render('TETRIS', 1, (255, 255, 255))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 30))

    # 显示分数
    font = pygame.font.SysFont('sans-serif', 30)
    label = font.render('Score: ' + str(score), 1, (255,255,255))
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + 50
    surface.blit(label, (sx, sy))

    # 显示速度
    # 0.27s是1x速度，越小越快
    speed_display = f"{(0.27 / fall_speed_setting):.1f}x"
    label = font.render('Speed: ' + speed_display, 1, (255,255,255))
    sx = TOP_LEFT_X - 220
    sy = TOP_LEFT_Y + 50
    surface.blit(label, (sx, sy))
    
    # 绘制游戏区域的方块
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    
    # 绘制游戏区域边框和网格线
    pygame.draw.rect(surface, (255, 0, 0), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 5)
    draw_grid_lines(surface)


# --- 新的主游戏循环 ---
async def main():
    """
    主函数，使用状态机管理游戏流程
    """
    pygame.init()
    pygame.font.init()
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')

    # 游戏状态
    class GameState:
        MENU = 1
        PLAYING = 2
        GAME_OVER = 3

    # --- 游戏变量 ---
    # 菜单设置
    fall_speed_setting = 0.27 # 值越小，速度越快
    
    # 游戏内变量
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    score = 0
    
    game_state = GameState.MENU
    running = True

    while running:
        # --- 菜单界面 ---
        if game_state == GameState.MENU:
            win.fill((0,0,0))
            draw_text_middle(win, 'Press Any Key To Play', 60, (255,255,255))
            
            font = pygame.font.SysFont('sans-serif', 30)
            speed_display = f"{(0.27 / fall_speed_setting):.1f}x"
            label = font.render(f'Initial Speed: {speed_display} (UP/DOWN keys to change)', 1, (255, 255, 255))
            win.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 420))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        fall_speed_setting = max(0.12, fall_speed_setting - 0.05) # 设置最快速度
                    elif event.key == pygame.K_DOWN:
                        fall_speed_setting = min(0.8, fall_speed_setting + 0.05) # 设置最慢速度
                    else:
                        # 重置游戏变量，开始新游戏
                        locked_positions = {}
                        grid = create_grid(locked_positions)
                        current_piece = get_shape()
                        next_piece = get_shape()
                        score = 0
                        fall_time = 0
                        game_state = GameState.PLAYING
        
        # --- 游戏进行中 ---
        elif game_state == GameState.PLAYING:
            grid = create_grid(locked_positions)
            
            # 自动下落逻辑
            fall_time += clock.get_rawtime()
            if fall_time / 1000 >= fall_speed_setting:
                fall_time = 0
                current_piece.y += 1
                if not valid_space(current_piece, grid) and current_piece.y > 0:
                    current_piece.y -= 1
                    change_piece = True
            
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                    elif event.key == pygame.K_UP:
                        current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                        if not valid_space(current_piece, grid):
                           current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
            
            # 绘制当前下落的方块
            shape_pos = convert_shape_format(current_piece)
            for i in range(len(shape_pos)):
                x, y = shape_pos[i]
                if y > -1:
                    grid[y][x] = current_piece.color

            # 方块落地，锁定并生成新方块
            if change_piece:
                for pos in shape_pos:
                    locked_positions[(pos[0], pos[1])] = current_piece.color
                current_piece = next_piece
                next_piece = get_shape()
                change_piece = False
                score += clear_rows(grid, locked_positions) * 10
            
            # 绘制所有内容
            draw_main_window(win, grid, score, fall_speed_setting)
            draw_next_shape(next_piece, win)
            
            # 检查是否输了
            if check_lost(locked_positions):
                game_state = GameState.GAME_OVER

        # --- 游戏结束界面 ---
        elif game_state == GameState.GAME_OVER:
            draw_text_middle(win, "GAME OVER", 80, (255, 255, 255))
            font = pygame.font.SysFont('sans-serif', 30)
            label = font.render('Press any key to return to menu', 1, (255,255,255))
            win.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 420))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    game_state = GameState.MENU

        # 更新显示
        pygame.display.update()
        clock.tick()
        
        # 这是让`pygbag`正常工作的关键
        await asyncio.sleep(0)
    
    pygame.quit()

# --- 程序入口 ---
if __name__ == "__main__":
    asyncio.run(main())