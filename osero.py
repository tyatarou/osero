# -*- coding: utf-8 -*-

import pygame
import sys
import random
import time

# 定数
BOARD_SIZE = 8
TILE_SIZE = 60
WINDOW_WIDTH = BOARD_SIZE * TILE_SIZE
WINDOW_HEIGHT = BOARD_SIZE * TILE_SIZE + 100
BLACK = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
LIGHT_PINK = (255, 182, 193)
GRAY = (160, 160, 160)

# 初期化
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("オセロゲーム：人間 vs AI")
font = pygame.font.SysFont(None, 30)
large_font = pygame.font.SysFont(None, 50)

# ゲーム状態
game_state = "start"  # start, playing, game_over
show_valid_moves = True  # トグルボタン状態

# ボード初期化関数
def init_board():
    board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    board[3][3] = board[4][4] = 2  # 白
    board[3][4] = board[4][3] = 1  # 黒
    return board

board = init_board()
current_player = 1  # 黒が先手
AI_PLAYER = 2

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),         (0, 1),
              (1, -1), (1, 0), (1, 1)]

def is_valid_move(x, y, player):
    if board[y][x] != 0:
        return False
    opponent = 3 - player
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        found_opponent = False
        while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            if board[ny][nx] == opponent:
                found_opponent = True
            elif board[ny][nx] == player:
                if found_opponent:
                    return True
                break
            else:
                break
            nx += dx
            ny += dy
    return False

def get_valid_moves(player):
    return [(x, y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if is_valid_move(x, y, player)]

def blink_stone(x, y, color):
    for _ in range(3):
        draw_board(get_valid_moves(3 - color))
        pygame.display.flip()
        pygame.time.wait(300)
        pygame.draw.circle(screen, GREEN, (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 2 - 5)
        pygame.display.flip()
        pygame.time.wait(300)

def make_move(x, y, player):
    board[y][x] = player
    draw_board(get_valid_moves(3 - player))
    pygame.display.flip()
    blink_stone(x, y, player)
    opponent = 3 - player
    for dx, dy in DIRECTIONS:
        tiles_to_flip = []
        nx, ny = x + dx, y + dy
        while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            if board[ny][nx] == opponent:
                tiles_to_flip.append((nx, ny))
            elif board[ny][nx] == player:
                for fx, fy in tiles_to_flip:
                    board[fy][fx] = player
                break
            else:
                break
            nx += dx
            ny += dy
    draw_board(get_valid_moves(3 - player))
    pygame.display.flip()

def has_valid_moves(player):
    return len(get_valid_moves(player)) > 0

def count_discs():
    black = sum(row.count(1) for row in board)
    white = sum(row.count(2) for row in board)
    return black, white

def draw_board(valid_moves):
    screen.fill(GREEN)
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if board[y][x] == 1:
                pygame.draw.circle(screen, BLACK, rect.center, TILE_SIZE // 2 - 5)
            elif board[y][x] == 2:
                pygame.draw.circle(screen, WHITE, rect.center, TILE_SIZE // 2 - 5)

    if show_valid_moves:
        for x, y in valid_moves:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(screen, LIGHT_PINK, (cx, cy), TILE_SIZE // 2 - 10, 3)

    black_count, white_count = count_discs()
    score_text = f"Black: {black_count}   White: {white_count}"
    text_surface = font.render(score_text, True, WHITE)
    screen.blit(text_surface, (10, WINDOW_HEIGHT - 90))

    # トグルボタン
    pygame.draw.rect(screen, GRAY, (WINDOW_WIDTH - 160, WINDOW_HEIGHT - 90, 150, 30))
    toggle_text = "手を表示: ON" if show_valid_moves else "手を表示: OFF"
    toggle_surface = font.render(toggle_text, True, BLACK)
    screen.blit(toggle_surface, (WINDOW_WIDTH - 150, WINDOW_HEIGHT - 85))

def display_winner():
    black_count, white_count = count_discs()
    if black_count > white_count:
        winner_text = "Black won"
    elif white_count > black_count:
        winner_text = "White won"
    else:
        winner_text = "引き分け！"
    result_surface = large_font.render(winner_text, True, WHITE)
    screen.blit(result_surface, (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT - 60))

def draw_start_screen():
    screen.fill(GREEN)
    title = large_font.render("オセロゲーム", True, WHITE)
    start_msg = font.render("クリックして開始", True, WHITE)
    screen.blit(title, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50))
    screen.blit(start_msg, (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 + 10))

def draw_replay_button():
    pygame.draw.rect(screen, GRAY, (WINDOW_WIDTH//2 - 60, WINDOW_HEIGHT - 40, 120, 30))
    text = font.render("リプレイ", True, BLACK)
    screen.blit(text, (WINDOW_WIDTH//2 - 30, WINDOW_HEIGHT - 35))

def ai_move():
    moves = get_valid_moves(AI_PLAYER)
    if moves:
        move = random.choice(moves)
        make_move(*move, AI_PLAYER)
        return True
    return False

# メインループ
running = True
game_over = False
while running:
    if game_state == "start":
        draw_start_screen()
    elif game_state == "playing":
        valid_moves = get_valid_moves(current_player)
        draw_board(valid_moves)
        if game_over:
            display_winner()
            draw_replay_button()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if game_state == "start":
                board = init_board()
                current_player = 1
                game_over = False
                game_state = "playing"

            elif game_state == "playing" and not game_over:
                if WINDOW_WIDTH - 160 <= mx <= WINDOW_WIDTH - 10 and WINDOW_HEIGHT - 90 <= my <= WINDOW_HEIGHT - 60:
                    show_valid_moves = not show_valid_moves

                elif current_player != AI_PLAYER:
                    x, y = mx // TILE_SIZE, my // TILE_SIZE
                    if (x, y) in get_valid_moves(current_player):
                        make_move(x, y, current_player)
                        if has_valid_moves(AI_PLAYER):
                            current_player = AI_PLAYER
                        elif not has_valid_moves(current_player):
                            game_over = True

            elif game_over:
                if WINDOW_WIDTH//2 - 60 <= mx <= WINDOW_WIDTH//2 + 60 and WINDOW_HEIGHT - 40 <= my <= WINDOW_HEIGHT - 10:
                    board = init_board()
                    current_player = 1
                    game_over = False
                    game_state = "playing"

    if game_state == "playing" and current_player == AI_PLAYER and not game_over:
        pygame.time.wait(500)
        if ai_move():
            if has_valid_moves(1):
                current_player = 1
            elif not has_valid_moves(AI_PLAYER):
                game_over = True
        if game_over:
            draw_board([])
            display_winner()
            draw_replay_button()
            pygame.display.flip()

pygame.quit()
sys.exit()
